
import  torch as th
import  torch.nn as nn
import  torch.nn.functional as F
import dgl
# from torchsummary import summary
# from feature_extractor import Deep_fingerprinting as Extractor
from dgl.nn.pytorch import GraphConv,GATConv,SortPooling,SAGEConv,AvgPooling
# GCN, GCDNN, GAT, GraphSAGE

class GCN_Classifier(nn.Module):
    def __init__(self, classes, num_layers, dim_input, dim_hidden, drop_out ):
        super(GCN_Classifier, self).__init__()

        self.classes = classes
        self.num_layers = num_layers
        self.dim_input = dim_input
        self.dim_hidden = dim_hidden
        self.drop_out = nn.Dropout(drop_out)
        self.logsoftmax = nn.LogSoftmax(dim=1)
        self.softmax = nn.Softmax(dim=1)

        self.layers = nn.ModuleList()
        self.layers.append(GraphConv(in_feats=self.dim_input,out_feats=self.dim_hidden)) #first layer
        for i in range(1, self.num_layers):
            self.layers.append(GraphConv(in_feats=self.dim_hidden,out_feats=self.dim_hidden))

        self.classify = nn.Linear(self.dim_hidden,self.classes)

    def forward(self, graph, feat):

        for i,layer in enumerate(self.layers):
            feat = F.relu(layer(graph,feat))
            if i != self.num_layers - 1:
                feat = self.drop_out(feat)

        graph.ndata['fet'] = feat
        hg = dgl.mean_nodes(graph,'fet')

        hg = self.classify(hg) # logits

        with graph.local_scope():
            # return self.logsoftmax(hg)
            return hg

# 2-layers GAT
class GAT_Classifier(nn.Module):
    def __init__(self, classes, num_layers, dim_input,dim_hidden,num_heads,drop_out):
        super(GAT_Classifier, self).__init__()

        self.classes = classes
        self.num_layers = num_layers
        self.dim_input = dim_input
        self.dim_hidden = dim_hidden
        self.num_heads = num_heads

        self.tmp = self.dim_hidden * self.num_heads

        self.layers = nn.ModuleList()
        self.layers.append(GATConv(self.dim_input, self.dim_hidden, self.num_heads)) #first layer
        for i in range(1, self.num_layers):
            self.layers.append(GATConv(self.tmp, self.dim_hidden, self.num_heads))

        self.classify = nn.Linear(self.tmp, self.classes)
        self.meanpooling = AvgPooling()
        self.drop_out = nn.Dropout(drop_out)
        self.logsoftmax = nn.LogSoftmax(dim=1)


    def forward(self, graph, feat):
        for i, layer in enumerate(self.layers):
            feat = F.relu(layer(graph,feat)).flatten(1)
            if i != self.num_layers - 1:
                feat = self.drop_out(feat)

        graph.ndata['fet'] = feat
        hg = dgl.mean_nodes(graph,'fet') # shape: bsz, head_num*hidden_dim

        hg = self.classify(hg)

        with graph.local_scope():
            return self.logsoftmax(hg)


class SAGE_Classifier(nn.Module):
    def __init__(self, classes,dim_input,dim_hidden,num_layers,drop_out):
        super(SAGE_Classifier, self).__init__()

        self.classes = classes
        self.num_layers = num_layers
        self.dim_input = dim_input
        self.dim_hidden = dim_hidden
        self.drop_out = nn.Dropout(drop_out)
        self.logsoftmax = nn.LogSoftmax(dim=1)

        self.layers = nn.ModuleList()
        self.layers.append(SAGEConv(self.dim_input, self.dim_hidden, aggregator_type='mean'))
        for i in range(1, self.num_layers):
            self.layers.append(SAGEConv(self.dim_hidden, self.dim_hidden, aggregator_type='mean'))

        self.classify = nn.Linear(self.dim_hidden, self.classes)
        self.logsoftmax = nn.LogSoftmax(dim=1)

    def forward(self, graph, feat):

        for i, layer in enumerate(self.layers):
            feat = F.relu(layer(graph,feat))
            if i != self.num_layers - 1:
                feat = self.drop_out(feat)

        graph.ndata['fet'] = feat
        hg = dgl.mean_nodes(graph,'fet')

        hg = self.classify(hg)

        with graph.local_scope():
            return self.logsoftmax(hg)

class DGCNN_Classifier(nn.Module):
    def __init__(self,classes, dim_input, dim_hidden, drop_out,
                latent_dim=[1024, 1024, 1024, 512], # output_dim of gcn layers
                 K=100,
                 conv1d_channels=[16, 32], # out_channels of conv1d layers
                 conv1d_kws=[0, 5]): # kernel_size of conv1d layers
        super(DGCNN_Classifier, self).__init__()

        self.classes = classes
        self.dim_input = dim_input
        self.dim_hidden = dim_hidden
        self.K = K
        self.total_latent_dim = sum(latent_dim)
        conv1d_kws[0] = self.total_latent_dim

        self.gcn1 = GraphConv(in_feats=self.dim_input, out_feats=latent_dim[0], norm='right')
        self.gcn2 = GraphConv(in_feats=latent_dim[0], out_feats=latent_dim[1],norm='right')
        self.gcn3 = GraphConv(in_feats=latent_dim[1], out_feats=latent_dim[2], norm='right')
        self.gcn4 = GraphConv(in_feats=latent_dim[2], out_feats=latent_dim[3],norm='right')

        self.sortpooling = SortPooling(k=K) # sortpooling for batch
        self.conv1 = nn.Conv1d(1, conv1d_channels[0], conv1d_kws[0], conv1d_kws[0])
        self.maxpool1d = nn.MaxPool1d(2,2)
        self.conv2 = nn.Conv1d(conv1d_channels[0], conv1d_channels[1], conv1d_kws[1], 1)
        self.relu = nn.ReLU(inplace=True)
        self.drop_out = nn.Dropout(drop_out)

        dense_dim = (int((self.K - 2) / 2 + 1) - conv1d_kws[1] + 1) * conv1d_channels[1]
        self.dense1 = nn.Linear(dense_dim,128)
        self.dense2 = nn.Linear(128,self.classes)
        self.logsoftmax = nn.LogSoftmax(dim=1)

    def forward(self, graph, feat):
        bsz = graph.batch_size
        ''' graph convolution layers '''
        feat1 = th.tanh(self.gcn1(graph, feat))  # shape: num_nodes_batch, 1024
        feat2 = th.tanh(self.gcn2(graph, feat1))
        feat3 = th.tanh(self.gcn3(graph, feat2))
        feat4 = th.tanh(self.gcn4(graph, feat3))  # shape: num_nodes_batch, 512
        cat_feats = th.cat([feat1,feat2,feat3,feat4],1)  # shape: num_nodes_batch, 1024+1024+1024+512

        ''' sortpooling layer '''
        batch_sortpooling = self.sortpooling(graph, cat_feats) # [bsz, K*(1024+1024+1024+512)]

        '''1d convlution and dense layers '''
        feat = batch_sortpooling.view((-1, 1, self.K * self.total_latent_dim)) # [bsz, 1, K*(1024+1024+1024+512)]
        feat = self.relu(self.conv1(feat)) # [bsz, 16, 100]
        feat = self.maxpool1d(feat) # [bsz, 16, 50]
        feat = self.relu(self.conv2(feat)) # [32, 32, 46]

        feat = feat.view(bsz,-1) # [32, 1472]
        feat = self.relu(self.dense1(feat)) # [32, 128]
        feat = self.drop_out(feat)
        hg = self.dense2(feat)

        with graph.local_scope():
            return self.logsoftmax(hg)
