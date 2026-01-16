
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_circles
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_blobs
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import json
import time

path_dir = './Datasets/MAMF/30_15/cr=0.5/test_graphs'
multiApp = os.listdir(path_dir)

multiapp2labeldict_path = './Datasets/MAMF/30_15/cr=0.5/LabelSpaceDict.json'
with open(multiapp2labeldict_path, 'r') as f:
    multiApp2label = json.load(f)

Graphs_seprated_info = { }
num_graph_app = {}
Time = []
for apps in multiApp:
    print("process apps: ",apps)
    file_names = os.path.join(path_dir,apps,'flow_features.csv')
    flows_app = pd.read_csv(file_names)
    num_graph_app[apps] = 0

    graph_ids = set(flows_app.graph_id)
    graph_info = {}
    for graph_id in graph_ids: #each graph
        if graph_id > num_graph_app[apps]: num_graph_app[apps] = graph_id
        graph_info[graph_id] = []

        flow_graph = flows_app[flows_app.graph_id == graph_id]
        flow_graph = flow_graph[flow_graph.total_num_pcks >= 5]
        y_true = flow_graph['app']
        flow_ids = np.array(flow_graph['flow_id'])

        flow_graph = flow_graph[['total_num_pcks','total_length','num_interaction',
                      'up_length','num_up_pcks','up_pck_pre','up_byte_pre','up_length_mean',
                      'down_length','num_down_pcks','down_pck_pre','down_byte_pre','down_length_mean']]

        flow_graph = np.array(flow_graph)
        flow_graph = StandardScaler().fit_transform(flow_graph)

        start_event = time.time() * 1000
        # DBSCAN
        dbscan = DBSCAN(eps=0.5, min_samples=1)
        y_dbscan = dbscan.fit_predict(flow_graph)
        pred_cats = set(y_dbscan)

        end_event = time.time() * 1000
        elapsed_time = (end_event - start_event) / 1000.0
        if elapsed_time != 0:
            Time.append(elapsed_time)

        #K-means
        # k = 50 if flow_graph.shape[0]>=50 else flow_graph.shape[0]
        # kmeans = KMeans(n_clusters=k)
        # kmeans.fit(flow_graph)
        # y_kmeans = kmeans.labels_
        # pred_cats = set(y_kmeans)

        for cat in pred_cats:
            sprated_flowID = flow_ids[y_dbscan==cat].tolist()
            graph_info[graph_id].append(sprated_flowID)

    Graphs_seprated_info[apps] = graph_info

# separate multi-app TBCG
for apps in multiApp:
    print("Seprate apps: ",apps)
    raw_features = pd.read_csv(os.path.join(path_dir,apps,'features.csv'),index_col=0)
    raw_edges = pd.read_csv(os.path.join(path_dir, apps, 'weights.csv'),index_col=0)

    New_all_features = pd.DataFrame()
    New_all_edges = pd.DataFrame()

    graph_ids = list(Graphs_seprated_info[apps].keys())
    apps_idx = multiApp2label[apps]

    for g_id in graph_ids: # each graph
        features = raw_features[raw_features.graph_id==g_id]
        edges = raw_edges[raw_edges.graph_id==g_id]

        flow_groups = Graphs_seprated_info[apps][g_id]

        for i in range(len(flow_groups)): # each seprated sub-graph
            flow_ids = flow_groups[i]
            new_graph_features = pd.DataFrame()

            for f_id in flow_ids: # flows in a sub-graph
                df = features[features.stream_id==f_id]
                new_graph_features = pd.concat((new_graph_features,df),axis=0)

            new_graph_features['graph_id'] = apps_idx*10000 + new_graph_features['graph_id']*100 + i

            burst_idxs = set(new_graph_features.burst_idx)
            new_edges = edges[(edges.source.isin(burst_idxs))&(edges.target.isin(burst_idxs))]
            new_edges['graph_id'] = apps_idx*10000 + new_edges['graph_id']*100 + i

            New_all_features = pd.concat((New_all_features,new_graph_features),axis=0)
            New_all_edges =  pd.concat((New_all_edges,new_edges),axis=0)

    New_all_features.to_csv(os.path.join(path_dir,apps,'separated_TBCGs_features.csv'),index=False)
    New_all_edges.to_csv(os.path.join(path_dir,apps,'separated_TBCGs_weights.csv'),index=False)











































