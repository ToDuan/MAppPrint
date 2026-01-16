
import os
import dgl
from dgl.data.utils import load_graphs,save_graphs
import pandas as pd
import json
#import logger_wrappers
import torch as th
import numpy as np
import tqdm

features = [
            'length','bytes','dur','byte_rate','ti2next_burst',
            'ps_max','ps_min','ps_mean','ps_std', 'ps_per25', 'ps_per50', 'ps_per_75','ps_mode1',
            'ti_max','ti_min','ti_mean','ti_std', 'ti_per25', 'ti_per50', 'ti_per75'
            ]

def gene_dglGraph(data_dir,AppName,labelNameSet):

    graphs_app = []

    features_path = os.path.join(data_dir, AppName, 'features.csv')
    weights_path = os.path.join(data_dir, AppName, 'weights.csv')

    features_df = pd.read_csv(features_path, index_col=0)
    weights_df = pd.read_csv(weights_path, index_col=0)

    graph_num = features_df['graph_id'].iloc[-1]

    for i in range(1, graph_num + 1):  # # for each graph of an app
        feature_df = features_df[features_df['graph_id'] == i]
        feature_df = feature_df[['burst_idx'] + features + ['graph_id']]

        feature_df = feature_df.drop_duplicates(subset=['burst_idx'], keep='first').sort_values('burst_idx')

        num_nodes = feature_df.shape[0]

        raw_burst_idx = feature_df.burst_idx.to_list()
        burst_reidx_map = {}
        for j in range(num_nodes):
            burst_reidx_map[raw_burst_idx[j]] = j

        feature_df['burst_idx'] = feature_df['burst_idx'].map(burst_reidx_map)

        weight_df = weights_df[weights_df['graph_id'] == i].reset_index(drop=True)  # 删除索引列

        weight_df['source'] = weight_df['source'].map(burst_reidx_map)
        weight_df['target'] = weight_df['target'].map(burst_reidx_map)

        src = weight_df['source'].astype(np.int32)
        dst = weight_df['target'].astype(np.int32)

        graph = dgl.graph((src, dst), num_nodes=num_nodes)

        node_fet = th.tensor(feature_df[features].to_numpy())
        edge_wt = th.tensor(weight_df.weight.to_numpy())
        #edge_tp = th.tensor(weight_df.edge_type.to_numpy())

        graph.ndata['fet'] = node_fet
        graph.edata['wt'] = edge_wt

        graphs_app.append(graph)

    labels_app = [labelNameSet[AppName]] * len(graphs_app)

    return graphs_app, labels_app

def DataTransLoad(split_chunks_directory='',time_win='5_0',dataset='train_graphs',usedumpData=False,
                 dumpFilename="xxx.bin"):
    if usedumpData:
        print('Load dump data from {0}...'.format(dumpFilename))
        graphs, labels_dict = load_graphs(dumpFilename)
        labels = labels_dict['glabel']
        return graphs, labels

    else:

        if os.path.isdir(split_chunks_directory) == False:
            info = '{0} is not a directory'.format(split_chunks_directory)
            print(info)
            raise BaseException(info)

        labelNameSet = {}
        graphs_all = []
        labels_all = []

        data_dir = os.path.join(split_chunks_directory, time_win, dataset)

        _labelNameSet = []  # all apps (label space)
        for _root, _dirs, _files in os.walk(data_dir):
            if _root == data_dir:
                continue
            _root = _root.replace("\\", "/")
            AppName = _root.split("/")[-1]
            _labelNameSet.append(AppName)
        _labelNameSet.sort()

        for i in range(len(_labelNameSet)):
            labelNameSet.setdefault(_labelNameSet[i], len(labelNameSet))
            # string label --> index label

        for _root, _dirs, _files in os.walk(data_dir):  # for each app
            if _root == data_dir:
                continue
            _root = _root.replace("\\", "/")
            AppName = _root.split("/")[-1]
            print('Processing App: {} ...'.format(AppName))

            graphs_app, labels_app = gene_dglGraph(data_dir, AppName, labelNameSet)

            graphs_all.extend(graphs_app)
            labels_all.extend(labels_app)

        # save
        graph_labels = {"glabel": th.tensor(labels_all)}
        save_graphs(dumpFilename,graphs_all,graph_labels)

        with open(os.path.join(split_chunks_directory, time_win, 'LabelSpaceDict.json'), "w") as tf:
            json.dump(labelNameSet,tf)

if __name__ == '__main__':

    split_chunks_directory= ''
    time_win='5'
    train_dataset = 'train_graphs' # train_graphs or test_graphs
    test_dataset = 'test_graphs'

    TraindumpFilename = "./{}/{}_dgl.bin".format(time_win,train_dataset)
    TestdumpFilename = "./{}/{}_dgl.bin".format(time_win,test_dataset)

    DataTransLoad(split_chunks_directory=split_chunks_directory,
                  time_win=time_win,
                  dataset=test_dataset,
                  usedumpData=False,
                  dumpFilename=TestdumpFilename)
