import time
import subprocess
import os
from adb_test import getuidByPackage
from collections import defaultdict
import json as js
"""
引擎工具，为各apk动作执行提供核心运行函数
"""

def run_adb_cmd(cmd, device):
    args = ['adb', '-s', device]
    args.extend(cmd)
    ret = None
    # 运行adb命令
    adbProcess = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = adbProcess.communicate()
        
    return ret  

#统一启动函数，处理流量捕获开始时的准备操作
def start_pre(package, basecmd, host , device, d, net='wlan0', act=None):
    #初始化抓包命令
    filename =f'{package}_{str(time.time())}.pcap'
    local_cmd = basecmd
    cmd = ['/data/tcpdump', 
    '-i', net,'-w', '/sdcard/' + filename, 'not','host',host]
    local_cmd = basecmd + cmd
    """
    cmd = ['adb', 'shell', 'su','-c','timeout 60','/data/tcpdump', 
    '-i', 'rmnet_data1','-w', '/sdcard/' + filename, 'not','host',host]
    """
    #删除旧日志文件
    cmd = ['shell','rm', '-rf', 'sdcard/networklog.txt']
    run_adb_cmd(cmd, device)
    d.app_start("com.googlecode.networklog")
    #开启networklog，监听记录流量日志
    while True:
        try:
            if d(resourceId="com.googlecode.networklog:id/actionbar_service_toggle").exists:
                time.sleep(2)
                d.press('home')
                break
        except:
            continue
    #启动tcpdump，捕获流量数据
    pcapProcess = subprocess.Popen(local_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #启动目标app，完成app相关动作以抓取对应流量
    if act is not None:
        d.app_start(package, act)
    else:
        d.app_start(package)
    d.implicitly_wait(10)
    return pcapProcess, filename

#统一终止函数，处理流量采集结束后的相关操作
def end_pre(package,pcapProcess,filename, device, d, traffic_path, act_do = 0):

    #清除列表，部分app无需保留登录信息，需要清空数据
    clearlist = ["com.hunantv.imgo.activity", "com.taobao.taobao"]
    d.app_stop(package)
    if package in clearlist:
        d.app_clear(package)
    pcapProcess.wait()
    d.app_stop("com.googlecode.networklog")
    if not os.path.exists(traffic_path):
        os.mkdir(traffic_path)
    storePath = os.path.join(traffic_path
                            ,package)
    if not os.path.exists(storePath):
        os.mkdir(storePath)
    if act_do == 0:
        tempname = filename
    else:
        storePath = os.path.join(storePath
                            ,act_do)
        if not os.path.exists(storePath):
            os.mkdir(storePath)
        tempname = filename[:-5] + '_' + act_do + '.pcap'
    #将pcap文件复制到pc端
    cmd = ['pull', '/sdcard/'+filename, os.path.join(storePath, tempname)]
    run_adb_cmd(cmd, device)
    # 将手机内，本次触发得到的Pcap文件删除
    cmd = ['shell','rm','-rf','/sdcard/'+filename]
    run_adb_cmd(cmd, device)
    return filename
def get_connections(package, device):
    #获取并解析流量日志文件，将五元组信息与包名关联
    cmd = ['pull', '/sdcard/networklog.txt', './networklog.txt']
    run_adb_cmd(cmd, device)
    
    #构建uid 到apk包名的字典
    uidic = {int(getuidByPackage(package,device)):package}
    #处理日志文件
    connections = defaultdict(list)
    with open('./networklog.txt', 'r') as f:
        for line in f:
            line = line.replace(',,', ',')
            socketinfo = line.split(',')
            uid = int(socketinfo[2])
            if uid not in uidic.keys():
                continue
            #保存socket与包名的对应关系
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
    return connections