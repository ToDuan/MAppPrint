import uiautomator2 as u2
import time
import threading
import glob
import random
import os
import argparse
import json as js
from requests.exceptions import ReadTimeout
from collections import defaultdict
import subprocess
from engine import get_connections, start_pre, end_pre, run_adb_cmd
from adb_test import getuidByPackage
from executeBystr import *

#正常（normal）模式下采集的apk列表，需手动配置
NORMALPKGLIST = ['com.jingdong.app.mall','net.csdn.csdnplus',
               'com.tencent.qqlive','com.qiyi.video','com.hunantv.imgo.activity',
               'tv.danmaku.bili','com.autonavi.minimap','com.netease.cloudmusic',
               'com.xunmeng.pinduoduo',"com.ss.android.ugc.aweme","com.baidu.searchbox",
               'com.UCMobile','com.kmxs.reader', 'com.dragon.read',
                'com.smile.gifmaker', 'com.zhihu.android','com.sina.weibog3','com.taobao.taobao']
#多应用(multi)模式下采集的apk列表，分为前端应用和后台应用，需手动配置
FOREPKGLIST = ["com.baidu.searchbox","com.kmxs.reader", "net.csdn.csdnplus"] #前端应用
BACKPKGLIST = ['tv.danmaku.bili',"com.tencent.qqlive",'com.netease.cloudmusic'] #后台应用
#细粒度动作(activity)模式下采集的apk列表，需手动配置
ACKPKGLIST = ['com.taobao.taobao','com.jingdong.app.mall', 'com.tencent.mm', 'com.tencent.mobileqq']
def normal_execute(arginfo):
    #完成一个apk相关模式['normal', 'fore', 'back']的一次流量采集
    d = arginfo['d']
    package = arginfo['package']
    goaltime = arginfo['goaltime']
    device = arginfo['device']
    mode = arginfo['mode']
    flow2uid_path = arginfo['flow2uid_path']
    #准备流量采集
    if mode in ['back', 'fore']:
        d.app_start(package)
        time.sleep(2)
    else:
        pcapProcess, filename= start_pre(package, arginfo['basecmd'], arginfo['host'], arginfo['device'], d, arginfo['net'])
    #执行apk动作，采集流量
    if arginfo['act_do'] == 0:
        globals()[package.replace('.','_')](mode, d, goaltime)
    else:
        globals()[package.replace('.','_')](mode, d, goaltime, arginfo['act_do'])
    
    #完成流量采集，处理流量
    if mode not in ['back', 'fore']:
        filename = end_pre(package, pcapProcess, filename, arginfo['device'], d, arginfo['traffic_path'])
    else:
        return None
    return None, filename

def normal_sniff(arginfo):
    for pkg in NORMALPKGLIST:
        while True:
            try:
                for m in range(arginfo['sample_num']):
                    if not  os.path.exists(arginfo['flow2uid_path']):
                        os.mkdir(arginfo['flow2uid_path'])
                    path = os.path.join(arginfo['flow2uid_path'],pkg)
                    if not os.path.exists(path):
                        os.mkdir(path)
                    if len(os.listdir(path)) > arginfo['sample_num']:
                        break
                    arginfo['package'] = pkg
                    arginfo['act_do'] = 0
                    #执行单次流量采集
                    _ ,filename = normal_execute(arginfo)
                    #解析networklog日志，保存为json格式
                    connections = get_connections(pkg)
                    with open(os.path.join(path,filename[:-5] + '_netlog.json'), 'w') as f:
                        f.write(js.dumps(connections))
                    time.sleep(2)
                break
            except ReadTimeout:
                continue

