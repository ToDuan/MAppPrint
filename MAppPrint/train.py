
from dataloader import DataTransLoad
from gcn_classifier import GCN_Classifier,GAT_Classifier,DGCNN_Classifier,SAGE_Classifier
import numpy as np
import pandas as pd
import torch as th
from torch.nn import functional as F
from dgl.dataloading import GraphDataLoader
from dgl.data import DGLDataset
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
import json
import time
import logging
import dgl
import os

# Select GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
device = th.device("cuda" if th.cuda.is_available() else "cpu")

params = {
    "dataset": "SIM-APP", # Dataset
    "time_win": "5", # Traffic traces collected time window: 5s; 10s; 20s; 30s; 60s.

    "in_feats": 22,
    "EPOCHS": 400,
    "batch_size": 32,
    "hidden_dim": 128,
    "lr": 0.001,
    "drop_out": 0.1,

    "gnn_model": "GAT", # TBCGs representation model: GAT, GCN, SAGE, DGCNN
    "gnn_layers": 2,
    "gat_heads": 4,

    "dgcnn_k": 40,
    'softmax_temp':'no'
}

# Logger
def getLogger(logfile_path):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt="[%(asctime)s|%(filename)s|%(levelname)s] %(message)s")
    # StreamHandler
    sHandler = logging.StreamHandler()
    sHandler.setFormatter(formatter)
    logger.addHandler(sHandler)

    # FileHandler
    fHandler = logging.FileHandler(logfile_path, mode='w')
    fHandler.setLevel(logging.DEBUG)
    fHandler.setFormatter(formatter)
    logger.addHandler(fHandler)

    return logger

time_win = params["time_win"]

dataset_dir = '../Datasets/TBCGs/{}'.format(params['dataset'])

trainset_path = "{}/{}/{}_dgl.bin".format(dataset_dir,time_win, 'train_graphs')
testset_path = "{}/{}/{}_dgl.bin".format(dataset_dir,time_win, 'test_graphs')
app2labeldict_path = '{}/{}/LabelSpaceDict.json'.format(dataset_dir,time_win)

logfile_save_path = './train_log/{}/{}_{}_layer={}_hidden_dim={}_lr={}_epoch={}_bsz={}.log'.format(
    params["dataset"],params["time_win"],params["gnn_model"],params["gnn_layers"],params["hidden_dim"],params["lr"],params["EPOCHS"],
    params["batch_size"])

result_save_path = './train_result/{}/{}_{}_layer={}_hidden_dim={}_lr={}_epoch={}_bsz={}.csv'.format(
    params["dataset"],params["time_win"],params["gnn_model"],params["gnn_layers"],params["hidden_dim"],params["lr"],params["EPOCHS"],
    params["batch_size"])

model_save_path = './trained_model/{}/{}_{}_layer={}_hidden_dim={}_lr={}_epoch={}_bsz={}.pt'.format(
    params["dataset"],params["time_win"],params["gnn_model"],params["gnn_layers"],params["hidden_dim"],params["lr"],params["EPOCHS"],
    params["batch_size"])
logger = getLogger(logfile_save_path)

logger.info("------------Training Information:------------")
logger.info("--Dataset: [{}]--Time Windows: [{}]--".format(params["dataset"],params["time_win"]))
logger.info("---------------------------------------------")
if params["gnn_model"] == "DGCNN":
    logger.info("--Model: [DGCNN]--layers: [4]--K: [{}]--".format(params["dgcnn_k"]))
elif params["gnn_model"] == "GAT":
    logger.info("--Model: [GAT]--layers: [{}]--heads: [{}]--".format(params["gnn_layers"],params["gat_heads"]))
else:
    logger.info("----Model: [{}]----layers: [{}]----".format(params["gnn_model"], params["gnn_layers"]))
logger.info("----In_feature_dim: [{}]----Hidden_dim: [{}]----".format(params["in_feats"],params["hidden_dim"]))
logger.info("----Batch Size: [{}]----Learning Rate: [{}]----".format(params["batch_size"],params["lr"]))
logger.info("----Epochs: [{}]----Dropout: [{}]----".format(params["EPOCHS"],params["drop_out"]))

