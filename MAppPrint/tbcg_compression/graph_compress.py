
import numpy as np
import os
import pandas as pd
import time
import threading
from multiprocessing import Process,Manager
from tqdm import trange
pd.options.mode.chained_assignment = None

def merge_one_graph(nodes, edges, dense_node_features, dense_edge_weights,short_bst_pt_list,long_bst_fp_list):
    for j in range(nodes.shape[0]):
        if nodes.iloc[j].dir == -1:
            nodes['pk_list_in_burst'].iloc[j] = str([-k for k in eval(nodes['pk_list_in_burst'].iloc[j])])

    nodes_short = nodes[nodes.length <= 3]
    nodes_long = nodes[nodes.length > 3]

    # for short burst
    for k in range(nodes_short.shape[0]):
        if nodes_short.pk_list_in_burst.iloc[k] in short_bst_pt_list:
            nodes_short['agent'].iloc[k] = nodes_short.pk_list_in_burst.iloc[k]

    for k in range(nodes_long.shape[0]):
        for l in long_bst_fp_list:
            if l in nodes_long.pk_list_in_burst.iloc[k]:
                nodes_long['agent'].iloc[k] = l
                break

    nodes = pd.concat((nodes_short, nodes_long), axis=0).sort_values(by='burst_idx')

    # node feature merge:
    nodes_N = nodes[nodes.agent == 'N']
    nodes_M = nodes[nodes.agent != 'N']

    merge_map_dict = {}

    merge_nodes_features = nodes_M.groupby(['agent'], as_index=False). \
        agg({
        'length': ['mean'],
        'bytes': ['mean'],
        'dur': ['mean'],
        'byte_rate': ['mean'],
        'ti2next_burst': ['mean'],
        'ps_max': ['mean'],
        'ps_min': ['mean'],
        'ps_mean': ['mean'],
        'ps_std': ['mean'],
        'ps_per25': ['mean'],
        'ps_per50': ['mean'],
        'ps_per_75': ['mean'],
        'ps_mode1': ['mean'],
        'ti_max': ['mean'],
        'ti_min': ['mean'],
        'ti_mean': ['mean'],
        'ti_std': ['mean'],
        'ti_per25': ['mean'],
        'ti_per50': ['mean'],
        'ti_per75': ['mean']
    })

    merge_nodes_features.columns = ['agent', 'length', 'bytes', 'dur',
                                    'byte_rate', 'ti2next_burst', 'ps_max', 'ps_min', 'ps_mean', 'ps_std',
                                    'ps_per25', 'ps_per50', 'ps_per_75', 'ps_mode1', 'ti_max', 'ti_min',
                                    'ti_mean', 'ti_std', 'ti_per25', 'ti_per50', 'ti_per75']

    nodes_M = nodes_M.drop_duplicates(subset='agent', keep='first')
    merge_nodes_idx = nodes_M.iloc[:, [1, -1]]

    for l in range(merge_nodes_idx.shape[0]):
        agt = merge_nodes_idx.agent.iloc[l]
        bst_idx = merge_nodes_idx.burst_idx.iloc[l]
        for soc in nodes[nodes.agent == agt].burst_idx.tolist():
            merge_map_dict[soc] = bst_idx
    for soc in nodes_N.burst_idx.tolist():
        merge_map_dict[soc] = soc

    nodes_M = nodes_M.drop(columns=['length', 'bytes', 'dur',
                                    'byte_rate', 'ti2next_burst', 'ps_max', 'ps_min', 'ps_mean', 'ps_std',
                                    'ps_per25', 'ps_per50', 'ps_per_75', 'ps_mode1', 'ti_max', 'ti_min',
                                    'ti_mean', 'ti_std', 'ti_per25', 'ti_per50', 'ti_per75'])

    nodes_M = pd.merge(nodes_M, merge_nodes_features, on='agent', how='inner')
    nodes_M = nodes_M.iloc[:,
                  [0, 1, 2, 3,
                   16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
                   4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]]
    # merged nodes
    nodes = pd.concat((nodes_N, nodes_M), axis=0,sort=True).sort_values(by='burst_idx')

    # edge merge:
    edges['source'] = edges['source'].map(merge_map_dict)
    edges['target'] = edges['target'].map(merge_map_dict)

    edges = edges.groupby(['source', 'target'], as_index=False). \
        agg({
        'weight': ['sum'], # edge weight merge
        'graph_id': ['min'],
        'edge_type': ['min']
    })

    edges.columns = ['source', 'target', 'weight', 'graph_id', 'edge_type']
    edges = edges[edges.source != edges.target]

    dense_node_features = pd.concat((dense_node_features, nodes), axis=0)
    dense_edge_weights = pd.concat((dense_edge_weights, edges), axis=0, sort=True)

    return dense_node_features,dense_edge_weights

