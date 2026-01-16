
import os
import matplotlib.pyplot as plt
import random
import pandas as pd
import numpy as np
from scipy.stats import chisquare
# from spot import *
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from scipy.stats import entropy

epoch = 400
corr_ration = 0.4
corr_ration = "{}cr".format(corr_ration)

output_info_dir = ''
trainset_info_path = os.path.join(output_info_dir,'Trainset_one-class-learner_singleApp_epoch={}_crr={}.csv'.format(epoch,corr_ration))

singleApp_info_path = os.path.join(output_info_dir,'Testset_one-class-learner_singleApp_epoch={}_crr={}.csv'.format(epoch,corr_ration))
multiApp_info_path = os.path.join(output_info_dir,'one-class-learner_multiApp_epoch={}_crr={}.csv'.format(epoch,corr_ration))
Trainset_info = pd.read_csv(trainset_info_path)

singleApp_info = pd.read_csv(singleApp_info_path)
multiApp_info = pd.read_csv(multiApp_info_path)

Trainset_info = Trainset_info[Trainset_info.predicted != 'None']

Trainset_info = Trainset_info[['com.autonavi.minimap', 'com.netease.cloudmusic', 'com.kmxs.reader',
       'com.dragon.read', 'com.hunantv.imgo.activity', 'com.xunmeng.pinduoduo',
       'tv.danmaku.bili', 'com.ss.android.ugc.aweme', 'net.csdn.csdnplus',
       'com.sina.weibog3', 'com.smile.gifmaker', 'com.taobao.taobao',
       'com.UCMobile', 'com.tencent.qqlive', 'com.baidu.searchbox',
       'com.jingdong.app.mall', 'com.zhihu.android', 'com.qiyi.video']]

singleApp_info = singleApp_info[['com.autonavi.minimap', 'com.netease.cloudmusic', 'com.kmxs.reader',
       'com.dragon.read', 'com.hunantv.imgo.activity', 'com.xunmeng.pinduoduo',
       'tv.danmaku.bili', 'com.ss.android.ugc.aweme', 'net.csdn.csdnplus',
       'com.sina.weibog3', 'com.smile.gifmaker', 'com.taobao.taobao',
       'com.UCMobile', 'com.tencent.qqlive', 'com.baidu.searchbox',
       'com.jingdong.app.mall', 'com.zhihu.android', 'com.qiyi.video']]
singleApp_info['label'] = 0

multiApp_info = multiApp_info[['com.autonavi.minimap', 'com.netease.cloudmusic', 'com.kmxs.reader',
       'com.dragon.read', 'com.hunantv.imgo.activity', 'com.xunmeng.pinduoduo',
       'tv.danmaku.bili', 'com.ss.android.ugc.aweme', 'net.csdn.csdnplus',
       'com.sina.weibog3', 'com.smile.gifmaker', 'com.taobao.taobao',
       'com.UCMobile', 'com.tencent.qqlive', 'com.baidu.searchbox',
       'com.jingdong.app.mall', 'com.zhihu.android', 'com.qiyi.video']]
multiApp_info['label'] = 1

all_sample_info = pd.concat((singleApp_info,multiApp_info),axis=0)
all_sample_info = all_sample_info.reset_index()

class KLDivergence:
    def __init__(self, eps=1e-10):
        self.eps = eps
    def kl_divergence(self, p, q):

        p = np.asarray(p, dtype=np.float)
        q = np.asarray(q, dtype=np.float)

        p = p/np.sum(p)
        q = q/np.sum(q)

        q = np.clip(q, self.eps, 1 - self.eps)

        kl_div = entropy(p,q)
        return kl_div


all_Trainset_CataInfo = Trainset_info
all_sample_CateInfo = all_sample_info

def raw_confidence_sort(conf_list):

    conf_list = sorted(conf_list)
    conf_list = [
                 conf_list[0], conf_list[2], conf_list[4],conf_list[6],conf_list[8],conf_list[10],conf_list[12],
        conf_list[14],conf_list[16],

        conf_list[17],conf_list[15], conf_list[13],conf_list[11],conf_list[9],conf_list[7], conf_list[5], conf_list[3], conf_list[1],
                 ]
    return conf_list

Trainset_confidence = all_Trainset_CataInfo
Trainset_conf_info = pd.DataFrame()
for i in range(Trainset_confidence.shape[0]):
    conf = Trainset_confidence.iloc[i].to_list()
    conf = raw_confidence_sort(conf)

    Trainset_conf_info = pd.concat((Trainset_conf_info,pd.DataFrame(conf).T),axis=0)

single_confidence = all_sample_CateInfo[all_sample_CateInfo.label==0]
single_confidence = single_confidence[['com.autonavi.minimap', 'com.netease.cloudmusic',
       'com.kmxs.reader', 'com.dragon.read', 'com.hunantv.imgo.activity',
       'com.xunmeng.pinduoduo', 'tv.danmaku.bili', 'com.ss.android.ugc.aweme',
       'net.csdn.csdnplus', 'com.sina.weibog3', 'com.smile.gifmaker',
       'com.taobao.taobao', 'com.UCMobile', 'com.tencent.qqlive',
       'com.baidu.searchbox', 'com.jingdong.app.mall', 'com.zhihu.android',
       'com.qiyi.video']]
single_conf_info = pd.DataFrame()
for i in range(single_confidence.shape[0]):
    conf = single_confidence.iloc[i].to_list()
    conf = raw_confidence_sort(conf)

    single_conf_info = pd.concat((single_conf_info,pd.DataFrame(conf).T),axis=0)

