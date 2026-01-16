
from dataloader import DataTransLoad
from gcn_classifier import GCN_Classifier,GAT_Classifier,DGCNN_Classifier,SAGE_Classifier
import numpy as np
import pandas as pd
import torch as th
from torch.nn import functional as F
from dgl.dataloading import GraphDataLoader
from dgl.data import DGLDataset
from torch.utils.data.sampler import WeightedRandomSampler
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
import json
import time
import logging
import dgl
import os

#os.environ['CUDA_VISIBLE_DEVICES'] = '1'
device = th.device("cuda" if th.cuda.is_available() else "cpu")

params = {
    "dataset": "FOAP",
    "time_win": "5_0",

    "in_feats": 22,
    "EPOCHS": 100,
    "batch_size": 8,
    "hidden_dim": 128,
    "lr": 0.0001,
    "drop_out": 0.1,

    "gnn_model": "GAT", # GAT, GCN, SAGE, DGCNN
    "gnn_layers":2,
    "gat_heads": 4,
    "dgcnn_k": 100
}

####Logger
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

trainset_path = ''
testset_path = ''
app2labeldict_path = ''

train_graphs, train_graph_labels = DataTransLoad(usedumpData=True, dumpFilename=trainset_path)
test_graphs, test_graph_labels = DataTransLoad(usedumpData=True, dumpFilename=testset_path)

with open(app2labeldict_path, 'r') as f:
    App2label = json.load(f)

App_Simi = ['diijam', 'myradio', 'spotify', 'nhaccuatui', 'soundcloud', 'sachnoiapp', 'truyenaudiosachnoiviet',
            'voizfm',
            'tunefm', 'radiofm', 'nhacvang', 'wesing', 'kaka', 'podcast_player', 'starmarker', 'zingmp3', 'truyenaudio']

def sampling(app_label2inx, subdataset, graphs, labels):
    subdata_label = [app_label2inx[app] for app in subdataset] # indx label of subdataset in app_label space

    smp_graphs = []
    smp_labels = []
    for label, graph in zip(labels, graphs):
        if label in subdata_label:
            smp_graphs.append(dgl.add_self_loop(graph).to(device))
            smp_labels.append(label)

    app_idx2label = {}
    for app, idx in app_label2inx.items():
        app_idx2label[idx] = app

    subapp_label2idx = {}
    for i, app in enumerate(subdataset):
        subapp_label2idx[app] = i

    subapp_labelname = []
    for label in smp_labels:
        subapp_labelname.append(app_idx2label[label.item()])

    subapp_idxlabels = []
    for name in subapp_labelname:
        subapp_idxlabels.append(subapp_label2idx[name])

    return smp_graphs, th.tensor(subapp_idxlabels).to(device), subapp_label2idx


target_datastet = FOAP
classes_num = len(target_datastet)

BATCH_SIZE = params['batch_size']
EPOCHS = params['EPOCHS']
INIT_LR = params['lr']
in_feats = params['in_feats']

train_graphs, train_graph_labels, labelspace = sampling(App2label, target_datastet, train_graphs, train_graph_labels)
test_graphs, test_graph_labels, labelspace2 = sampling(App2label, target_datastet, test_graphs, test_graph_labels)
assert labelspace == labelspace2

allLabelidx = sorted(labelspace2.values())

class Traindataset(DGLDataset):

    def __init__(self, raw_dir=None, force_reload=False, verbose=False):
        super().__init__(name='Train',raw_dir=raw_dir,force_reload=force_reload,verbose=verbose)

    def process(self):
        self.graphs, self.label = train_graphs, train_graph_labels

    def __getitem__(self, idx):
        return self.graphs[idx], self.label[idx]

    def __len__(self):
        return len(self.graphs)

    @property
    def num_labels(self):
        return classes_num

class Testdataset(Traindataset):
    def process(self):
        self.graphs, self.label = test_graphs, test_graph_labels

class BinaryTraindataset(Traindataset):
    def process(self):
        self.graphs, self.label = train_graphs_binary, train_graph_labels_binary

class BinaryTestdataset(Traindataset):
    def process(self):
        self.graphs, self.label = test_graphs_binary, test_graph_labels_binary


## The training and testing dataset required for converting into a binary classifier.
def trans_data_binary(target_label,data,label):

    num_sample = len(data)
    pst_sampleidx = np.where(np.array(label.tolist()) == target_label)[0].tolist()

    pst_minidx, pst_maxidx = pst_sampleidx[0], pst_sampleidx[-1]
    num_pst, num_net = len(pst_sampleidx), num_sample-len(pst_sampleidx)
    assert pst_maxidx - pst_minidx + 1 == len(pst_sampleidx)

    pst_graphs = data[pst_minidx:pst_maxidx + 1]
    pst_label = [1] * num_pst

    if pst_minidx == 0:
        net_graphs = data[pst_maxidx + 1:]
    else:
        net_graphs = data[:pst_minidx] + data[pst_maxidx + 1:]
    net_label = [0] * num_net

    trans_data = pst_graphs + net_graphs
    trans_label = pst_label + net_label

    return trans_data, th.tensor(trans_label).to(device),num_pst,num_net

model_list = []