logger.info("---------------------------------------------")

train_graphs, train_graph_labels = DataTransLoad(usedumpData=True, dumpFilename=trainset_path)
test_graphs, test_graph_labels = DataTransLoad(usedumpData=True, dumpFilename=testset_path)

with open(app2labeldict_path, 'r') as f:
    App2label = json.load(f)

SIM-APP = ['diijam', 'myradio', 'spotify', 'nhaccuatui', 'soundcloud', 'sachnoiapp', 'truyenaudiosachnoiviet',
            'voizfm',
            'tunefm', 'radiofm', 'nhacvang', 'wesing', 'kaka', 'podcast_player', 'starmarker', 'zingmp3', 'truyenaudio']

def sampling(app_label2inx, subdataset, graphs, labels):
    subdata_label = [app_label2inx[app] for app in subdataset] # indx label of subdataset in app_label space
    # sample target subdataset from total dataset
    smp_graphs = []
    smp_labels = []
    for label, graph in zip(labels, graphs):
        if label in subdata_label:
            smp_graphs.append(dgl.add_self_loop(graph).to(device))
            smp_labels.append(label)

    # label index transform
    app_idx2label = {}
    for app, idx in app_label2inx.items():
        app_idx2label[idx] = app

    subapp_label2idx = {}
    for i, app in enumerate(subdataset):
        subapp_label2idx[app] = i

    subapp_labelname = [] # real label names of subdataset
    for label in smp_labels:
        subapp_labelname.append(app_idx2label[label.item()])

    subapp_idxlabels = []
    for name in subapp_labelname:
        subapp_idxlabels.append(subapp_label2idx[name])

    return smp_graphs, th.tensor(subapp_idxlabels).to(device), subapp_label2idx

if params['dataset']=='App_Simi':
    target_datastet = App_Simi
elif params['dataset']=='App_Diff':
    target_datastet = App_Diff
elif params['dataset']=='FOAP':
    target_datastet = FOAP
elif params['dataset']=='SAMF':
    target_datastet = SAMF

classes_num = len(target_datastet)
BATCH_SIZE = params['batch_size']
EPOCHS = params['EPOCHS']
INIT_LR = params['lr']
in_feats = params['in_feats']

logger.info("Sample target dataset...")
train_graphs, train_graph_labels, labelspace = sampling(App2label, target_datastet, train_graphs, train_graph_labels)
test_graphs, test_graph_labels, labelspace2 = sampling(App2label, target_datastet, test_graphs, test_graph_labels)
assert labelspace == labelspace2

# DGL Training set
class Traindataset(DGLDataset):

    def __init__(self, raw_dir=None, force_reload=False, verbose=False):
        super().__init__(name='Train',
                         raw_dir=raw_dir,
                         force_reload=force_reload,
                         verbose=verbose)

    def process(self):
        self.graphs, self.label = train_graphs, train_graph_labels

    def __getitem__(self, idx):
        return self.graphs[idx], self.label[idx]

    def __len__(self):
        return len(self.graphs)

    @property
    def num_labels(self):
        return classes_num

# DGL Testing set
class Testdataset(Traindataset):
    def process(self):
        self.graphs, self.label = test_graphs, test_graph_labels

logger.info('Loading to DGLgraph...')
dataset_train = Traindataset()
dataloader_train = GraphDataLoader(dataset_train, batch_size=BATCH_SIZE, drop_last=True, shuffle=True)
dataset_test = Testdataset()
dataloader_test = GraphDataLoader(dataset_test, batch_size=BATCH_SIZE, drop_last=True, shuffle=True)

trainSteps = dataset_train.__len__() // BATCH_SIZE
valSteps = dataset_test.__len__() // BATCH_SIZE