multi_confidence = all_sample_CateInfo[all_sample_CateInfo.label==1]
multi_confidence = multi_confidence[['com.autonavi.minimap', 'com.netease.cloudmusic',
       'com.kmxs.reader', 'com.dragon.read', 'com.hunantv.imgo.activity',
       'com.xunmeng.pinduoduo', 'tv.danmaku.bili', 'com.ss.android.ugc.aweme',
       'net.csdn.csdnplus', 'com.sina.weibog3', 'com.smile.gifmaker',
       'com.taobao.taobao', 'com.UCMobile', 'com.tencent.qqlive',
       'com.baidu.searchbox', 'com.jingdong.app.mall', 'com.zhihu.android',
       'com.qiyi.video']]
multi_conf_info = pd.DataFrame()
for i in range(multi_confidence.shape[0]):
    conf = multi_confidence.iloc[i].to_list()
    conf = raw_confidence_sort(conf)

    multi_conf_info = pd.concat((multi_conf_info,pd.DataFrame(conf).T),axis=0)

mean_single_conf_dist = round(single_conf_info.mean(),3).to_list()
mean_multi_conf_dist = round(multi_conf_info.mean(),3).to_list()

labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
         '11', '12', '13', '14', '15','16', '17', '18']


rand_add1 = np.array([random.uniform(0, 0.000001) for i in range(18)])
rand_add2 = np.array([random.uniform(0, 0.000001) for i in range(18)])
mean_single_conf_dist = ([0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0]+rand_add1).tolist()

# KLD = KLDivergence()
indicator = [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0]

Trainset_K2_Dist = []
for i in range(Trainset_conf_info.shape[0]):
    con_dis = (Trainset_conf_info.values[i]+rand_add2).tolist()
    k2d,_ = chisquare(mean_single_conf_dist, con_dis)

    # con_dis = Trainset_conf_info.values[i].tolist()
    # kld = KLD.kl_divergence(con_dis,indicator)

    Trainset_K2_Dist.append(k2d)

single_K2_Dist = []
for i in range(single_conf_info.shape[0]):
    con_dis = (single_conf_info.values[i]+rand_add2).tolist()
    k2d,_ = chisquare(mean_single_conf_dist, con_dis)

    # con_dis = single_conf_info.values[i].tolist()
    # kld = KLD.kl_divergence(con_dis,indicator)

    single_K2_Dist.append(k2d)

multi_K2_Dist = []
for i in range(multi_conf_info.shape[0]):
    con_dis = (multi_conf_info.values[i]+rand_add2).tolist()
    k2d,_ = chisquare(mean_single_conf_dist, con_dis)

    # con_dis = multi_conf_info.values[i].tolist()
    # kld = KLD.kl_divergence(con_dis,indicator)

    multi_K2_Dist.append(k2d)

Total_K2_Dist = single_K2_Dist + multi_K2_Dist

# 3 /delt
discrim_bar = (np.array(Trainset_K2_Dist)).mean() + 3*(np.array(Trainset_K2_Dist)).std()
singleApp_discover_acc = (np.array(single_K2_Dist)<=discrim_bar).sum()/len(single_K2_Dist)
multiApp_discover_acc = (np.array(multi_K2_Dist)>discrim_bar).sum()/len(multi_K2_Dist)

TP = (np.array(single_K2_Dist)<=discrim_bar).sum()
FN = len(single_K2_Dist) - TP

TN = (np.array(multi_K2_Dist)>discrim_bar).sum()
FP = len(multi_K2_Dist) - TN

single_TPR = TP/len(single_K2_Dist)
single_FNR = FN/len(single_K2_Dist)

multi_TPR = TN/len(multi_K2_Dist)
multi_FNR = FP/len(multi_K2_Dist)

label = [0]*len(single_K2_Dist) + [1]*len(multi_K2_Dist)
pre = [0]*TP+[1]*FN+[1]*TN+[0]*FP
print("corr_per= ",corr_ration)
print("Num Single-App={};\tNum Multi-App={}".format(len(single_K2_Dist),len(multi_K2_Dist)))
print("Detail Result: ")
print("Single-App:\tTPR={}\tFNR={}".format(single_TPR,single_FNR))
print("Multi-App:\tTPR={}\tFNR={}".format(multi_TPR,multi_FNR))

print("Total Result: ")
print(classification_report(label,pre,digits=4))

print("Just Acc: ")
print("Single-Acc={}\tMulti-Acc={}".format(singleApp_discover_acc,multiApp_discover_acc))

pred = [ ]
for k2d in Total_K2_Dist:
    if k2d <= discrim_bar:
        pred.append(0) #single
    else:
        pred.append(1) #multi

multiApp_info = pd.read_csv(multiApp_info_path)
multiApp_info_single = multiApp_info[multiApp_info.predicted_list == 'single']

count = 0
for i in range(multiApp_info_single.shape[0]):
    if multiApp_info_single.iloc[i].predicted in multiApp_info_single.iloc[i].label:
        count += 1
multiApp_discover2single_acc_inall = count/len(multi_K2_Dist)
multiApp_discover2single_acc_wrong = count/FP
print("Discover one true App in FP: ")
print("Acc_in_all={}\tAcc_in_FP={}".format(multiApp_discover2single_acc_inall,multiApp_discover2single_acc_wrong))