def multi_sniff(arginfo):
    for forepackage in FOREPKGLIST:
        for backpakage in BACKPKGLIST:
            while True:
                try: 
                    for m in range(arginfo['sample_num']):
                        path = os.path.join(arginfo['flow2uid_path'], forepackage + '_' + backpakage)
                        if not os.path.exists(path):
                            os.mkdir(path)
                        if len(os.listdir(path)) > arginfo['sample_num']:
                            break
                        filename =f'{forepackage}_{backpakage}_{str(time.time())}.pcap'
                        cmd = ['/data/tcpdump', 
        '-i', arginfo['net'],'-w', '/sdcard/' + filename, 'not','host',arginfo['host']]
                        local_cmd = arginfo['basecmd'] + cmd
                        #删除之前的日志文件
                        cmd = ['shell','rm', '-rf', 'sdcard/networklog.txt']
                        run_adb_cmd(cmd,arginfo['device'])
                        #启动后台应用
                        d = arginfo['d']
                        globals()[backpakage.replace('.','_')]('back', d, arginfo['goaltime'])
                        #启动日志记录
                        d.app_start("com.googlecode.networklog")
                        while True:
                            try:
                                if d(resourceId="com.googlecode.networklog:id/actionbar_service_toggle").exists:
                                    time.sleep(2)
                                    d.press('home')
                                    break
                            except:
                                continue
                        #启动抓包
                        pcapProcess = subprocess.Popen(local_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        #启动前端应用，执行前端应用动作
                        globals()[backpakage.replace('.','_')]('fore', d, arginfo['goaltime'])
                        #关闭前后端应用
                        d.app_stop(forepackage)
                        d.app_stop(backpakage)
                        #等待抓包结束
                        pcapProcess.wait()
                        #结束日志
                        d.app_stop("com.googlecode.networklog")
                        #保存流量
                        storepath = os.path.join(arginfo['traffic_path'], forepackage+ '_' + backpakage)
                        if not os.path.exists(storepath):
                            os.makedirs(storepath, exist_ok=True)
                        pcapPath = os.path.join(storepath,filename)
                        cmd = ['pull', '/sdcard/'+filename, pcapPath]
                        run_adb_cmd(cmd, arginfo['device'])
                        cmd = ['shell','rm','-rf','/sdcard/'+filename]
                        run_adb_cmd(cmd, arginfo['device'])
                        #获取日志文件
                        cmd = ['pull', '/sdcard/networklog.txt', './networklog.txt']
                        run_adb_cmd(cmd, arginfo['device'])
                        #处理日志文件
                        uidic = {int(getuidByPackage(forepackage,arginfo['device'])):forepackage, int(getuidByPackage(backpakage,arginfo['device'])):backpakage}
                        connections = defaultdict(list)
                        with open('./networklog.txt', 'r') as f:
                            for line in f:
                                line = line.replace(',,', ',')
                                socketinfo = line.split(',')
                                uid = int(socketinfo[2])
                                if uid not in uidic.keys():
                                    continue
                                uid = uidic[uid]
                                src = socketinfo[3] +':' + socketinfo[4]
                                dst = socketinfo[5] +':' + socketinfo[6]
                                if src > dst:
                                    src, dst = dst, src
                                proto = socketinfo[-1].strip()
                                conn = (src,dst,proto)
                                connections[uid].append(conn)
                            for key in connections.keys():
                                connections[key] = list(set(connections[key]))
                            connections = dict(connections)
                        with open(os.path.join(path,filename[:-5] + '_netlog' + '.json'), 'w') as f:
                            f.write(js.dumps(connections))
                        time.sleep(2)
                    break
                except ReadTimeout:
                    continue
            
def act_sniff(arginfo):
    for pkg in ACKPKGLIST:
        for act_do in range(1,8):
            #act_do表示某个app的细粒度动作，本代码提供的动作最少为8个
            while True:
                try:
                    for m in range(arginfo['sample_num']):
                    
                        flow2uid = defaultdict(list)
                     
                        path = os.path.join(arginfo['flow2uid_path'], pkg)
                        if not os.path.exists(path):
                            os.mkdir(path)
                        path = os.path.join(path, str(act_do))
                        if not os.path.exists(path):
                            os.mkdir(path)
                        
                        if len(os.listdir(path)) >= arginfo['sample_num']:
                            break
                        arginfo['mode'] = 'normal'
                        arginfo['act_do'] = act_do
                        _ ,filename = normal_execute(arginfo)
                        connections = get_connections(pkg)
                        with open(os.path.join(path,filename[:-5] + '_netlog.json'), 'w') as f:
                            f.write(js.dumps(connections))
                        time.sleep(2)

                    break
                except ReadTimeout:
                    continue
def main(args):
    #主函数，不同功能采集函数入口
    arginfo = {}
    device = args.device
    arginfo['device'] = device
    arginfo['d'] = u2.connect(device)
    arginfo['goaltime'] = args.goaltime
    arginfo['traffic_path'] = args.traffic_path
    arginfo['flow2uid_path'] = args.flow2uid_path
    arginfo['host'] = args.host
    arginfo['basecmd'] = ['adb','-s', device, 'shell', 'su','-c','timeout', args.goaltime]
    arginfo['net'] = args.net
    arginfo['sample_num'] = args.sample_num
    if args.func == 'normal':
        normal_sniff(arginfo)
    elif args.func == 'multi':
        multi_sniff(arginfo)
    elif args.func == 'activity':
        act_sniff(arginfo)
    else:
        return False
    return True
def get_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help="The IP of the host where the program is running, which is filtered when collecting traffic")
    parser.add_argument('--device', type=str, default="sn_XXX",
                        help="adb device name  you want to install apks, you can get it by running command:'adb device'")
    parser.add_argument('--goaltime', type=int, default=300, 
                        help='Duration of one traffic trace')
    parser.add_argument('--traffic_path', type=str, default=r'./traffic',
                        help='The path you want to store the traffic')
    parser.add_argument('--flow2uid_path', type=str, default=r'./flow2uidJson',
                        help="The path you want to store the log json files of traffic")
    parser.add_argument('--func', type=str, choices=['normal', 'multi', 'activity'],default='normal',
                        help="Select the flow collection function to access the different collection functions")
    parser.add_argument('--net', type=str, default="wlan0", 
                        help="Name of the network to which the phone is connected")
    parser.add_argument('--sample_num', type=int, default=30,
                        help="Number of times a single apk is captured")
    return parser
if __name__ == "__main__":
    device = "deviceIP:port"
    device = "device_sn"
    args = get_parser().parse_args()
    
    main(args)