logger.info("Load GNN model: {}...".format(params['gnn_model']))
if params['gnn_model'] == 'GAT':
    model = GAT_Classifier(
                            classes=classes_num,num_layers=params['gnn_layers'],drop_out=params['drop_out'],
                            dim_input=in_feats,dim_hidden= params['hidden_dim'], num_heads=params['gat_heads'],
                            softmax_temp=params['softmax_temp'])
elif params['gnn_model'] == 'GCN':
    model =GCN_Classifier(
                            classes=classes_num,num_layers=params['gnn_layers'],drop_out=params['drop_out'],
                            dim_input=in_feats,dim_hidden= params['hidden_dim'])
elif params['gnn_model'] == 'SAGE':
    model = SAGE_Classifier(
                            classes=classes_num,num_layers=params['gnn_layers'],drop_out=params['drop_out'],
                            dim_input=in_feats,dim_hidden= params['hidden_dim'])
elif params['gnn_model'] == 'DGCNN':
    model = DGCNN_Classifier(
                            classes=classes_num,drop_out=params['drop_out'],dim_input=in_feats,
                            dim_hidden= params['hidden_dim'],
                            K = params['dgcnn_k'],
                            latent_dim=[1024, 1024, 1024, 512],
                            conv1d_channels = [16, 32],
                            conv1d_kws = [0, 5]
                             )
else:
    logger.info("Model definition error!")

model.to(device)
opt = th.optim.Adam(model.parameters(), lr=INIT_LR)

results = []
time_epoch = []
logger.info("Training......")
current_acc = 0

# Training
for epoch in range(EPOCHS):
    model.train()

    totalTrainLoss = 0
    totalValLoss = 0
    trainCorrect = 0.00
    valCorrect = 0.00
    startTime_train = time.time()
    for batched_graph, labels in dataloader_train:
        feats = batched_graph.ndata['fet'].type(th.float)
        pred = model(batched_graph, feats)
        loss = F.cross_entropy(pred, labels)

        opt.zero_grad()
        loss.backward()
        opt.step()

        totalTrainLoss += loss.detach().item()
        trainCorrect += (pred.argmax(1) == labels).type(
            th.float).sum().item()
    endTime_train = time.time()
    time_epoch.append(endTime_train-startTime_train)

    with th.no_grad():
        model.eval()
        for batched_graph, labels in dataloader_test:
            feats = batched_graph.ndata['fet'].type(th.float)
            pred = model(batched_graph, feats)
            loss = F.cross_entropy(pred, labels)

            pred = F.softmax(pred,dim=1)
            totalValLoss += loss.detach().item()
            valCorrect += (pred.argmax(1) == labels).type(
                th.float).sum().item()

    avgTrainLoss = totalTrainLoss / trainSteps
    avgValLoss = totalValLoss / valSteps

    trainCorrect = trainCorrect / (trainSteps * BATCH_SIZE)
    valCorrect = valCorrect / (valSteps * BATCH_SIZE)

    results.append([epoch,avgTrainLoss,trainCorrect,avgValLoss,valCorrect])

    logger.info("[{}_Model] EPOCH: {}/{}-{}s".format(params["gnn_model"],epoch + 1, EPOCHS, int(endTime_train - startTime_train)))
    logger.info("Train loss: {:.6f}, Train accuracy: {:.4f}, Val loss: {:.6f}, Val accuracy: {:.4f}".format(
        avgTrainLoss, trainCorrect, avgValLoss, valCorrect))

    if current_acc < valCorrect:
        current_acc = valCorrect
        th.save(model.state_dict(), model_save_path)

model.eval()
#model.to(device)
with th.no_grad():
    pred = []
    true = []
    for batched_graph, labels in dataloader_test:
        feats = batched_graph.ndata['fet'].type(th.float)
        outputs = model(batched_graph, feats)
        outputs = F.softmax(outputs,dim=1)
        _, predicted = th.max(outputs.data, 1)
        pred.extend(predicted.cuda().data.cpu().numpy())
        true.extend(labels.cuda().data.cpu().numpy())

logger.info(classification_report(true, pred, target_names=labelspace, digits=4))

results = pd.DataFrame(results)
results.to_csv(result_save_path,sep=',',header=False,index=False)
