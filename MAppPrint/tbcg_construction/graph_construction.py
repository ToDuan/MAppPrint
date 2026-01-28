
import random
import pandas as pd

pd.options.mode.chained_assignment = None
import os
import pandas as pd
import numpy as np
import json
from functools import partial
import scipy
import scipy.stats
import warnings
import time

from multiprocessing import Process,Manager

warnings.filterwarnings('ignore')

root_path = '../Datasets/TBCGs/FOAP/'

duration = 5
overlap = 0

train_size = 5000
test_size = 1000

# APP Name List
target_app =  ['app_a','app_b',...]

#used node features
features = [
            'protocol','dir','length','bytes','dur','byte_rate','ti2next_burst',
            'ps_max','ps_min','ps_mean','ps_std', 'ps_per25', 'ps_per50', 'ps_per_75','ps_mode1',
            'ti_max','ti_min','ti_mean','ti_std', 'ti_per25', 'ti_per50', 'ti_per75'
            ]

def basic_reprocessing(df):

    # remove dns protocol
    df = df[(df['source_port'] != 53) & (df['destination_port'] != 53) &
            (df['source_port'] != 5353) & (df['destination_port'] != 5353) &
            (df['source_port'] != 137) & (df['destination_port'] != 137) &
            (df['source_port'] != 67) & (df['destination_port'] != 67) &
            (df['source_port'] != 68) & (df['destination_port'] != 68) &
            (df['source_port'] != 5355) & (df['destination_port'] != 5355)]

    #1. get packet direction
    df['des_greater_src'] = df['destination_port'] - df['source_port']

    df['dir'] = 0
    df['dir'] = np.where(df['des_greater_src'] > 0, 1, -1)
    # 'dir'=1 : client --> server
    # 'dir'=-1: server --> client

    #2. gene burst index (as node index in future) and time interval for each packet in same flow.
    df['burst_idx'] = 0
    df['time_interval'] = 0
    df['burst_ti'] = 0
    df['flow_start'] = 0
    df['flow_end'] = 0

    flow_ids = set(df.stream_id)
    burst_idx = 0
    flows = []
    for flow_id in flow_ids: # each flow in csv chunk
        flow = df[df.stream_id == flow_id]
        f_start = flow.time.min()
        f_end = flow.time.max()
        sign = 0
        start_burst_idx = burst_idx+1
        for i in range(flow.shape[0]): #each packet
            #
            flow.flow_start.iloc[i] = f_start
            flow.flow_end.iloc[i] = f_end
            #
            if flow.dir.iloc[i] != sign: # first packet of a new burst
                if i != 0 : # not first packet of flow
                    flow.burst_ti.iloc[i-1] = flow.time.iloc[i] - flow.time.iloc[i-1]
                    #compute the time interval between last burst with courrent burst
                burst_idx += 1
                sign = flow.dir.iloc[i]
                flow.burst_idx.iloc[i] = burst_idx
                flow.time_interval.iloc[i] = 0

            else :
                flow.burst_idx.iloc[i] = flow.burst_idx.iloc[i-1]
                flow.time_interval.iloc[i] = flow.time.iloc[i] - flow.time.iloc[i - 1]

        end_burst_id = burst_idx
        flow['start_burst_idx'] = start_burst_idx
        flow['end_burst_id'] = end_burst_id
        flows.append(flow)
    df = pd.concat(flows, ignore_index=True).sort_values(by='time').reset_index(drop=True)

    return df

