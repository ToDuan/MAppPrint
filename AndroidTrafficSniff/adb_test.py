import subprocess
from matplotlib import pyplot as pt
import numpy as np
import json
import codecs
import random
import time
import uiautomator2 as u2
import threading
import os
from tqdm import tqdm
import logging
import signal
from sniffutils import *
def run_adb_cmd(cmd):
    args = ['adb']
    args.extend(cmd)
    ret = None
    # 运行adb命令
    adbProcess = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = adbProcess.communicate()
    return ret
def getPackgeByuid(uid='2000'):
    #uid = "2000"  # 替换为你要查询的应用程序的UID

    # 使用ADB命令获取应用列表
    command = ['adb', 'shell', 'cmd', 'package', 'list', 'packages', '-U']
    output = subprocess.check_output(command).decode("utf-8")

    # 在输出中查找包含指定UID的行
    uid_line = next(line for line in output.splitlines() if uid in line)

    # 提取包名
    package_name = uid_line.split(' ')[0].split(":")[1].strip()

    print("UID {} 对应的应用程序包名为: {}".format(uid, package_name))
def getuidByPackage(packagename, device):
     # 替换为你要查询的应用程序的包名

    # 使用ADB命令获取应用UID
    command = ['adb', '-s', device,'shell', 'dumpsys', 'package', packagename]
    output = subprocess.check_output(command).decode("utf-8")

    # 在输出中查找包含UID的行
    uid_line = next(line for line in output.splitlines() if "userId=" in line)

    # 提取UID值
    uid = uid_line.split("=")[-1]

    #print("应用程序 {} 的UID为: {}".format(packagename, uid))
    return uid
def getuidByflow(flow, device, output=None, flowid=0):
    source_ip = flow[0]  # 替换为实际的流的源IP
    destination_ip = flow[2]  # 替换为实际的流的目标IP
    source_port = flow[1] # 替换为实际的流的源端口
    destination_port = flow[3]  # 替换为实际的流的目标端口
    src = convert_ip_port(ip=source_ip,port=source_port)
    dst = convert_ip_port(ip=destination_ip,port=destination_port)
    # 使用ADB命令获取流对应的UID
    command1 = ['adb','-s', device, 'shell', 'cat', '/proc/net/tcp']
    command2 = ['adb', '-s', device, 'shell', 'cat', '/proc/net/udp']
    if output == None:
        if flowid == 0:
            #tcp_flow
            output = subprocess.check_output(command1).decode("utf-8")
        else:
            #udp_flow
            output = subprocess.check_output(command2).decode("utf-8")    
    # 在输出中查找匹配的流信息
    flow_info = next(line for line in output.splitlines() if all(text in line for text in [src, dst]))

    # 提取UID值
    uid = flow_info.split()[7]

    #print("流 {}:{} -> {}:{} 对应的UID为: {}".format(source_ip, source_port, destination_ip, destination_port, uid))
    return uid, output
def getflowByuid(uid, device):
    # 使用ADB命令获取流对应的UID
    command1 = ['adb','-s', device, 'shell', 'cat', '/proc/net/tcp']
    command2 = ['adb', '-s', device, 'shell', 'cat', '/proc/net/udp']
  
    #tcp_flow
    connection = []
    output = subprocess.check_output(command1).decode("utf-8")
    # 提取UID值
    try:
        flow_lines = [line for line in output.splitlines() if all(text in line for text in [uid])]
    except:
        flow_lines = None
    if flow_lines != None:
        for flow_line in flow_lines:
            local_address, rem_address= flow_line.split()[1:3]    
            flowinfo = (local_address,rem_address,'tcp')
            connection.append(flowinfo)
    #udp_flow
    output = subprocess.check_output(command2).decode("utf-8")    
    # 在输出中查找匹配的流信息
    # 提取UID值
    try:
        flow_lines = [line for line in output.splitlines() if all(text in line for text in [uid])]
    except:
        flow_lines = None
    if flow_lines != None:
        for flow_line in flow_lines:
            local_address, rem_address= flow_line.split()[1:3]    
            flowinfo = (local_address,rem_address,'udp')
            connection.append(flowinfo)
    return connection
    

    

    #print("流 {}:{} -> {}:{} 对应的UID为: {}".format(source_ip, source_port, destination_ip, destination_port, uid))
    return uid, output

def getpackageslist():
    cmd = ['adb','shell','pm','list','packages']
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = p.communicate()
    ret = [line for line in ret[0].splitlines()]
    """
    for line in ret:
        print(line)
        """
    return ret
