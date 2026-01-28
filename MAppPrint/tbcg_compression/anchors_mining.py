
import numpy as np
import os
from prefixspan import PrefixSpan
import pandas as pd
pd.options.mode.chained_assignment = None
from multiprocessing import Process,Manager
import time

def app_burst_fp_mining(root_dir,app,Bst_FP):

    print("1) Loading......")
    path = os.path.join(root_dir,app,'features.csv')
    features_df = pd.read_csv(path,index_col=0)

    num_graph = features_df.graph_id.max()
    num_burst = features_df.shape[0]
    features_df = features_df.iloc[:,[2,3,-3]]

    # burst sequence
    for i in range(features_df.shape[0]):
        if features_df.iloc[i].dir == 1:
            features_df['pk_list_in_burst'].iloc[i] = eval(features_df['pk_list_in_burst'].iloc[i])
        else:
            features_df['pk_list_in_burst'].iloc[i] = [-k for k in eval(features_df['pk_list_in_burst'].iloc[i])]

    shot_bursts = features_df[features_df.length <= 3]
    long_bursts = features_df[features_df.length > 3]
    
    if long_bursts.shape[0] == 0 : long_burst_length_mean = 0 # no long burst
    else:
        long_burst_length_mean = int(long_bursts.length.mean())
    
    seq_min = int(np.percentile(long_bursts.length,10))
    seq_max = min(long_burst_length_mean,np.percentile(long_bursts.length,90))

    shot_bursts = shot_bursts['pk_list_in_burst'].to_list()
    long_bursts = long_bursts['pk_list_in_burst'].to_list()

    # long behaviors frequent sub-sequences
    print("2) Long Behaviors Processing......")
    num_long_bursts = len(long_bursts)
    per_long = num_long_bursts/num_burst
    model = PrefixSpan(long_bursts)
    top_subburst = model.topk(100)
    top_subburst = [(round(n/num_long_bursts,3), len(seq),seq) for (n,seq) in top_subburst]
    top_subburst = pd.DataFrame(top_subburst)
    top_subburst.columns = ['confidence','length','sequence']
    top_subburst = top_subburst[(top_subburst.length >= seq_min) & (top_subburst.length <= seq_max)]
    top_subburst['set'] = ''
    for i in range(top_subburst.shape[0]):
        top_subburst.set.iloc[i] = str(set(top_subburst.sequence.iloc[i]))

    top_subburst = top_subburst.drop_duplicates(subset='set',keep='first')
    top_subburst['total_conf'] = top_subburst['confidence'] * per_long
    top_subburst = top_subburst.iloc[:,[0,1,2,4]]
    top_subburst['bst_type'] = 'long'

    # short behaviors frequent sequences
    print("3) Short Behaviors Processing......")
    num_short_bursts = len(shot_bursts)
    per_short = num_short_bursts/num_burst
    short_burst_fp = { }
    for bst in shot_bursts:
        bst = str(bst)
        if bst in short_burst_fp: short_burst_fp[bst] += 1
        else: short_burst_fp[bst] = 1

    short_burst_fp = sorted(short_burst_fp.items(), key=lambda item: item[1], reverse=True)
    short_burst_fp = pd.DataFrame(short_burst_fp)
    short_burst_fp.columns = ['sequence','confidence']
    short_burst_fp.confidence = round(short_burst_fp.confidence/num_short_bursts,3)
    short_burst_fp = short_burst_fp.iloc[:10] # top-10
    short_burst_fp['length'] = ''
    for i in range(short_burst_fp.shape[0]):
        short_burst_fp.sequence.iloc[i] = eval(short_burst_fp.sequence.iloc[i])
        short_burst_fp.length.iloc[i] = len(short_burst_fp.sequence.iloc[i])

    short_burst_fp['total_conf'] = short_burst_fp['confidence'] * per_short
    short_burst_fp = short_burst_fp.iloc[:,[1,2,0,3]]
    short_burst_fp['bst_type'] = 'short'

    # total
    burst_fp = pd.concat((short_burst_fp,top_subburst),axis=0)
    burst_fp['app'] = app

    Bst_FP[app] = burst_fp


def app_burst_fp_mining_multithreading(root_dir,Bst_FP):
    processes = []
    counter = 0
    app_dir = os.listdir(root_dir)

    for app in app_dir:
        counter += 1
        print("Processing....{}: {}/{}".format(app, counter, len(app_dir)))

        # sub-process
        proc = Process(target=app_burst_fp_mining, args=(root_dir, app, Bst_FP,))
        processes.append(proc)
        proc.start()

    for proc in processes:
        proc.join()

    return Bst_FP

def save_burst_pf(burst_pf_dict,save_path):
    Burst_PFs = pd.DataFrame()

    for  app,bst_pfs in burst_pf_dict.items():
        Burst_PFs = pd.concat((Burst_PFs,bst_pfs),axis=0)

    Burst_PFs.to_csv(save_path, index=False)

if __name__ == "__main__":
    
    time_win = '5'

    root_dir = '../Datasets/TBCGs/FOAP/{}/train_graphs/'.format(time_win)
    save_path = '../Datasets/TBCGs/FOAP/{}/burst_pf.csv'.format(time_win)

    start_time = time.time()
    manager = Manager()
    Total_Bst_FP = manager.dict()
    Total_Bst_FP = app_burst_fp_mining_multithreading(root_dir=root_dir,Bst_FP=Total_Bst_FP)
    save_burst_pf(Total_Bst_FP,save_path)

    end_time = time.time()
    print("Running Time：", (end_time - start_time)/60, "mins")