def extract_burst_feature(df):

    per_25 = partial(pd.Series.quantile, q=0.25)
    per_50 = partial(pd.Series.quantile, q=0.5)
    per_75 = partial(pd.Series.quantile, q=0.75)

    # transform protocol from string type to int ('tcp':0,'udp':1)
    df['protocol'] = df['protocol'] == 'tcp'
    df['protocol'] = df['protocol'].astype('int')

    # merge packets into bursts
    df = df.groupby(['protocol','stream_id', 'burst_idx','dir','flow_start','flow_end','start_burst_idx', 'end_burst_id'], as_index=False). \
        agg({'time' : ['min','max'],
             'burst_ti':['max'],
             'length': ['count', 'sum', 'max', 'min', 'mean','std',per_25,per_50,per_75,lambda x: scipy.stats.mode(x)[0],lambda x: list(x)],
             'time_interval': ['sum', 'max', lambda x: x[x!=0].min(), lambda x: x[x!=0].mean(),  lambda x: x[x!=0].std(),per_25,per_50,per_75]
             })

    df.columns = ['protocol', 'stream_id', 'burst_idx', 'dir','flow_start','flow_end','start_burst_idx', 'end_burst_idx',
                  'start', 'end', # burst's start/end time
                  'ti2next_burst',
                  'length','bytes','ps_max','ps_min','ps_mean','ps_std','ps_per25','ps_per50','ps_per_75','ps_mode1','pk_list_in_burst',
                  'dur','ti_max','ti_min','ti_mean','ti_std','ti_per25','ti_per50','ti_per75']

    df.fillna(0, inplace=True)
    df['byte_rate'] = df['bytes']/df['dur']
    df.byte_rate = np.where(df.byte_rate == np.inf, df.bytes / df.ti2next_burst, df.byte_rate)
    df.byte_rate = np.where(df.byte_rate == np.inf, 0, df.byte_rate)

    return df


def gene_edge_weight(burst_df):
    # create a dataframe of weights
    burst1_list = []  # source node
    burst2_list = []  # target node
    weight_list = []  # edge weight
    weight_type = []

    bursts = list(burst_df['burst_idx'])
    active_bursts = set()  # nodes have edge

    flows_id = set(burst_df.stream_id)

    burst_df['is_start'] = 0
    burst_df['is_end'] = 0

    burst_df.is_start = np.where(burst_df.start==burst_df.flow_start, 1 ,0)
    burst_df.is_end = np.where(burst_df.end==burst_df.flow_end,1,0)

    for flow_id in flows_id:
        flow_df = burst_df[burst_df.stream_id == flow_id]
        for i in range(flow_df.shape[0] - 1):
            bst1 = flow_df.burst_idx.iloc[i]
            bst2 = flow_df.burst_idx.iloc[i + 1]
            burst1_list.append(bst1)
            burst2_list.append(bst2)
            weight_list.append(1)
            weight_type.append(0)
            active_bursts = active_bursts.union({bst1, bst2})
    for i in range(len(bursts)):
        burst_a = burst_df.iloc[i]
        if not burst_a.is_end and burst_a.stream_id == burst_df.iloc[i+1].stream_id:
            continue

        burst_rest = burst_df[(burst_df.stream_id!=burst_a.stream_id) & (burst_df.start>=burst_a.start)]

        for j in range(len(burst_rest)):
            burst_b = burst_rest.iloc[j]
            if burst_b.stream_id == burst_df[burst_df.burst_idx==burst2_list[-1]].stream_id.iloc[0] and \
                burst_a.stream_id == burst_df[burst_df.burst_idx==burst1_list[-1]].stream_id.iloc[0]:
                continue

            gap_ab = burst_b.start - burst_a.end

            if gap_ab <= 20000:
                bst1 = burst_a.burst_idx
                bst2 = burst_b.burst_idx
                if burst1_list[-1] == bst2 and burst2_list[-1] == bst1:
                    continue
                burst1_list.extend([bst2,bst1])
                burst2_list.extend([bst1,bst2])
                weight_list.extend([1,1])
                weight_type.extend([1,1])
                active_bursts = active_bursts.union({bst1, bst2})

            elif gap_ab<=1000000 and burst_a.is_end and burst_b.is_start:
                bst1 = burst_a.burst_idx
                bst2 = burst_b.burst_idx
                burst1_list.append(bst1)
                burst2_list.append(bst2)
                weight_list.append(1)
                weight_type.append(2)
                active_bursts = active_bursts.union({bst1, bst2})
            elif not burst_a.is_end and not burst_b.is_end and burst_a.ti2next_burst >= gap_ab+burst_b.dur+burst_b.ti2next_burst:
                bst1 = burst_a.burst_idx
                bst2 = burst_b.burst_idx

                bstn = burst_b.end_burst_idx
                gap = gap_ab+burst_b.dur+burst_b.ti2next_burst
                for b in range(int(bst2+1), int(bstn)):
                    burst_c = burst_rest[burst_rest.burst_idx == b]
                    gap = gap + burst_c.dur.iloc[0] +burst_c.ti2next_burst.iloc[0]
                    if gap < burst_a.ti2next_burst: continue
                    else: break
                bst3 = bst1 +1
                bst4 = np.float64(b)
                burst1_list.append(bst4)
                burst2_list.append(bst3)
                weight_list.append(1)
                weight_type.append(2)
                active_bursts = active_bursts.union({bst1, bst2})

                burst1_list.append(bst1)
                burst2_list.append(bst2)
                weight_list.append(1)
                weight_type.append(2)
                active_bursts = active_bursts.union({bst1, bst2})

            else: break

    # get nodes without edge to remove
    inactive_bursts = list(set(bursts) - active_bursts)

    # create dataframe of edge weights
    weights_df = pd.DataFrame(
        {
            "source": burst1_list,
            "target": burst2_list,
            "weight": weight_list,
            "edge_type": weight_type
        }
    )

    weights_df = weights_df.sort_values(by="weight", ascending=False, ignore_index=True)

    features_df = burst_df[~burst_df['burst_idx'].isin(inactive_bursts)]
    weights_df = weights_df[~weights_df['source'].isin(inactive_bursts) & ~weights_df['target'].isin(
        inactive_bursts)].reset_index(drop=True)

    # remove reduplicative edges
    weights_df = weights_df.drop_duplicates(subset=['source', 'target'], keep='first').reset_index(drop=True)

    return features_df, weights_df