def handle_traffic():
    print("采集流量中")
    global filename
    sniffcmd = ['adb', 'shell', f'su -c data/tcpdump -i wlan0 -G 62 -W 1 -w /sdcard/{packageName}_{str(time.time())}.pcap']
    cmd = 'adb shell su -c data/tcpdump -i wlan0 -G 62 -W 1 -w ' + '/sdcard/' + filename
    os.system(cmd)
    #sniff = subprocess.Popen(sniffcmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #res = sniff.communicate()
    print("采集完毕")
    return 0

def preparAnalyzeAPK(filename):
    #记录pcap文件,忽略host是10.0.2.2的数据包
    cmd = ['adb', 'shell', 'su','-c','tcpdump', '-w', '/data/local/tmp/' + filename, '-s', str(0), '-vvv']
    pcapProcess = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pcapProcess
#关闭飞行模式，打开数据开关，输入为ControlThread类本身，无输出
def closeAirPlaneMode():
    cmd = ['shell', 'settings', 'put', 'global', 'airplane_mode_on', '0']
    run_adb_cmd(cmd)
    cmd = ['shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'false']
    run_adb_cmd(cmd)
    cmd = ['shell', 'svc', 'data', 'enable']
    run_adb_cmd(cmd)

#打开apk，输入为ControlThread类本身，无输出
def openApk(packageName):
    app_info = d.app_info('应用包名')
    main_activity = app_info['mainActivity']
    startStr = '%s/%s' % (packageName, main_activity)
    cmd = ['shell', 'am', 'start', '-n', startStr]
    run_adb_cmd(cmd)
    log.info("open apk")
    time.sleep(5)

    #分析apk，输入为ControlThread类本身，无输出
def analyzeApk(packageName):
    print('------ start ------')
    log.info("start analyze apk")
    # 模拟用户交互
    # cmd = ['python','UITree3.py', self.emuClient.emuName , self.apk.path, self.apk.pkg, self.apk.startStr]
    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # p.communicate()
    monkey(packageName)
    print('------- end -------')


#对monkey命令调参，输入为ControlThread类本身，无输出
def monkey(packageName):
    time.sleep(5)
    cmd = ['shell', 'monkey', '-p', packageName, '-s', '600', '--pct-touch', '20', '2000', '--pct-motion', '20','2000', '--pct-trackball', '10', '2000', '--pct-appswitch', '50', '2000', '--ignore-crashes', '--ignore-security-exceptions', '--kill-process-after-error' '-v', '2000']
    run_adb_cmd(cmd)


#关闭apk，输入为ControlThread类本身，无输出
def closeApk(packageName):
    cmd = ['shell', 'am', 'force-stop', packageName]
    run_adb_cmd(cmd)
#         print "close Apk"
    log.info("close apk")

#卸载apk，输入为ControlThread类本身，无输出
def uninstallApk(packageName):
    # cmd = ['uninstall', self.apk.pkg]
    cmd = ['uninstall', packageName]
    run_adb_cmd(cmd)
#         print "uninstall Apk"
    log.info("uninstall apk")
def convert_ip_port(ip, port):
    # Convert IP address to hex and reverse byte order
    ip_hex = ''.join(format(int(x), '02x') for x in ip.split('.')[::-1])
    
    # Convert port to hex and reverse byte order
    port_hex = format(port, '04x')[2:] + format(port, '04x')[:2]
    
    # Combine reversed IP address and port with a colon separator
    result = ip_hex.upper() + ':' + port_hex.upper()
    
    return result
#完成分析，输入为ControlThread类本身，无输出
def finishAnalyzeApk(self):
    # 结束logcat记录进程和pcap捕捉进程
    try:
        os.kill(self.pcapProcess.pid, signal.SIGKILL)
    except OSError as ex:
        pass
    #将pcap保存进APKLog的对应路径下
    cmd = ['aapt', 'dump', 'badging', self.apk.path]
    ret = None
    adbProcess = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = adbProcess.communicate()
    retlist = ret[0].splitlines()
    for line in ret[0].splitlines():
        if 'application: label' in line:
            self.apkName = line.split("'")[1]
    pcapPath = os.path.join(self.apkLogFolder, self.apk.name + '_' + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + '.pcap')
    cmd = ['pull', '/data/local/tmp/netdata.pcap', pcapPath]
    #cmd = ['pull', '/data/local/tmp/netdata.pcap', self.apkLogFolder]
    self.run_adb_cmd(cmd)
    #删除分析完的apk
    #os.remove(self.apk.path)
    apkPath = os.path.join(self.apkLogFolder, self.apk.name + '.apk')
    #成功分析完成,将bugNum置为0
    self.bugNum = 0
    self.isInstallSuccess = False
    print ("%s analyze finish %s" % (self.emuClient.avdName, self.apkName))
    self.log.info("[%s]analyze finish %s[cost %d]" % (self.getFormatTime(), os.path.basename(self.apk.path), time.time()-self.startTime))
    self.apk = None

    self.analyzeTimes = self.analyzeTimes + 1
    if self.analyzeTimes >= 20:
        self.needStart = True
        self.telnetShutDown()
        self.analyzeTimes = 0
def install_apk(apkpath):
    isInstallSuccess = False
    cmd = ['install', apkpath]
    ret = run_adb_cmd(cmd)
    retLines = ret[0].splitlines()
    if len(retLines) > 1:
        ret = retLines[1].decode('utf-8')
        if "FAILED" in ret:
            # 如果安装一次失败了，则再装一次试试
            ret = run_adb_cmd(cmd)
            retLines = ret[0].splitlines()
            if len(retLines) > 1:
                ret = retLines[1].decode('utf-8')
                if "FAILED" in ret:
                    isInstallSuccess = False
                else:
                    isInstallSuccess = True
            else:
                isInstallSuccess = False
        else:
            isInstallSuccess = True
    else:
        isInstallSuccess = False

    if isInstallSuccess == False:
        print("install failed")
    elif isInstallSuccess == True:
        print("install apk: " + apkpath)
    
    return isInstallSuccess
def domonkeyInapp(packageName, num = 100):
    #针对app执行num个随机指令，间隔时间为300ms
    global filename 
    monkeycmd = ['adb', 'shell', 'monkey', '-p', packageName, '--throttle 1000','--pct-syskeys 10', '-v', f'{num}']
    sniffcmd = ['adb', 'shell', f'su -c data/tcpdump -i wlan0 -G 62 -W 1 -w /sdcard/{packageName}_{str(time.time())}.pcap']
    filename = f'{packageName}_{str(time.time())}.pcap'
    #d = u2.connect() # 一个设备时
    start_time = time.time()
    #d.screen_on()
    time.sleep(1)
    sniff_th = threading.Thread(target=handle_traffic)
    sniff_th.start()
    print("执行monkey")
    time.sleep(1)
    while time.time() - start_time < 60:
        p = subprocess.Popen(monkeycmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()
    print("执行完毕")
    #d.app_stop(packageName)
    time.sleep(1)
    sniff_th.join()
    cmd = 'adb pull ' + '/sdcard/' + filename + f' ./traffic/{filename}'
    #os.system(cmd)
    #d.pull('/sdcard/'+ filename, f'./traffic/{filename}')
    """
    time.sleep(2)
    d.shell('rm {}'.format('/sdcard/'+ filename))
    """
    time.sleep(2)
def uninstallApk(packageName):
    # cmd = ['uninstall', self.apk.pkg]
    cmd = ['uninstall', packageName]
    run_adb_cmd(cmd)
    print ("uninstall Apk")
def monkeyrunner(packageName):
    pass
def generate_message():
    dialog_list = json.loads(codecs.open("dialog_release.json", "r", "utf-8").read())
    a = random.randint(0,19918)
    content = dialog_list[a]['content']
    b = random.randint(0, len(content) - 1)
    mesg = content[b]
    return mesg
def get_flow2uid(uidic, proto='tcp'):
    connections = {}
    with open(f'./{proto}_connections.txt', 'r') as f:
        i = 0
        for line in f:
            #跳过第一行
            if i == 0:
                i += 1
                continue
            # 移除行末的换行符
            line = line.strip()
            
            # 分割行,获取 uid 和连接信息
            parts = line.split(': ')
            uid = int(parts[0])
            if uid not in uidic.keys():
                continue
            uid = uidic[uid]
            conn_info = parts[1]
            
            # 将连接信息拆分为元组列表
            temp = conn_info
            conn_infolist = list(conn_info)
            for i in range(1, len(temp)):
                if temp[i] == ' ' and temp[i-1] != ',':
                    conn_infolist[i] = '  '
            conn_info = ''.join(conn_infolist)
            conn_list = [tuple(conn.strip('()').split(', ') + [proto]) for conn in conn_info.split('  ')]
            
            # 将数据存入字典
            connections[uid] = list(set(conn_list))
    return connections
if __name__ == "__main__":
    #getpackageslist()
    d = u2.connect()
    d.screen_on()
    d.unlock()
    
    log = logging.getLogger("apk traffic sniff")
    packageName = 'tv.danmaku.bili'
    """
    for i in tqdm(range(50)):
        domonkeyInapp(packageName)
    """
    getflowByuid('10166')
        