def process_one_app(app_dir,app,bust_pf,big_graph_bar,num_node_list,num_edge_list):
    print("In app {} ...".format(app))

    node_features = pd.read_csv(os.path.join(app_dir,app, 'features.csv'))
    edge_weights = pd.read_csv(os.path.join(app_dir,app, 'weights.csv'))

    app_bst_pf = bust_pf
    short_bst_pt = app_bst_pf[app_bst_pf.bst_type == 'short']
    short_bst_pt_list = short_bst_pt.sequence.tolist()
    long_bst_fp = app_bst_pf[app_bst_pf.bst_type == 'long']
    long_bst_fp_list = [st[1:-1] for st in long_bst_fp.sequence.tolist()]

    num_graphs = node_features.graph_id.max()

    dense_node_features = pd.DataFrame()
    dense_edge_weights = pd.DataFrame()

    for i in range(1, num_graphs + 1):

        nodes = node_features[node_features.graph_id == i]
        edges = edge_weights[edge_weights.graph_id == i]
        nodes['agent'] = 'N'

        if nodes.shape[0] <= big_graph_bar:
            dense_node_features = pd.concat((dense_node_features, nodes), axis=0)
            dense_edge_weights = pd.concat((dense_edge_weights, edges), axis=0, sort=True)
            continue
        dense_node_features, dense_edge_weights = merge_one_graph(nodes=nodes, edges=edges,
                                                                  dense_node_features=dense_node_features,
                                                                  dense_edge_weights=dense_edge_weights,
                                                                  short_bst_pt_list=short_bst_pt_list,
                                                                  long_bst_fp_list=long_bst_fp_list)
    # save
    node_dense_pre = 1 - (dense_node_features.shape[0]/node_features.shape[0])
    edge_dense_pre = 1 - (dense_edge_weights.shape[0]/edge_weights.shape[0])
    num_node_list.append((dense_node_features.shape[0],node_features.shape[0]))
    num_edge_list.append((dense_edge_weights.shape[0],edge_weights.shape[0]))
    print("Dense Ration of App {}: node = {}; edge = {}".format(app,node_dense_pre,edge_dense_pre))
    
    num_dense_graphs = set(dense_node_features.graph_id).__len__()
    print("Num Graphs: {}, Num Densed Graph: {}".format(num_graphs, num_dense_graphs))
    dense_node_features.to_csv(os.path.join(app_dir,app, 'dense_all_features.csv'))
    dense_edge_weights.to_csv(os.path.join(app_dir,app, 'dense_all_weights.csv'))


def process_app_multithread(root_dir,bust_pf,big_graph_bar,num_node_list,num_edge_list):

    processes = []
    counter = 0
    app_dir = os.listdir(root_dir)

    for app in app_dir:
        counter += 1
        print("Processing....{}: {}/{}".format(app, counter, len(app_dir)))

        # sub-process
        proc = Process(target=process_one_app, args=(root_dir, app, bust_pf,big_graph_bar,num_node_list,num_edge_list,))
        processes.append(proc)
        proc.start()

    for proc in processes:
        proc.join()

    return num_node_list,num_edge_list

def compute_dense_ration(num_list):
    dense,raw = 0, 0
    for d, r in num_list:
        dense += d
        raw += r
    return round(1-dense/raw,4)

if __name__ == "__main__":
    time_win = '10_0'
    
    start_time = time.time()
    num_node_list = Manager().list()
    num_edge_list = Manager().list()

    # train set
    root_dir = '../Datasets/TBCGs/FOAP/{}/train_graphs/'.format(time_win)
    bst_fp_path = '../Datasets/TBCGs/FOAP/{}/burst_pf.csv'.format(time_win)
    bust_pf = pd.read_csv(bst_fp_path)

    bust_pf = bust_pf.sort_values(by='total_conf',ascending=False)
    bust_pf = bust_pf.drop_duplicates(subset=['sequence'])

    Node_CDF90_FOAP = {
        '5_0':0,
        '10_0':0,
        '20_5':0,
        '30_15':0,
        '60_30':0,
            }

    node_cdf90 = Node_CDF90_FOAP[time_win]

    num_node_list,num_edge_list = process_app_multithread(root_dir=root_dir,bust_pf=bust_pf,big_graph_bar=node_cdf90,num_node_list=num_node_list,num_edge_list=num_edge_list)
    
    node_dense_ration = compute_dense_ration(num_node_list)
    edge_dense_ration = compute_dense_ration(num_edge_list)
    print("Total node dense ration = {}; edge dense ration = {}".format(node_dense_ration,edge_dense_ration))
    
    # test set
    root_dir = '../Datasets/TBCGs/FOAP/{}/test_graphs/'.format(time_win)
    num_node_list = Manager().list()
    num_edge_list = Manager().list()

    num_node_list,num_edge_list = process_app_multithread(root_dir=root_dir,bust_pf=bust_pf,big_graph_bar=node_cdf90,num_node_list=num_node_list,num_edge_list=num_edge_list)
    
    node_dense_ration = compute_dense_ration(num_node_list)
    edge_dense_ration = compute_dense_ration(num_edge_list)
    print("Total node dense ration = {}; edge dense ration = {}".format(node_dense_ration,edge_dense_ration))

    end_time = time.time()
    print("Running Time：", (end_time - start_time)//60, "mins")