def generate_features_weights(df):

    df.time = df.time*1000000
    df = basic_reprocessing(df)
    burst_df = extract_burst_feature(df).sort_values(by=['start']).reset_index(drop=True)

    features_df, weights_df = gene_edge_weight(burst_df)

    return features_df, weights_df

def generate_graphs_one_app(app_src, filenames,graphs,app,dataset_type=0,size=0,):

    print('子进程：{}运行中...'.format(os.getpid()))
    feature_columns = ['burst_idx'] + features + ['graph_id']
    weight_columns = ['source', 'target', 'weight', 'graph_id']

    features_df = pd.DataFrame([], columns=feature_columns)
    weights_df = pd.DataFrame([], columns=weight_columns)
    graph_id = 0

    # loop over all traffic chunks of one app
    num_files = len(filenames)
    for k,filename in enumerate(filenames):
        if graph_id >= size:break

        path = os.path.join(app_src, filename)
        df = pd.read_csv(path, index_col=0)
        df = df.sort_values(by='time')

        if df.empty: continue

        try:
            node_data, weights = generate_features_weights(df)
        except:
            #print('WRONG')
            continue

        if weights.shape[0] > 1:
            graph_id = graph_id + 1
            node_data['graph_id'] = graph_id
            weights['graph_id'] = graph_id

            features_df = pd.concat([features_df, node_data], ignore_index=True)
            weights_df = pd.concat([weights_df, weights], ignore_index=True)

    print("Total {} chunks, arm to generate {} graphs, really generate {} graph...".format(len(filenames),size,graph_id))
    graphs[app] = [features_df, weights_df]
    print(graphs.keys())