for classidx in allLabelidx: # for each class

    train_graphs_binary, train_graph_labels_binary,num_pst_train,num_net_train = trans_data_binary(target_label=classidx,data=train_graphs,label=train_graph_labels)
    test_graphs_binary, test_graph_labels_binary,_,_ = trans_data_binary(target_label=classidx,data=test_graphs,label=test_graph_labels)

    dataset_train = BinaryTraindataset()
    sample_weights = []
    sample_weights.extend([1 / num_pst_train] * num_pst_train)
    sample_weights.extend([1 / num_net_train] * num_net_train)
    train_sampler = WeightedRandomSampler(sample_weights, num_pst_train*2, replacement = False)
    dataloader_train = GraphDataLoader(dataset_train, batch_size=BATCH_SIZE,sampler=train_sampler,
                                       drop_last=True, shuffle=False)

    dataset_test = BinaryTestdataset()
    dataloader_test = GraphDataLoader(dataset_test, batch_size=BATCH_SIZE, drop_last=True, shuffle=True)

    trainSteps = dataset_train.__len__() // BATCH_SIZE
    valSteps = dataset_test.__len__() // BATCH_SIZE

    model = GAT_Classifier(classes=2,num_layers=params['gnn_layers'],drop_out=params['drop_out'],
                           dim_input=in_feats,dim_hidden= params['hidden_dim'], num_heads=params['gat_heads'])

    model.to(device)
    opt = th.optim.Adam(model.parameters(), lr=INIT_LR)

    results = []
    time_epoch = []
    current_acc = 0

    # Train the model
    for epoch in range(EPOCHS):
        # set the model in training mode
        model.train()

        # initialize the total training and validation loss
        totalTrainLoss = 0
        totalValLoss = 0

        predicted_labels = []
        gt_labels = []

        startTime_train = time.time()
        for batched_graph, labels in dataloader_train:
            feats = batched_graph.ndata['fet'].type(th.float)  # node feature, trans to float32

            # perform a forward pass and calculate the training loss
            pred = model(batched_graph, feats) # logits
            loss = F.cross_entropy(pred, labels) ##

            opt.zero_grad()
            loss.backward()
            opt.step()

            totalTrainLoss += loss.detach().item()

            pred = F.softmax(pred, dim=1)
            pred = pred.argmax(1).tolist()
            predicted_labels.extend(pred)
            gt_labels.extend(labels.tolist())

        endTime_train = time.time()
        time_epoch.append(endTime_train - startTime_train)

        accTrain = accuracy_score(gt_labels, predicted_labels,average='weighted')
        preTrain = precision_score(gt_labels, predicted_labels,average='weighted')
        recTrain = recall_score(gt_labels, predicted_labels,average='weighted')

        # switch off autograd for evaluation
        # binary classifier performance
        with th.no_grad():
            # set the model in evaluation mode
            model.eval()

            predicted_labels = []
            gt_labels = []
            # loop over the validation set
            for batched_graph, labels in dataloader_test:
                feats = batched_graph.ndata['fet'].type(th.float)
                # make the predictions and calculate the validation loss
                pred = model(batched_graph, feats)
                loss = F.cross_entropy(pred, labels)

                # calculate the number of correct predictions
                totalValLoss += loss.detach().item()
                pred = F.softmax(pred, dim=1)
                pred = pred.argmax(1).tolist()
                predicted_labels.extend(pred)
                gt_labels.extend(labels.tolist())

        # calculate the average training and validation loss for an epoch
        avgTrainLoss = totalTrainLoss / trainSteps
        avgValLoss = totalValLoss / valSteps

        # calculate the training and validation accuracy
        accTest = accuracy_score(gt_labels, predicted_labels,average='weighted')
        preTest = precision_score(gt_labels, predicted_labels,average='weighted')
        recTest = recall_score(gt_labels, predicted_labels,average='weighted')

        # update our training history
        results.append([epoch, avgTrainLoss, accTrain,preTrain,recTrain, avgValLoss, accTest,preTest, recTest])

        model_save_path = ''
        if current_acc < preTest:
            current_acc = preTest
            th.save(model.state_dict(), model_save_path)

    model_list.append(model)

# Eval the model_list use multi-classification performance
dataset_test = Testdataset()
dataloader_test = GraphDataLoader(dataset_test, batch_size=BATCH_SIZE, drop_last=True, shuffle=True)

with th.no_grad():

    true_All = []
    pred_byAllClassifyer = pd.DataFrame()
    confidence_pstAll = pd.DataFrame()

    for classidx in allLabelidx:

        model = model_list[classidx]
        model.eval()
        model.to(device)

    for batched_graph, labels in dataloader_test:
        feats = batched_graph.ndata['fet'].type(th.float)
        pred_batch = []
        conf_batch = []
        for classidx in allLabelidx:
            outputs = model_list[classidx](batched_graph, feats)
            outputs = F.softmax(outputs, dim=1)  # pred是logits
            confidence_pst = outputs[:, 1]
            _, predicted = th.max(outputs.data, 1)

            pred_batch.append(predicted.cuda().data.cpu().numpy())
            conf_batch.append(confidence_pst.cuda().data.cpu().numpy())

        pred_byAllClassifyer = pd.concat((pred_byAllClassifyer,pd.DataFrame(pred_batch).T),axis=0)
        confidence_pstAll = pd.concat((confidence_pstAll, pd.DataFrame(conf_batch).T), axis=0)
        true_All.extend(labels.cuda().data.cpu().numpy())

    pred_multi_lable = []
    true_muli_label = []

    for idx in range(confidence_pstAll.shape[0]):
        sample_conf = confidence_pstAll.iloc[idx]
        multi_lable = sample_conf.idxmax()
        pred_multi_lable.append(multi_lable)
        true_muli_label.append(true_All[idx])

    availability = round(len(true_muli_label)/len(true_All),4)
    classification_report(true_muli_label, pred_multi_lable, target_names=labelspace, digits=4)
    #logger.info(classification_report(true, pred, target_names=labelspace, digits=4))