def gene_graphs_multithreading(duration, overlap, graphs, index=0,dataset_size=0):
    path = os.path.join(root_path, '%d_%d' % (duration, overlap), 'train_test_info.json')
    with open(path, 'r') as f:
        train_test_info = json.load(f)

    samples_folder = os.path.join(root_path, '%d_%d' % (duration, overlap), 'sample')

    idx = 0
    processes = []

    for app in target_app:
        idx += 1
        print('Loading App : {} ... {}/{}'.format(app, idx, len(target_app)))

        app_src = os.path.join(samples_folder, app)
        filenames = train_test_info[app][index]
        random.shuffle(filenames)

        proc = Process(target=generate_graphs_one_app,args=(app_src, filenames, graphs, app, index, dataset_size,))
        processes.append(proc)
        proc.start()

    for proc in processes:
        proc.join()

    print("All app have been processed !!!")
    print("All graph: ",graphs.keys())
    return graphs

def standardize_features(df, mean_std_dic):
    # standardize the features in dataframe
    for feature in mean_std_dic.keys():
        m, std = mean_std_dic[feature][0], mean_std_dic[feature][1]
        df[feature] = (df[feature] - m) / std

    return df

def save_graphs(graphs, dataset='test_graphs'):
    saved_graph_folder = os.path.join(root_path, '%d_%d' % (duration, overlap), dataset)
    if not os.path.exists(saved_graph_folder):
        os.mkdir(saved_graph_folder)

    for app in graphs.keys():
        graph_app_folder = os.path.join(saved_graph_folder, app)
        if not os.path.exists(graph_app_folder):
            os.mkdir(graph_app_folder)

        features_df = graphs[app][0]
        weights_df = graphs[app][1]

        features_path = os.path.join(graph_app_folder, 'features.csv')
        weights_path = os.path.join(graph_app_folder, 'weights.csv')

        features_df.to_csv(features_path)
        weights_df.to_csv(weights_path)

if __name__ == "__main__":
    start_time = time.time()
    manager = Manager()
    training_graphs = manager.dict()
    testing_graphs = manager.dict()

    training_graphs = gene_graphs_multithreading(duration=duration,overlap=overlap,graphs=training_graphs,index=0,dataset_size=train_size)
    save_graphs(training_graphs, dataset='train_graphs_unnormalized')

    testing_graphs = gene_graphs_multithreading(duration=duration,overlap=overlap,graphs=testing_graphs,index=1,dataset_size=test_size)
    save_graphs(testing_graphs, dataset='test_graphs_unnormalized')

    # feature normalization
    cols = ['burst_idx'] + features + ['graph_id']
    df = pd.DataFrame([], columns=cols)

    # loop over train graphs
    for app in training_graphs.keys():
        df_ = training_graphs[app][0]  # weight_df
        df = pd.concat([df, df_], axis=0)

    # compute mean and std of all featurs in training set
    mean_std_dic = dict()
    for feature in df.columns:
        if feature not in ['burst_idx', 'protocol', 'dir', 'graph_id', 'stream_id', 'flow_start', 'flow_end',
                           'start_burst_idx',
                           'end_burst_idx', 'start', 'end', 'is_start', 'is_end', 'pk_list_in_burst']:  # 不需要归一化的特征
            mean_std_dic[feature] = (df[feature].mean(), df[feature].std())

    print('Standardization...')
    training_graph = {}
    testing_graph = {}

    for app in training_graphs.keys():
        training_graph[app] = [0,0]
        testing_graph[app] = [0,0]

        training_graph[app][0] = standardize_features(training_graphs[app][0], mean_std_dic)
        training_graph[app][1] = training_graphs[app][1]

        testing_graph[app][0] = standardize_features(testing_graphs[app][0], mean_std_dic)
        testing_graph[app][1] = testing_graphs[app][1]

    print('Saving...')
    #save_graphs(training_graphs, dataset='train_graphs_unnormalized')
    #save_graphs(testing_graphs, dataset='test_graphs_unnormalized')

    save_graphs(training_graph, dataset='train_graphs')
    save_graphs(testing_graph, dataset='test_graphs')
    
    end_time = time.time()
    print("Running Time：", (end_time - start_time)/3600, "mins")

