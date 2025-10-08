import uiautomator2 as u2
import time
import threading
from threading import Event
import subprocess
import os
import signal
import glob
import random
from requests.exceptions import ReadTimeout
import json as js
import socket
from collections import defaultdict
from adb_test import getpackageslist, install_apk,uninstallApk, getuidByPackage, getflowByuid,generate_message, get_flow2uid
class Trafficsnif:
    @staticmethod
    def run_adb_cmd(cmd):
        global device
        args = ['adb', '-s', device]
        args.extend(cmd)
        ret = None
        # 运行adb命令
        adbProcess = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = adbProcess.communicate()
        
        return ret  
    @staticmethod
    def check(event, pkgname):
        global flow2uid, device
        while True:
            if event.is_set():
                break
            """
            e1 = d.xpath("同意并继续")
            e2 = d.xpath("我知道了")
            
            if e1.exists:
                e1.click()
            if e2.exists:
                e2.click()
            d.xpath("同意").click_exists(timeout=1)
            if 'Trans'in d.app_current()['activity']:
                d.press("back")
                time.sleep(0.5)
            if 'login'in d.app_current()['activity'] or 'Login'in d.app_current()['activity']:
                d.press("back")
                time.sleep(0.5)
            if "launcher" in d.app_current()['activity']:
                d.press("back")
                time.sleep(0.5)
            if "permission" in d.app_current()['activity'] or "Permission" in d.app_current()['activity']:
                if (d.xpath("允许").exists):
                    d.xpath("允许").click()
                    time.sleep(0.5)
            """
            uid = getuidByPackage(pkgname, device)
            flow2uid[pkgname] = list(set(flow2uid[uid] + getflowByuid(uid, device))) 
    @staticmethod
    def do_press(d, cmd):
        d.xpath(cmd).click_exists(timeout=1)
        time.sleep(5)
        d.press("back")
        time.sleep(1)
        
    #统一启动函数，处理流量捕获开始时的准备操作
    @staticmethod
    def start_pre(package, act=None):
        event = Event()
        #初始化抓包命令
        filename =f'{package}_{str(time.time())}.pcap'
        local_cmd = basecmd
        cmd = ['/data/tcpdump', 
        '-i', 'rmnet_data1','-w', '/sdcard/' + filename, 'not','host',host]
        local_cmd = basecmd + cmd
        """
        cmd = ['adb', 'shell', 'su','-c','timeout 60','/data/tcpdump', 
        '-i', 'rmnet_data1','-w', '/sdcard/' + filename, 'not','host',host]
        """
        #删除旧日志文件
        cmd = ['shell','rm', '-rf', 'sdcard/networklog.txt']
        Trafficsnif.run_adb_cmd(cmd)
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
        checklogin = threading.Thread(target=Trafficsnif.check,args=(event,package))
        checklogin.start()
        d.implicitly_wait(10)
        width, height = d.window_size()
        return pcapProcess, checklogin, event, filename
    #统一终止函数，处理流量采集结束后的相关操作
    @staticmethod
    def end_pre(package,pcapProcess,checklogin,event,filename, act_do = 0):
        event.set()
        checklogin.join()
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
        
        cmd = ['pull', '/sdcard/'+filename, os.path.join(storePath, tempname)]
        Trafficsnif.run_adb_cmd(cmd)
        # 将本次触发得到的Pcap文件删除
        cmd = ['shell','rm','-rf','/sdcard/'+filename]
        Trafficsnif.run_adb_cmd(cmd)    
        return filename

    @staticmethod
    def backgroud_two_flow(forePackage, backPackage):
        filename =f'{forePackage}_{backPackage}_{str(time.time())}.pcap'
        
        cmd = ['/data/tcpdump', 
        '-i', 'rmnet_data1','-w', '/sdcard/' + filename, 'not','host',host]
        local_cmd = basecmd + cmd
        print(local_cmd)
        log_cmd_tcp = ['adb', 'shell', 'sh', '/sdcard/tcplinksniff.sh']
        log_cmd_udp = ['adb', 'shell', 'sh', '/sdcard/udplinksniff.sh']
        #back do first 
        event = Event()
        if backPackage in ['com.tencent.mm', 'com.tencent.mobileqq']:
            back_event, _ = getattr(Trafficsnif, backPackage.replace('.', '_'))('back', 3)
        else:
            back_event, _ = getattr(Trafficsnif, backPackage.replace('.', '_'))('back')
        """
        #方法1，删除日志文件
        cmd = ['shell','rm', '-rf', 'sdcard/tcp_connections.txt']
        Trafficsnif.run_adb_cmd(cmd)
        cmd = ['shell','rm', '-rf', 'sdcard/udp_connections.txt']
        Trafficsnif.run_adb_cmd(cmd)
        """
        #方法2，删除日志文件
        cmd = ['shell','rm', '-rf', 'sdcard/networklog.txt']
        Trafficsnif.run_adb_cmd(cmd)
        #启动日志记录
        """
        #方法1，记录udp/tcp日志
        tcplogProcess = subprocess.Popen(log_cmd_tcp,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        udplogProcess = subprocess.Popen(log_cmd_udp,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        """
        #方法2，使用NetLog应用
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
        checklogin_fore = threading.Thread(target=Trafficsnif.check,args=(event,forePackage))
        checklogin_back = threading.Thread(target=Trafficsnif.check,args=(event,backPackage))
        checklogin_fore.start()
        checklogin_back.start()
        #fore do neext 
        fore_event, _ = getattr(Trafficsnif, forePackage.replace('.','_'))('fore')
        event.set()
        checklogin_fore.join()
        checklogin_back.join()
        d.app_stop(forePackage)
        #d.app_clear(forePackage)
        d.app_stop(backPackage)
        #d.app_clear(backPackage)
        pcapProcess.wait()
        #方法2，结束日志
        d.app_stop("com.googlecode.networklog")
        storepath = os.path.join(traffic_path, forePackage+ '_' + backPackage)
        if not os.path.exists(storepath):
            os.makedirs(storepath, exist_ok=True)
        pcapPath = os.path.join(storepath
                                ,filename)
        cmd = ['pull', '/sdcard/'+filename, pcapPath]
        Trafficsnif.run_adb_cmd(cmd)
        # 将本次触发得到的Pcap文件删除
        cmd = ['shell','rm','-rf','/sdcard/'+filename]
        Trafficsnif.run_adb_cmd(cmd)
        """
        #方法1，获取日志文件
        cmd = ['pull', '/sdcard/tcp_connections.txt', './tcp_connections.txt']
        Trafficsnif.run_adb_cmd(cmd)
        cmd = ['pull', '/sdcard/udp_connections.txt', './udp_connections.txt']
        Trafficsnif.run_adb_cmd(cmd)
        """
        #方法2，获取日志文件
        cmd = ['pull', '/sdcard/networklog.txt', './networklog.txt']
        Trafficsnif.run_adb_cmd(cmd)
        uidic = {int(getuidByPackage(forePackage,device)):forePackage, int(getuidByPackage(backPackage,device)):backPackage}
        """
        #方法1,处理日志文件
        tcp_connection = get_flow2uid(uidic, proto='tcp')
        udp_connection = get_flow2uid(uidic, proto='udp')
        connections = defaultdict(list)
        for di in (tcp_connection, udp_connection):
            for ki, vi in di.items():
                connections[ki].extend(vi)
        connections = dict(connections)
        """
        #方法2，处理日志文件
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
        return connections, filename
    @staticmethod
    def com_autonavi_minimap(mode):
        package = "com.autonavi.minimap"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename=  Trafficsnif.start_pre(package)
        time.sleep(2)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("com.autonavi.minimap:id/iv_close").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("取消").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,2)
        act = 0
        def act1():
            dolist = ['up', 'down','left', 'right']
            for i in range(24):
                rnd = random.randint(0,3)
                d.swipe_ext(dolist[rnd])
                time.sleep(5)
        def act2():
            time.sleep(2)
            d.xpath('附近').click_exists(timeout=1)
            
            for i in range(24):
                d.swipe_ext('up')
                time.sleep(5)
        def act3():
            d.xpath("实时公交").click_exists(timeout=1)
            time.sleep(6)
            for i in range(10):
                d.swipe_ext('up')
                time.sleep(5)
        act_funcs = {
            0:act1,
            1:act2,
            2:act3,
        }
        if mode == 'back':
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            time.sleep(5)
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 3]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def installtest():
        apklist = glob.glob("XXXXX\ApkStore" + '/*.apk')
        for i,apk in enumerate(apklist):
            if i < 5:
                continue
            oldlist = getpackageslist()
            print("Installing...")
            install_apk(apkpath=apk)
            newlist = getpackageslist()
            pkg = list(set(newlist) - set(oldlist))
            if len(pkg) == 0:
                continue
            pkg = pkg[0].decode('utf-8')
            pkg = pkg.split(':')[1]
            d.app_start(pkg)
            time.sleep(4)
            d.app_stop(pkg)
            d.app_clear(pkg)
            time.sleep(1)
            #uninstallApk(pkg)
            break
    
    @staticmethod
    def air_tv_douyu_android(mode):
        package = "air.tv.douyu.android"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("等待").click()
        ctx.when("忽略").click()
        ctx.when("稍后再说").click()
        ctx.when("下次再说").click()
        ctx.when("确定").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when('0.01元参与').call(lambda d : d.click(894,501))
        ctx.when("狠心离开").click()
        ctx.when("残忍离开").click()
        ctx.when("不感兴趣").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            for i in range(5):
                d.swipe_ext('up')
                time.sleep(60)
        def act2():
            time.sleep(2)
            d.click(250,1100)
            time.sleep(300)
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode == 'back':
            while True:
                try:
                    d.xpath('首页').click()
                    break
                except:
                    continue
            time.sleep(5)
            d.xpath('//*[@resource-id="air.tv.douyu.android:id/kc_"]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]').click_exists(timeout=1)
            time.sleep(4)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                #func = act_funcs[act % 2]
                func = act_funcs[0]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_duowan_kiwi(mode):
        package = "com.duowan.kiwi"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("忽略").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("等待").click()
        ctx.when("稍后再说").click()
        ctx.when("下次再说").click()
        ctx.when("确定").click()
        ctx.when("确认").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when('0.01元参与').call(lambda d : d.click(894,501))
        ctx.when("狠心离开").click()
        ctx.when("残忍离开").click()
        ctx.when("不感兴趣").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            for i in range(5):
                d.swipe_ext('up')
                time.sleep(60)
        def act2():
            time.sleep(2)
            d.xpath('//*[@resource-id="com.duowan.kiwi:id/content_view"]/android.view.ViewGroup[1]').click_exists(timeout=1)
            time.sleep(300)
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode == 'back':
            while True:
                try:
                    d.xpath("首页").click()
                    break
                except:
                    continue
            time.sleep(5)
            d.xpath('//*[@resource-id="com.duowan.kiwi:id/content_view"]/android.view.ViewGroup[1]').click_exists(timeout=1)
            time.sleep(7)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 2]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_qiyi_video(mode):
        package = "com.qiyi.video"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("确定").click()
        ctx.when("确认").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when('0.01元参与').call(lambda d : d.click(894,501))
        ctx.when("狠心离开").click()
        # ctx.when("不感兴趣").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            d.click(274,1060)
            time.sleep(600)
        def act2():
            d.xpath('随刻视频').click_exists(timeout=1)
            time.sleep(2)
            for i in range(20):
                time.sleep(30)
                d.swipe_ext('up')
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode == 'back':
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 2]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_tencent_qqlive(mode):
        package = "com.tencent.qqlive"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("确定").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when('0.01元参与').call(lambda d : d.click(894,501))
        ctx.when("狠心离开").click()
        ctx.when("不感兴趣").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            d.xpath('返回顶部').click_exists(timeout=1)
            time.sleep(10)
            #d.xpath('电影').click_exists(timeout=1)
            #time.sleep(10)
            d.xpath(f'//androidx.viewpager.widget.ViewPager/android.widget.RelativeLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.FrameLayout[{random.randint(1,4)}]/android.view.ViewGroup[1]/android.view.ViewGroup[1]').click_exists(timeout=1)
            d.click(268,1707)
            time.sleep(300)
        def act2():
            d.xpath('短片').click_exists(timeout=1)
            time.sleep(2)
            for i in range(20):
                time.sleep(30)
                d.swipe_ext('up')
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode == 'back':
            while True:
                try:
                    d.xpath('首页').click()
                    time.sleep(3)
                    break
                except:
                    continue
            d.xpath('电视剧').click_exists(timeout=1)
            time.sleep(5)
            d.xpath(f'//androidx.viewpager.widget.ViewPager/android.widget.RelativeLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.FrameLayout[{random.randint(2,5)}]/android.view.ViewGroup[1]/android.view.ViewGroup[1]').click_exists(timeout=1)
            time.sleep(3)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                if act == 1:
                    continue
                func = act_funcs[act % 2]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_hunantv_imgo_activity(mode):
        package = "com.hunantv.imgo.activity"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("确定").click()
        ctx.when("忽略").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when('0.01元参与').call(lambda d : d.click(894,501))
        ctx.when("com.hunantv.imgo.activity:id/ivJbpFirstPopClose").click()
        ctx.when("com.hunantv.imgo.activity:id/btnClose").click()
        ctx.when("狠心离开").click()
        ctx.when("同意开启").click()
        ctx.when("不感兴趣").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            d.xpath('返回顶部').click_exists(timeout=1)
            time.sleep(3)
            d.xpath('电影').click_exists(timeout=1)
            time.sleep(10)
            for i in range(random.randint(1,3)):
                d.swipe_ext('up')
                d.sleep(2)
            d.xpath('//android.support.v7.widget.RecyclerView/android.widget.LinearLayout[2]/android.widget.LinearLayout[2]/android.widget.RelativeLayout[1]').click_exists(timeout=1)
            #d.click(268,1707)
            time.sleep(280)
        def act2():
            d.xpath('短视频').click_exists(timeout=1)
            time.sleep(5)
            for i in range(20):
                time.sleep(30)
                d.swipe_ext('up')
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode == 'back':
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 2]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('//*[@resource-id="com.hunantv.imgo.activity:id/tab_host_index"]/android.widget.RelativeLayout[1]/android.view.View[1]').click_exists(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    
    @staticmethod
    def com_sina_weibog3(mode, act_do=0):
        package = "com.sina.weibog3"
        package = "com.sina.weibog3"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename=  Trafficsnif.start_pre(package)
        
        d.xpath("确定").click_exists(timeout=1)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("确定").click()
        ctx.when("跳过").click()
        ctx.when("我知道了").click()
        ctx.when("以后再说").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,6)
        actlist = ['hotBrowsing', 'videoBrowsing', 'chaohuaBlogs', 'articleBrowsing', 
                   'browsingHistory', 'digitalCollection', 'shoppingBrowsing']
        def act1():
            while True:
                try:
                    d.xpath("发现").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            #刷微博发现热点（视频、图片、文字混合）
            time.sleep(4)
            d.xpath("热点").click_exists(timeout=1)
            time.sleep(2)
            if act_do == 0:
                for i in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(15)
                    d.swipe_ext('up')
        def act2():
            #刷微博视频（视屏、文字混合）
            while True:
                try:
                    d.xpath('//*[@resource-id="com.sina.weibog3:id/main_radio"]/android.widget.FrameLayout[3]').click(timeout=1)
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            #刷微博发现热点（视频、图片、文字混合）
            time.sleep(4)
            d.xpath('//*[@resource-id="com.sina.weibog3:id/main_radio"]/android.widget.FrameLayout[2]').click_exists(timeout=1)
            time.sleep(2)
            while time.time() - start_time < goaltime:
                time.sleep(30)
                d.swipe_ext('up')
        def act3():
            #刷超话广场（文字、图片混合
            while True:
                try:
                    d.xpath("超话").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            #刷微博发现热点（视频、图片、文字混合）
            time.sleep(4)
            d.xpath("广场").click_exists(timeout=1)
            time.sleep(2)
            if act_do == 0:
                for i in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        def act4():
            #刷头条文章
            while True:
                try:
                    d.xpath("我").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            time.sleep(2)
            while not d.xpath('头条文章').exists:
                d.swipe_ext('up')
                time.sleep(2)
            d.xpath("头条文章").click_exists(timeout=1)
            time.sleep(3)
            d.click(500,500)
            if act_do == 0:
                for j in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else: 
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')  
        def act5():
            #查看浏览记录
            while True:
                try:
                    d.xpath("我").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            time.sleep(2)
            while not d.xpath('浏览记录').exists:
                d.swipe_ext('down')
                time.sleep(2)
            d.xpath("浏览记录").click_exists(timeout=1)
            time.sleep(3)
            d.xpath("视频").click_exists(timeout=1)
            if act_do == 0:
                for i in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        def act6():
            #数字藏品浏览
            while True:
                try:
                    d.xpath("我").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            time.sleep(2)
            while not d.xpath('我的钱包').exists:
                d.swipe_ext('down')
                time.sleep(2)
            d.xpath('我的钱包').click_exists(timeout=1)
            time.sleep(3)
            while not d.xpath("数字藏品").exists:
                d.swipe_ext('up')
                time.sleep(2)
            d.xpath("数字藏品").click_exists(timeout=1)
            if act_do == 0:
                for i in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        def act7():
            #微博限时购商品秒杀
            while True:
                try:
                    d.xpath("我").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            time.sleep(2)
            while not d.xpath('我的钱包').exists:
                d.swipe_ext('down')
                time.sleep(2)
            d.xpath('我的钱包').click_exists(timeout=1)
            time.sleep(3)
            while not d.xpath("限时购").exists:
                d.swipe_ext('up')
                time.sleep(2)
            d.xpath("限时购").click_exists(timeout=1)
            if act_do == 0:
                for i in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        act_funcs = {
            0:act1,
            1:act2,
            2:act3,
            3:act4,
            4:act5,
            5:act6,
            6:act7
        }
        if mode =='back':
            time.sleep(4)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                if mode == 'fore':
                    act = 0
                if act_do == 0:
                    func = act_funcs[act % 2]
                else:
                    func = act_funcs[act_do - 1]
                func()
                t = True
                while t :
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath("首页").click_exists(timeout=1)
                        # d.xpath('//*[@resource-id="com.sina.weibog3:id/main_radio"]/android.widget.FrameLayout[1]').click(timeout=1)
                        time.sleep(2)
                        d(resourceId="com.sina.weibog3:id/tv_groupName", text="关注").click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1  
        ctx.stop()
        if mode not in ['back', 'fore']:
            if act_do == 0:
                filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
            else:
                filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename, act_do=actlist[act_do-1])
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_sina_weibo(mode, act_do=0):
        package = "com.sina.weibo"
        package = "com.sina.weibo"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename=  Trafficsnif.start_pre(package)
        
        d.xpath("确定").click_exists(timeout=1)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("确定").click()
        ctx.when("跳过").click()
        ctx.when("我知道了").click()
        ctx.when("以后再说").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,6)
        actlist = ['hotBrowsing', 'videoBrowsing', 'chaohuaBlogs', 'articleBrowsing', 
                   'browsingHistory', 'digitalCollection', 'shoppingBrowsing']
        def act1():
            while True:
                try:
                    d.xpath("发现").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            #刷微博发现热点（视频、图片、文字混合）
            time.sleep(4)
            d.xpath("热点").click_exists(timeout=1)
            time.sleep(2)
            if act_do == 0:
                for i in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(15)
                    d.swipe_ext('up')
        def act2():
            #刷微博视频（视屏、文字混合）
            while True:
                try:
                    d.xpath('//*[@resource-id="com.sina.weibo:id/main_radio"]/android.widget.FrameLayout[3]').click(timeout=1)
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            #刷微博发现热点（视频、图片、文字混合）
            time.sleep(4)
            d.xpath('//*[@resource-id="com.sina.weibo:id/main_radio"]/android.widget.FrameLayout[2]').click_exists(timeout=1)
            time.sleep(2)
            while time.time() - start_time < goaltime:
                time.sleep(30)
                d.swipe_ext('up')
        def act3():
            #刷超话广场（文字、图片混合
            while True:
                try:
                    d.xpath("超话").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            #刷微博发现热点（视频、图片、文字混合）
            time.sleep(4)
            d.xpath("广场").click_exists(timeout=1)
            time.sleep(2)
            if act_do == 0:
                for i in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        def act4():
            #刷头条文章
            while True:
                try:
                    d.xpath("我").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            time.sleep(2)
            while not d.xpath('头条文章').exists:
                d.swipe_ext('up')
                time.sleep(2)
            d.xpath("头条文章").click_exists(timeout=1)
            time.sleep(3)
            d.click(500,500)
            if act_do == 0:
                for j in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else: 
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')  
        def act5():
            #查看浏览记录
            while True:
                try:
                    d.xpath("我").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            time.sleep(2)
            while not d.xpath('浏览记录').exists:
                d.swipe_ext('down')
                time.sleep(2)
            d.xpath("浏览记录").click_exists(timeout=1)
            time.sleep(3)
            d.xpath("视频").click_exists(timeout=1)
            if act_do == 0:
                for i in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        def act6():
            #数字藏品浏览
            while True:
                try:
                    d.xpath("我").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            time.sleep(2)
            while not d.xpath('我的钱包').exists:
                d.swipe_ext('down')
                time.sleep(2)
            d.xpath('我的钱包').click_exists(timeout=1)
            time.sleep(3)
            while not d.xpath("数字藏品").exists:
                d.swipe_ext('up')
                time.sleep(2)
            d.xpath("数字藏品").click_exists(timeout=1)
            if act_do == 0:
                for i in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        def act7():
            #微博限时购商品秒杀
            while True:
                try:
                    d.xpath("我").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            time.sleep(2)
            while not d.xpath('我的钱包').exists:
                d.swipe_ext('down')
                time.sleep(2)
            d.xpath('我的钱包').click_exists(timeout=1)
            time.sleep(3)
            while not d.xpath("限时购").exists:
                d.swipe_ext('up')
                time.sleep(2)
            d.xpath("限时购").click_exists(timeout=1)
            if act_do == 0:
                for i in range(20):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        act_funcs = {
            0:act1,
            1:act2,
            2:act3,
            3:act4,
            4:act5,
            5:act6,
            6:act7
        }
        if mode =='back':
            time.sleep(4)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                if mode == 'fore':
                    act = 0
                if act_do == 0:
                    func = act_funcs[act % 2]
                else:
                    func = act_funcs[act_do - 1]
                func()
                t = True
                while t :
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        # d.xpath("首页").click_exists(timeout=1)
                        d.xpath('//*[@resource-id="com.sina.weibo:id/main_radio"]/android.widget.FrameLayout[1]').click(timeout=1)
                        time.sleep(2)
                        d(resourceId="com.sina.weibo:id/tv_groupName", text="关注").click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1  
        ctx.stop()
        if mode not in ['back', 'fore']:
            if act_do == 0:
                filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
            else:
                filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename, act_do=actlist[act_do-1])
        else:
            return event,None
        return None, filename
    @staticmethod
    def tv_danmaku_bili(mode):
        package = "tv.danmaku.bili"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("等待").click()
        ctx.when("同意并继续").click()
        ctx.when("重试").click()
        ctx.when("我知道了").click()
        ctx.when("登录").call(lambda d: d.press("back"))
        ctx.when("密码登录").call(lambda d: d.press("back"))
        ctx.wait_stable() # 等待界面不在有弹窗了
        t = True
        act = random.randint(0,1)
        act = 0
        start_time = time.time()
        def act1():
            # for i in range(2):
            #     time.sleep(3)
            #     d.swipe_ext('up')
            time.sleep(3)
            d.click(268,1239)
            time.sleep(300)
        def act2():
            for i in range(2):
                time.sleep(3)
                d.swipe_ext('up')
            d.click(268,1239)
            time.sleep(5)
            d.double_click(520,406)
            time.sleep(1)
            d.xpath('评论').click_exists(timeout=1)
            for i in range(12):
                time.sleep(5)
                d.swipe_ext('up')
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode =='back':
            while True:
                try:
                    d.xpath('首页').click_exists(timeout=1)
                    break
                except:
                    continue
            time.sleep(4)
            d.xpath('//*[@resource-id="tv.danmaku.bili:id/recycler_view"]/android.view.ViewGroup[2]/android.widget.FrameLayout[1]').click_exists(timeout=1)
            
            time.sleep(5)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 2]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
        
        #d(resourceId=f"{package}:id/private_yes").click()
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_ximalaya_ting_android(mode):
        package = "com.ximalaya.ting.android"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("跳过广告").click()
        ctx.when("稍后更新").click()
        ctx.when("同意").click()
        ctx.when("确定").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when('0.01元参与').call(lambda d : d.click(894,501))
        ctx.when("狠心离开").click()
        ctx.when("不感兴趣").click()
        ctx.when("com.ximalaya.ting.android:id/main_iv_close").click()
        ctx.when("com.ximalaya.ting.android:id/host_free_listen_time_close_iv").click()
        ctx.when("com.ximalaya.ting.android:id/main_iv_limit_close").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            time.sleep(5)
            for i in range(20):
                d.swipe_ext('up')
                time.sleep(6)
        def act2():
            d.xpath('首页').click_exists(timeout=1)
            time.sleep(5)
            d.xpath('//*[@resource-id="android:id/list"]/android.widget.RelativeLayout[2]/android.widget.RelativeLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]/android.widget.ImageView[1]').click_exists(timeout=1)
            time.sleep(4)
            d.xpath('开始播放').click_exists(timeout=1)
            time.sleep(120)
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode == 'back':
            #等待页面稳定
            time.sleep(10)
            while True:
                try:
                    d.xpath('首页').click_exists(timeout=1)
                    break
                except:
                    continue
            time.sleep(5)
            d.xpath('//*[@resource-id="android:id/list"]/android.widget.RelativeLayout[2]/android.widget.RelativeLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]/android.widget.ImageView[1]').click_exists(timeout=1)
            time.sleep(4)
            d.xpath('开始播放').click_exists(timeout=1)
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 2]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_netease_cloudmusic(mode):
        package = "com.netease.cloudmusic"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package,'com.netease.cloudmusic.activity.IconChangeDefaultAlias')
        else:
            pcapProcess, checklogin, event, filename=  Trafficsnif.start_pre(package,'com.netease.cloudmusic.activity.IconChangeDefaultAlias')
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when('//*[@resource-id="com.netease.cloudmusic:id/dsl_dialog_root"]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.widget.ImageView[1]').click()
        ctx.when("同意").click()
        ctx.when("立即体验").click()
        ctx.when("同意并继续").click()
        ctx.when("等待").click()
        ctx.when("跳过").click()
        ctx.when("去登录").call(lambda d: d.press('back'))
        ctx.when("com.netease.cloudmusic:id/dsl_dialog_root").call(lambda d:d.xpath('//*[@resource-id="com.netease.cloudmusic:id/dsl_dialog_root"]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]').click())
        ctx.when("com.netease.cloudmusic:id/updateVersionBgImage").call(lambda d: d(resourceId="com.netease.cloudmusic:id/md_dialog_cm_close_btn").click())
        ctx.when("com.netease.cloudmusic:id/md_dialog_cm_close_btn").click()
        ctx.when('//*[@resource-id="android:id/content"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.ViewGroup[1]/android.view.ViewGroup[2]/android.view.ViewGroup[1]').click()
        ctx.when("close-v2.de1574df").click()
        ctx.wait_stable() # 去登录
        time.sleep(2)
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            d.xpath('发现').click_exists(timeout=1)
            time.sleep(5)
            for i in range(20):
                d.swipe_ext('up')
                time.sleep(6)
        def act2():
            d.xpath('我的').click_exists(timeout=1)
            time.sleep(3)
            d.xpath('持续更新一个没有vip的免费歌单').click_exists(timeout=1)
            time.sleep(5)
            d.xpath('播放全部').click_exists(timeout=1)
            time.sleep(10)
            d(resourceId="com.netease.cloudmusic:id/commentBtnStyle2").click_exists(timeout=1)
            for j in range(10):
                d.swipe_ext("up")
                time.sleep(10)
            t = True
            while t:
                if time.time() - start_time < goaltime:
                        break
                try:
                    d.xpath('我的').click(timeout=1)
                    t = False
                except:
                    d.press('back')
                    time.sleep(1)
            d(resourceId="com.netease.cloudmusic:id/minPlayBtn").click_exists(timeout=1)
            time.sleep(1)
        def act3():
            d.xpath('动态').click_exists(timeout=1)
            time.sleep(4)
            for i in range(10):
                d.swipe_ext('up')
                time.sleep(12)
        def act4():
            time.sleep(4)
            d.click(333,814)
            time.sleep(4)
            for j in range(12):
                d.swipe_ext("up")
                time.sleep(5)
        act_funcs = {
            0:act1,
            1:act2,
            2:act3
        }
        if mode =='back':
            time.sleep(3)
            while True:
                try:
                    d.xpath('我的').click_exists(timeout=1)
                    break
                except:
                    continue
            time.sleep(7)
            d.xpath('持续更新一个没有vip的免费歌单').click_exists(timeout=1)
            time.sleep(5)
            d.xpath('播放全部').click_exists(timeout=1)
            time.sleep(5)
            d.press("home")
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 3]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('我的').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                    
                time.sleep(5)
                act += 1    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    
    @staticmethod
    def com_tencent_mm(mode, act_do=0, commu_name='default'):
        package = "com.tencent.mm"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        
        ctx = d.watch_context()
        ctx.when("同意").click()
        ctx.when("我知道了").click()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        t = True
        start_time = time.time()
        act = random.randint(0,6)
        actlist = ['pictureSending','textChatting', 'voiceCall', 'videoCall', 
                   'subscriptionsBrowsing', 'channelsBrowsing', 'momentsBrowsing']
        def act1():
            #图片发送

            time.sleep(3)
            d.xpath(commu_name).click_exists(timeout=1)
            time.sleep(3)
            
            while time.time() - start_time - 6 < goaltime:
                pic_num = random.randint(1, 7)
                #显示额外功能
                d(resourceId="com.tencent.mm:id/bjz").click_exists(timeout=1)
                time.sleep(2)
                #相册查看
                d.xpath('//*[@resource-id="com.tencent.mm:id/a1u"]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[1]').click_exists(timeout=1)
                time.sleep(2)
                #选择图片
                d.xpath(f'//*[@resource-id="com.tencent.mm:id/jdw"]/android.widget.RelativeLayout[{pic_num}]/android.widget.CheckBox[1]').click_exists(timeout=1)
                time.sleep((pic_num + 3))
                #发送图片
                d(resourceId="com.tencent.mm:id/kaq").click_exists(timeout=1)
                time.sleep(random.randint(10,40) * 0.1)
        def act2():
            #文字聊天
            
            time.sleep(3)
            d.xpath(commu_name).click_exists(timeout=1)
            time.sleep(3)
            
            while time.time() - start_time - 6 < goaltime:
                msg = generate_message()
                #选择文本框
                d(resourceId="com.tencent.mm:id/o4q").click_exists(timeout=1)
                time.sleep(1)
                #输入消息文本
                d.send_keys(msg, clear=True)
                time.sleep(len(msg)/3)
                #发送消息
                d(resourceId="com.tencent.mm:id/bql").click_exists(timeout=1)
                time.sleep(random.randint(30,60) * 0.1)
        def act3():
            #语音通话
            time.sleep(3)
            d.xpath(commu_name).click_exists(timeout=1)
            time.sleep(3)
            #打开额外栏
            d(resourceId="com.tencent.mm:id/bjz").click_exists(timeout=1)
            time.sleep(3)
            hang = False
            if d.xpath("接听").exists:
                #存在接听，hang设置为true,标记为通话接收方
                hang = True
            if hang:
                d.xpath("接听").click_exists(timeout=1)
            else:
                #发起语音通话
                d.xpath('//*[@resource-id="com.tencent.mm:id/a1u"]/android.widget.LinearLayout[3]/android.widget.FrameLayout[1]').click_exists(timeout=1)
                time.sleep(2)
                d(resourceId="com.tencent.mm:id/obc", text="语音通话").click_exists(timeout=1)
            time.sleep(goaltime - 9)
            if not hang:
                #挂断语音通话
                d.click(500,500)
                time.sleep(0.5)
                d(description="挂断").click_exists(timeout=1)   
        def act4():
            #视频通话
            time.sleep(3)
            d.xpath(commu_name).click_exists(timeout=1)
            time.sleep(3)
            #打开额外栏
            d(resourceId="com.tencent.mm:id/bjz").click_exists(timeout=1)
            time.sleep(3)
            hang = False
            if d.xpath("接听").exists:
                #存在接听，hang设置为true,标记为通话接收方
                hang = True
            if hang:
                d.xpath("接听").click_exists(timeout=1)
            else:
                #发起视频通话
                d.xpath('//*[@resource-id="com.tencent.mm:id/a1u"]/android.widget.LinearLayout[3]/android.widget.FrameLayout[1]').click_exists(timeout=1)
                time.sleep(2)
                d(resourceId="com.tencent.mm:id/obc", text="视频通话").click_exists(timeout=1)
            temp_time = goaltime
            temp_time -= 9
            while temp_time > 0:
                d.xpath("接听").click_exists(timeout=1)
                temp_time -= 1
            if not hang:
                #挂断视频通话
                d.click(500,500)
                time.sleep(0.5)
                d(resourceId="挂断").click_exists(timeout=1)
        def act5():
            #订阅号浏览
            while True:
                try:
                    d.xpath("微信").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
            time.sleep(2)
            d.xpath("腾讯新闻").click_exists(timeout=1)
            for i in  range(42):
                time.sleep(6)
                d.swipe_ext('down')
        def act6():
            #视频号浏览
            while True:
                try:
                    d.xpath("发现").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
            time.sleep(2)
            d.xpath('视频号').click_exists(timeout=1)
            for i in  range(10):
                time.sleep(30)
                d.swipe(0.5, 0.8, 0.6, 0.3, 0.2)
        def act7():
            #朋友圈
            while True:
                try:
                    d.xpath("发现").click()
                    break
                except:
                    d.press('back')
            time.sleep(4)
            d.xpath('朋友圈').click_exists(timeout=1)
            time.sleep(2)
            for j in range(42):
                time.sleep(6)
                d.swipe_ext('up')
        act_funcs = {
            0:act1,
            1:act2,
            2:act3,
            3:act4,
            4:act5,
            5:act6,
            6:act7
        }
        if mode == 'back':
            #语音通话
            time.sleep(3)
            d.xpath(commu_name).click_exists(timeout=1)
            time.sleep(3)
            #打开额外栏
            d(resourceId="com.tencent.mm:id/bjz").click_exists(timeout=1)
            time.sleep(3)
            #发起语音通话
            d.xpath('//*[@resource-id="com.tencent.mm:id/a1u"]/android.widget.LinearLayout[3]/android.widget.FrameLayout[1]').click_exists(timeout=1)
            time.sleep(2)
            d(resourceId="com.tencent.mm:id/obc", text="语音通话").click_exists(timeout=1)
            time.sleep(3)
            d.press('home')
        else:
             while time.time() - start_time < goaltime:
                if act_do == 0:
                    func = act_funcs[act % 7]
                else:
                    func = act_funcs[act_do - 1]
                func()
                t = True
                while t:
                    if act_do == 0:
                        try:
                            d.xpath('微信').click(timeout=1)
                            t = False
                        except:
                            d.press('back')
                            time.sleep(1)
                    else:
                        break
                time.sleep(5)
                if act_do == 0:
                    act += 1  
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename,act_do=actlist[act_do-1])
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_tencent_mobileqq(mode, act_do=0, commu_name='龙的分身LG2'):
        package = "com.tencent.mobileqq"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("同意").click()
        ctx.when("我知道了").click()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        t = True
        start_time = time.time()
        act = random.randint(0,6)
        actlist = ['pictureSending','textChatting', 'voiceCall', 'videoCall', 
                   'qqchannelsBrowsing', 'shortvideoBrowsing', 'qqmomentsBrowsing']
        def act1():
            #图片发送
            
            time.sleep(3)
            d.xpath('//*[@resource-id="com.tencent.mobileqq:id/nl0"]/android.view.ViewGroup[1]').click_exists(timeout=1)
            
            time.sleep(3)
            
            while time.time() - start_time - 6 < goaltime:
                pic_num = random.randint(1, 9)
                d(description="相册").click_exists(timeout=1)
                time.sleep(2)
                d(resourceId="com.tencent.mobileqq:id/p2").click_exists(timeout=1)
                time.sleep(2)
                d.xpath(f'//*[@resource-id="com.tencent.mobileqq:id/skj"]/android.view.ViewGroup[{pic_num}]/android.widget.FrameLayout[1]/android.widget.CheckBox[1]').click_exists(timeout=1)
                time.sleep((pic_num + 3)/3)
                d(resourceId="com.tencent.mobileqq:id/tvh").click_exists(timeout=1)
                time.sleep(random.randint(10,40) * 0.1)
        def act2():
            #文字聊天
            time.sleep(3)
            d.xpath('//*[@resource-id="com.tencent.mobileqq:id/nl0"]/android.view.ViewGroup[1]').click_exists(timeout=1)
            time.sleep(3)
            
            while time.time() - start_time - 6 < goaltime:
                msg = generate_message()
                d(resourceId="com.tencent.mobileqq:id/input").click_exists(timeout=1)
                time.sleep(1)
                d.send_keys(msg, clear=True)
                time.sleep(len(msg)/3)
                d(resourceId="com.tencent.mobileqq:id/send_btn").click_exists(timeout=1)
                time.sleep(random.randint(10,40) * 0.1)
        def act3():
            #语音通话
            time.sleep(3)
            d.xpath('//*[@resource-id="com.tencent.mobileqq:id/nl0"]/android.view.ViewGroup[1]').click_exists(timeout=1)
            
            time.sleep(3)
            #打开额外栏
            d.xpath('//*[@resource-id="com.tencent.mobileqq:id/nku"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.RelativeLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[2]/android.widget.FrameLayout[2]').click_exists(timeout=1)
            time.sleep(3)
            hang = False
            if d.xpath("com.tencent.mobileqq:id/a28").exists:
                #存在接听，hang设置为true,标记为通话接收方
                hang = True
            if hang:
                d.xpath("com.tencent.mobileqq:id/a28").click_exists(timeout=1)
            else:
                #发起语音通话
                d.xpath('//*[@resource-id="com.tencent.mobileqq:id/txl"]/android.widget.RelativeLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]').click_exists(timeout=1)
            time.sleep(goaltime - 9)
            if not  hang:
                #挂断语音通话
                d.click(500,500)
                time.sleep(0.5)
                d(resourceId="com.tencent.mobileqq:id/g74").click_exists(timeout=1)
            
        def act4():
            #视频通话
            time.sleep(3)
            d.xpath('//*[@resource-id="com.tencent.mobileqq:id/nl0"]/android.view.ViewGroup[1]').click_exists(timeout=1)
            time.sleep(3)
            #打开额外栏
            d.xpath('//*[@resource-id="com.tencent.mobileqq:id/nku"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.RelativeLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[2]/android.widget.FrameLayout[2]').click_exists(timeout=1)
            time.sleep(3)
            hang = False
            if d.xpath("com.tencent.mobileqq:id/a28").exists:
                #存在接听，hang设置为true,标记为通话接收方
                hang = True
            if hang:
                d.xpath("com.tencent.mobileqq:id/a28").click_exists(timeout=1)
            else:
                #发起视频通话
                d.xpath('//*[@content-desc="视频通话"]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]').click_exists(timeout=1)
            time.sleep(goaltime - 9)
            if not  hang:
                #挂断视频通话
                d.click(500,500)
                time.sleep(0.5)
                d(resourceId="com.tencent.mobileqq:id/g74").click_exists(timeout=1)
        def act5():
            #频道浏览
            while True:
                try:
                    d.xpath("频道").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
            time.sleep(2)
            for i in  range(42):
                time.sleep(6)
                d.swipe_ext('up')
        def act6():
            #短视频浏览
            while True:
                try:
                    d.xpath("短视频").click()
                    break
                except:
                    d.press('back')
                    time.sleep(1)
            time.sleep(2)
            for i in  range(10):
                time.sleep(30)
                d.swipe_ext('up')
        def act7():
            #好友动态
            while True:
                try:
                    d.xpath("动态").click()
                    break
                except:
                    d.press('back')
            time.sleep(4)
            d.xpath('好友动态').click_exists(timeout=1)
            time.sleep(2)
            for j in range(42):
                time.sleep(6)
                d.swipe_ext('up')
        act_funcs = {
            0:act1,
            1:act2,
            2:act3,
            3:act4,
            4:act5,
            5:act6,
            6:act7
        }
        if mode == 'back':
            #语音通话
            time.sleep(3)
            d.xpath('//*[@resource-id="com.tencent.mobileqq:id/nl0"]/android.view.ViewGroup[1]').click_exists(timeout=1)
            
            time.sleep(3)
            #打开额外栏
            d.xpath('//*[@resource-id="com.tencent.mobileqq:id/nku"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.RelativeLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[2]/android.widget.FrameLayout[2]').click_exists(timeout=1)
            time.sleep(3)
            #发起语音通话
            d.xpath('//*[@resource-id="com.tencent.mobileqq:id/txl"]/android.widget.RelativeLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]').click_exists(timeout=1)
            time.sleep(2)
            d.press('home')
        else:
             while time.time() - start_time < goaltime:
                if act_do == 0:
                    func = act_funcs[act % 2]
                else:
                    func = act_funcs[act_do - 1]
                func()
                t = True
                while t:
                    if act_do == 0:
                        try:
                            d.xpath('消息').click(timeout=1)
                            t = False
                        except:
                            d.press('back')
                            time.sleep(1)
                    else:
                        break
                time.sleep(5)
                if act_do ==0:
                    act += 1  
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename,act_do=actlist[act_do-1])
        else:
            return event,None
        return None, filename
    
    @staticmethod
    def com_xunmeng_pinduoduo(mode):
        package = "com.xunmeng.pinduoduo"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when('//*[@content-desc="拍照搜索"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]').call(lambda d : d.xpath('//*[@content-desc="拍照搜索"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]').click())
        
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,5)
        act = 0
        def act1():
            for i in range(12):
                d.swipe_ext('up')
                time.sleep(5)
        def act2():
            time.sleep(2)
            for i in range(3):
                d.swipe_ext('up')
                time.sleep(3)
            d.click(250,1337)
            time.sleep(4)
            for i in range(11):
                d.swipe_ext('up')
                time.sleep(4)
            time.sleep(1)
        def act3():
            d.xpath("个人中心").click_exists(timeout=1)
            time.sleep(3)
            d.xpath("商品收藏").click_exists(timeout=1)
            for i in range(11):
                d.swipe_ext('up')
                time.sleep(5)
        def act4():
            d.xpath("多多视频").click_exists(timeout=1)
            time.sleep(3)
            d.xpath("直播").click_exists(timeout=1)
            time.sleep(3)
            d.click(120,450)
            time.sleep(52)
        def act5():
            d.xpath('个人中心').click_exists(timeout=1)
            time.sleep(3)
            d.xpath("我的订单").click_exists(timeout=1)
            time.sleep(3)
            for i in range(10):
                d.swipe_ext('up')
                time.sleep(6)
        act_funcs = {
            0:act1,
            1:act2,
            2:act3,
            3:act4,
            4:act5
        }
        if mode == 'back':
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 5]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_taobao_taobao(mode, act_do = 0):
        package = "com.taobao.taobao"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("暂不").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("com.taobao.taobao:id/aliuser_recommend_login_reg_tv").call(lambda d: d.press('back'))
        
            
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,6)
        actlist = ['productBrowsing', 'detailBrowsing', 'cartBrowsing', 'shortvideoBrowsing',
                   'historyorderBrowsing', 'messageBrowsing', 'taobaoMoments'] 
        def act1():
            if act_do == 0:
                for i in range(12):
                    time.sleep(6)
                    d.swipe_ext('up')
            #浏览商品
            else:
                while True:
                    try:
                        d.xpath('首页').click()
                        break
                    except:
                        d.press('back')
                        time.sleep(2)
                
                while time.time() - start_time < goaltime:
                #for i in range(12):
                    time.sleep(6)
                    d.swipe_ext('up')
                
        def act2():
            #浏览商品详细信息
            if act_do == 0:
                for i in range(random.randint(1,3)):
                    d.swipe_ext('up')
                    time.sleep(3)
                d.xpath('//android.support.v4.view.ViewPager/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.support.v7.widget.RecyclerView[1]/android.widget.FrameLayout[4]/android.widget.FrameLayout[1]').click_exists(timeout=1)
                time.sleep(4)
                for i in range(11):
                    d.swipe_ext('up')
                    time.sleep(6)
            else:
                while True:
                    try:
                        d.xpath('首页').click()
                        break
                    except:
                        d.press('back')
                        time.sleep(2)
                for i in range(random.randint(1,3)):
                    d.swipe_ext('up')
                    time.sleep(3)
                d.xpath('//android.support.v4.view.ViewPager/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.support.v7.widget.RecyclerView[1]/android.widget.FrameLayout[4]/android.widget.FrameLayout[1]').click_exists(timeout=1)
                time.sleep(4)
                while time.time() - start_time < goaltime:
                #for i in range(11):
                    d.swipe_ext('up')
                    time.sleep(6)
        def act4():
            #浏览购物车信息
            while True:
                try:
                    d.xpath('购物车').click()
                    break
                except:
                    d.press('back')
                    time.sleep(2)
            time.sleep(3)
            if act_do == 0:
                for i in range(11):
                    d.swipe_ext('up')
                    time.sleep(6)
            else:
                while time.time() - start_time < goaltime:
                #for i in range(11):
                    d.swipe_ext('up')
                    time.sleep(6)
        
        def act3():
            out = False
            #观看短视频
            while out == False:
                try:
                    d.xpath('视频').click()
                    out = True
                except:
                    d.press('back')
                    time.sleep(2)
                try:
                    d.xpath('//*[@content-desc="逛逛"]/android.widget.ImageView[1]').click()
                    out = True
                except:
                    d.press('back')
                    time.sleep(2)
            time.sleep(3)
            """
            d(description="直播,未选中,按钮").click_exists(timeout=1)
            time.sleep(3)"""
            if act_do == 0:
                for i in range(2):
                    d.swipe_ext('up')
                    time.sleep(30)  
            else:
                while time.time() - start_time < goaltime:
                #for i in range(2):
                    d.swipe_ext('up')
                    time.sleep(30)   
        def act5():
            #浏览历史订单
            while True:
                try:
                    d.xpath('我的淘宝').click()
                    break
                except:
                    d.press('back')
                    time.sleep(2)
            time.sleep(4)
            d.xpath("我的订单").click_exists(timeout=1)
            time.sleep(4)
            if act_do == 0:
                for i in range(10):
                    d.swipe_ext('up')
                    time.sleep(6)
            else:
                while time.time() - start_time < goaltime:
                #for i in range(10):
                    d.swipe_ext('up')
                    time.sleep(6)
        def act6():
            #浏览消息通知
            while True:
                try:
                    d.xpath('消息').click()
                    break
                except:
                    d.press('back')
                    time.sleep(2)
            time.sleep(2)
            d.xpath('//*[@resource-id="com.taobao.taobao:id/viewCenterSectionList"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.support.v7.widget.RecyclerView[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.View[3]').click_exists(timeout=1)
            time.sleep(4)
            d.xpath('//android.widget.HorizontalScrollView/android.widget.LinearLayout[1]/android.support.v7.app.ActionBar-b[6]/android.widget.FrameLayout[1]').click_exists(timeout=1)
            if act_do == 0:
                for i in range(10):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        def act7():
            #浏览淘友圈动态
            while True:
                try:
                    d.xpath('我的淘宝').click()
                    break
                except:
                    d.press('back')
                    time.sleep(2)
            if act_do == 0:
                for i in range(10):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        act_funcs = {
            0:act1,
            1:act2,
            2:act3,
            3:act4,
            4:act5,
            5:act6,
            6:act7
        }
        if mode == 'back':
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                if act % 5 == 3 and mode == 'fore':
                    act += 1
                    continue
                if act_do == 0:
                    func = act_funcs[act % 3]
                else:
                    func = act_funcs[act_do - 1]
                func()
                t= True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            if act_do == 0:
                filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
            else:
                filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename, act_do=actlist[act_do-1])
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_jingdong_app_mall(mode, act_do = 0):
        package = "com.jingdong.app.mall"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("等待").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("com.jd.lib.login.feature:id/ht").call(lambda d : d(resourceId="com.jd.lib.login.feature:id/ht").click())
        ctx.when("com.jd.lib.personal.feature:id/bc").call(lambda d : d(resourceId="com.jd.lib.personal.feature:id/bc").click())
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,6)
        actlist = ['productBrowsing', 'detailBrowsing', 'cartBrowsing', 'shortvideoBrowsing',
                   'historyorderBrowsing', 'messageBrowsing', 'taobaoMoments'] 
        def act1():
            #浏览商品
            if act_do == 0:
                for i in range(12):
                    d.swipe_ext('up')
                    time.sleep(6)
            else:
                while True:
                    try:
                        d.xpath('首页').click()
                        break
                    except:
                        d.press('back')
                        time.sleep(2)
                while time.time() - start_time < goaltime:
                #for i in range(12):
                    d.swipe_ext('up')
                    time.sleep(6)
        def act2():
            #浏览商品详细信息
            while True:
                try:
                    d.xpath('首页').click()
                    break
                except:
                    d.press('back')
                    time.sleep(2)
            for i in range(random.randint(1,3)):
                d.swipe_ext('up')
                time.sleep(3)
            d.xpath('//android.support.v4.view.ViewPager/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.support.v7.widget.RecyclerView[1]/android.widget.FrameLayout[4]/android.widget.FrameLayout[1]').click_exists(timeout=1)
    
            time.sleep(4)
            if act_do == 0:
                for i in range(11):
                    d.swipe_ext('up')
                    time.sleep(6)
            else:
                while time.time() - start_time < goaltime:
                #for i in range(11):
                    d.swipe_ext('up')
                    time.sleep(6)
        def act3():
            #浏览购物车信息
            while True:
                try:
                    d.xpath('购物车').click()
                    break
                except:
                    d.press('back')
                    time.sleep(2)
            time.sleep(3)
            if act_do == 0:
                for i in range(11):
                    d.swipe_ext('up')
                    time.sleep(6)  
            else:
                while time.time() - start_time < goaltime:
                #for i in range(11):
                    d.swipe_ext('up')
                    time.sleep(6)
        def act4():
            #观看短视频
            while True:
                try:
                    d.xpath('逛').click()
                    break
                except:
                    d.press('back')
                    time.sleep(2)
            time.sleep(3)
            """
            d(description="直播,未选中,按钮").click_exists(timeout=1)
            time.sleep(3)"""
            if act_do == 0:
                for i in range(2):
                    d.swipe_ext('up')
                    time.sleep(30)   
            else:
                while time.time() - start_time < goaltime:
                #for i in range(2):
                    d.swipe_ext('up')
                    time.sleep(30)   
        def act5():
            #浏览历史订单
            while True:
                try:
                    d.xpath('我的').click()
                    break
                except:
                    d.press('back')
                    time.sleep(2)
            time.sleep(4)
            d.xpath("我的订单").click_exists(timeout=1)
            time.sleep(4)
            if act_do == 0:
                for i in range(10):
                    d.swipe_ext('up')
                    time.sleep(6)
            else:
                while time.time() - start_time < goaltime:
                #for i in range(10):
                    d.swipe_ext('up')
                    time.sleep(6)
        def act6():
            #浏览消息通知
            while True:
                try:
                    d.xpath('我的').click()
                    break
                except:
                    d.press('back')
                    time.sleep(2)
            time.sleep(2)
            d(resourceId="com.jingdong.app.mall:id/d_f").click_exists(timeout=1)
            time.sleep(4)
            d.xpath('京东快讯').click_exists(timeout=1)
            if act_do == 0:
                for i in range(10):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        def act7():
            #浏览淘友圈动态
            while True:
                try:
                    d.xpath('我的').click()
                    break
                except:
                    d.press('back')
                    time.sleep(2)
            if act_do == 0:
                for i in range(10):
                    time.sleep(6)
                    d.swipe_ext('up')
            else:
                while time.time() - start_time < goaltime:
                    time.sleep(6)
                    d.swipe_ext('up')
        act_funcs = {
            0:act1,
            1:act2,
            2:act3,
            3:act4,
            4:act5,
            5:act6,
            6:act7
        }
        if mode == 'back':
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            time.sleep(5)
            while time.time() - start_time < goaltime:
                if act_do == 0:
                    if mode == 'fore' and act % 7 > 2:
                        act += 1
                        continue
                    func = act_funcs[act % 7]
                else:
                    func = act_funcs[act_do - 1]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            if act_do == 0:
                filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
            else:
                filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename, act_do=actlist[act_do-1])
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_baidu_searchbox(mode):
        package = "com.baidu.searchbox"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("以后再说").click()
        ctx.when("同意").click()
        ctx.when("确定").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when('0.01元参与').call(lambda d : d.click(894,501))
        ctx.when("狠心离开").click()
        #ctx.when("不感兴趣").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act2():
            for i in range(12):
                time.sleep(5)
                d.swipe_ext('up')
        def act1():
            for i in range(3):
                d.swipe_ext('up')
                time.sleep(4)
            time.sleep(3)
            d.xpath('//androidx.recyclerview.widget.RecyclerView/android.widget.RelativeLayout[1]').click_exists(timeout=1)
            time.sleep(5)
            for i in range(10):
                time.sleep(5)
                d.swipe_ext('up')
        def act3():
            d.xpath('//*[@resource-id="android:id/tabcontent"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[2]').click_exists(timeout=1)
            time.sleep(3)
            d(resourceId="com.baidu.searchbox:id/obfuscated", text="搜索").click_exists(timeout=1)
            time.sleep(5)
            for i in range(20):
                d.swipe_ext('up')
                time.sleep(5)
        act_funcs = {
            0:act1,
            1:act2,
            2:act3
        }
        if mode == 'back':
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                if mode == 'fore':
                    act = random.randint(1,2)
                func = act_funcs[act % 3]
                func()
                d.app_start('com.baidu.searchbox', 'com.baidu.searchbox.MainActivity')
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_UCMobile(mode):
        package = "com.UCMobile"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("以后再说").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("确定").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when('0.01元参与').call(lambda d : d.click(894,501))
        ctx.when("狠心离开").click()
        # ctx.when("不感兴趣").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            for i in range(12):
                time.sleep(5)
                d.swipe_ext('up')
        def act2():
            d.xpath('//*[@content-desc="搜索框"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').click_exists(timeout=1)
            time.sleep(3)
            d(resourceId="com.UCMobile:id/cancel").click_exists(timeout=1)
            time.sleep(5)
            for i in range(20):
                d.swipe_ext('up')
                time.sleep(5)
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode == 'back':
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 2]
                func()
                t= True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_kmxs_reader(mode):
        package = "com.kmxs.reader"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("确定").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("知道了").click()
        ctx.when('0.01元参与').call(lambda d : d.click(894,501))
        ctx.when("狠心离开").click()
        ctx.when("以后再说").click()
        ctx.when("残忍离开").click()
        ctx.when("稍后再说").click()
        ctx.when("下次再说").click()
        ctx.when("com.kmxs.reader:id/close_red_packet").click()
        ctx.when("com.kmxs.reader:id/iv_close_bonus").click()
        
        ctx.when("com.kmxs.reader:id/img_close_dialog").click()
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            #书城浏览
            for i in range(20):
                time.sleep(6)
                d.swipe_ext('up')
        def act2():
            #长时间阅读
            d.xpath('推荐').click_exists(timeout=1)
            time.sleep(5)
            d.xpath('//*[@resource-id="com.kmxs.reader:id/book_store_view_pager"]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.view.ViewGroup[3]').click_exists(timeout=1)
            time.sleep(5)
            for i in range(20):
                d.swipe_ext('left')
                time.sleep(10)
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode == 'back':
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 2]
                func()
                t = True
                while t:
                    try:
                        d.xpath('书城').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                        continue
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_dragon_read(mode):
        package = "com.dragon.read"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package,'.pages.splash.SplashActivity')
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package, act='.pages.splash.SplashActivity')
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("确定").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("知道了").click()
        ctx.when('0.01元参与').call(lambda d : d.click(894,501))
        ctx.when("狠心离开").click()
        ctx.when("下次再说").click()
        ctx.when("以后再说").click()
        ctx.when("稍后再说").click()
        ctx.when("暂不加入").click()
        ctx.when("com.dragon.read:id/bfn").click()
        ctx.when("com.dragon.read:id/nv").click()
        ctx.when("com.dragon.read:id/ak3").call(lambda d: d.xpath('//*[@resource-id="com.dragon.read:id/ak3"]/android.widget.FrameLayout[1]/com.lynx.tasm.behavior.ui.LynxFlattenUI[17]').click())

        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            #书城浏览
            d.xpath('推荐').click_exists(timeout=1)
            time.sleep(5)
            for i in range(20):
                time.sleep(6)
                d.swipe_ext('up')
        def act2():
            #长时间阅读
            d.xpath('经典').click_exists(timeout=1)
            time.sleep(5)
            d.xpath('//*[@resource-id="com.dragon.read:id/f16"]/android.widget.LinearLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]').click_exists(timeout=1)

            time.sleep(5)
            for i in range(20):
                d.swipe_ext('left')
                time.sleep(10)
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode == 'back':
            time.sleep(2)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 2]
                func()
                t = True
                while t:
                    try:
                        d.xpath('书城').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                        continue
                time.sleep(5)
                act += 1
                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def net_csdn_csdnplus(mode):
        package = "net.csdn.csdnplus"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("以后再说").click()
        ctx.when("同意").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("手机号登录").call(lambda d: d.press("back"))
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            for i in range(20):
                d.swipe_ext('up')
                time.sleep(5)
        def act2():
            time.sleep(4)
            d.xpath('//*[@resource-id="net.csdn.csdnplus:id/fl_container"]/android.widget.LinearLayout[1]/androidx.viewpager.widget.ViewPager[1]/android.widget.LinearLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]/android.view.ViewGroup[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[2]').click_exists(timeout=1)
            time.sleep(4)
            for j in range(12):
                d.swipe_ext("up")
                time.sleep(5)
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode =='back':
            time.sleep(4)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                if mode == 'fore':
                    act = 0
                func = act_funcs[act % 2]
                func()
                t = True
                while t:
                    try:
                        d.xpath('//*[@resource-id="net.csdn.csdnplus:id/ll_bar_content"]/android.widget.LinearLayout[1]').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_zhihu_android(mode):
        package = "com.zhihu.android"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("等待").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("取消").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("com.zhihu.android:id/iv_close").click()
        ctx.when("手机号登录").call(lambda d: d.press("back"))
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            for i in range(20):
                d.swipe_ext('up')
                time.sleep(6)
        def act2():
            time.sleep(4)
            d.click(333,814)
            time.sleep(4)
            for j in range(12):
                d.swipe_ext("up")
                time.sleep(5)
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode =='back':
            time.sleep(4)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                if mode == 'fore':
                    act = 0
                func = act_funcs[act % 2]
                func()
                d.app_start('com.zhihu.android','com.zhihu.android.app.ui.activity.MainActivity')
                
                time.sleep(5)
                act += 1                    
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_smile_gifmaker(mode):
        package = "com.smile.gifmaker"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
            time.sleep(2)
        else:
            pcapProcess, checklogin, event, filename =  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("取消").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("以后再说").click()
        ctx.when("手机号登录").call(lambda d: d.press("back"))
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        t = True
        act = random.randint(0,1)
        act = 0
        start_time = time.time()
        def act1():
            for i in range(4):
                d.swipe(0.5, 0.8, 0.6, 0.3, 0.2)
                time.sleep(30 + random.randint(5, 8))
        def act2():
            d(resourceId="com.smile.gifmaker:id/comment_icon").click_exists(timeout=1)
            time.sleep(4)
            for j in range(12):
                d.swipe_ext("up")
                time.sleep(5)
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode =='back':
            time.sleep(4)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 2]
                func()
                d.press('back')
                time.sleep(4)
                d.press('back')
                time.sleep(4)
                act += 1                 
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    @staticmethod
    def com_ss_android_ugc_aweme(mode):
        package = "com.ss.android.ugc.aweme"
        event = Event()
        filename =f'{package}_{str(time.time())}.pcap'
        if mode != 'back':
            tmd = ['/data/tcpdump', 
            '-i', 'rmnet_data1','-w', '/sdcard/' + filename, 'not','host','219.245.186.169']
            cmd = basecmd + tmd
            pcapProcess = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            checklogin = threading.Thread(target=Trafficsnif.check,args=(event,package))
            checklogin.start()
        d.app_start(package,'.splash.SplashActivity')
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("关闭").click()
        ctx.when("以后再说").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("我要投广告").call(lambda d: d.press("back"))
        ctx.when("登录").call(lambda d: d.press("back"))
        ctx.when("密码登录").call(lambda d: d.press("back"))
        ctx.wait_stable() # 等待界面不在有弹窗了
        d.implicitly_wait(10)
        width, height = d.window_size()
        time.sleep(2)
        start_time = time.time()
        t = True
        act = random.randint(0,1)
        act = 0
        start_time = time.time()
        def act1():
            for i in range(10):
                d.swipe_ext('up')
                time.sleep(30 + random.randint(5, 8))
        def act2():
            d.xpath('评论%').click_exists(timeout=1)
            time.sleep(4)
            for j in range(12):
                d.swipe_ext("up")
                time.sleep(5)
        act_funcs = {
            0:act1,
            1:act2
        }
        if mode =='back':
            time.sleep(4)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 2]
                func()
                d.press('back')
                time.sleep(4)
                d.press('back')
                time.sleep(4)
                act += 1
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename
    
    @staticmethod
    def com_tencent_qqmusic(mode):
        package = "com.tencent.qqmusic"
        event = Event()
        if mode in ['back', 'fore']:
            d.app_start(package)
        else:
            pcapProcess, checklogin, event, filename=  Trafficsnif.start_pre(package)
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("同意").click()
        ctx.when("以后再说").click()
        ctx.when("立即体验").click()
        ctx.when("同意并继续").click()
        ctx.when("等待").click()
        ctx.when("跳过").click()
        ctx.when("去登录").call(lambda d: d.press('back'))
        ctx.when("com.netease.cloudmusic:id/updateVersionBgImage").call(lambda d: d(resourceId="com.netease.cloudmusic:id/md_dialog_cm_close_btn").click())
        ctx.when("\u5173\u95ed\u5f39\u7a97").click()
        ctx.wait_stable() # 去登录
        time.sleep(2)
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            for i in range(20):
                d.swipe_ext('up')
                time.sleep(6)
        def act2():
            d(resourceId="com.tencent.qqmusic:id/gua").click_exists(timeout=1)
            time.sleep(4)
            d.click(333,814)
            time.sleep(4)
            for j in range(12):
                d.swipe_ext("up")
                time.sleep(5)
        def act3():
            time.sleep(4)
            d.click(333,814)
            time.sleep(4)
            for j in range(12):
                d.swipe_ext("up")
                time.sleep(5)
        def act4():
            time.sleep(4)
            d.click(333,814)
            time.sleep(4)
            for j in range(12):
                d.swipe_ext("up")
                time.sleep(5)
        act_funcs = {
            0:act1,
            1:act2,
            2:act3
        }
        if mode =='back':
            time.sleep(4)
            d.press('home')
            time.sleep(1)
        else:
            while time.time() - start_time < goaltime:
                func = act_funcs[act % 3]
                func()
                t = True
                while t:
                    if time.time() - start_time < goaltime:
                        break
                    try:
                        d.xpath('首页').click(timeout=1)
                        t = False
                    except:
                        d.press('back')
                        time.sleep(1)
                time.sleep(5)
                act += 1    
        """
        while t == True:
            try:
                d.xpath("同意").click_exists(timeout=1)
                time.sleep(1)
                d.xpath("立即体验").click_exists(timeout=1)
                time.sleep(1)
                d.xpath("同意并继续").click_exists(timeout=1)
                time.sleep(2)
                d.xpath("发现").click()
                t = False
            except:
                print('not start, restart!')
                d.press("back")
                time.sleep(0.5)
                d.app_start(package,'com.netease.cloudmusic.activity.IconChangeDefaultAlias')
        """
        if mode =='back':
            time.sleep(4)
            d.click(200,1000)
            time.sleep(8)
            d.xpath("播放全部").click_exists(timeout=1)
            time.sleep(3)
            d.press("home")
            time.sleep(1)
        else:
            time.sleep(2)
            for j in range(81):
                #d.xpath("发现").click_exists(timeout=1)
                time.sleep(1)
                #d.swipe_ext('down')
                time.sleep(1)
                #d.click(200,500)
                d.sleep(6)
                d.xpath("播放全部").click_exists(timeout=2)
                time.sleep(1)
                #d.press("back")
                time.sleep(30 + random.randint(0,5))
                #d.app_start(package,'com.netease.cloudmusic.activity.IconChangeDefaultAlias')
                d.sleep(1)
            """
            d.xpath("动态").click_exists(timeout=1)
            time.sleep(1)
            for i in range(10):
                d.swipe_ext('up')
                time.sleep(0.5)
            """
        ctx.stop()
        if mode not in ['back', 'fore']:
            filename = Trafficsnif.end_pre(package, pcapProcess, checklogin, event, filename)
        else:
            return event,None
        return None, filename

def get_connections(package):
    #方法2，获取日志文件
    cmd = ['pull', '/sdcard/networklog.txt', './networklog.txt']
    Trafficsnif.run_adb_cmd(cmd)
    uidic = {int(getuidByPackage(package,device)):package}
    #方法2，处理日志文件
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
    return connections

def multi_devices_do():
    #activity
    global flow2uid
    packagelist = ['com.tencent.mm', 'com.tencent.mobileqq']
    Host = socket.gethostname()
    print(Host)
    port = 5000 
    address = (Host, port)
    buffer = 1024
    print(Host)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)
    print("启动服务器：发起方")
    server.listen(10)
    for pkg in packagelist:
        for act_do in range(1,3):
            for m in range(12):
                flow2uid = defaultdict(list)
                path = './flow2uidJson/activity/' + pkg
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, str(act_do))
                if not os.path.exists(path):
                    os.mkdir(path)
                if len(os.listdir(path)) >= 12:
                    break
                while True:
                    print("进入循环,等待客户端连接")
                    conn, addr = server.accept()
                    print('连接的客服端套接字对象为：~{}\n客服端的IP地址（拨进电话号码）：{}'.format(conn, addr))
                    
                    send_str = pkg+ '_' + str(act_do)
                    conn.send(send_str.encode('utf-8'))
                    _ ,filename = getattr(Trafficsnif, pkg.replace('.','_'))('normal', act_do)
                    
                    with open(os.path.join(path,filename[:-5] + '.json'), 'w') as f:
                        f.write(js.dumps(flow2uid))
                    time.sleep(2)
                    break

def activity_traffic():
    global flow2uid
    packagelist = ['com.taobao.taobao','com.jingdong.app.mall']
    packagelist = ['com.tencent.mm', 'com.tencent.mobileqq']
    for pkg in packagelist:
        for act_do in range(1,8):
            while True:
                try:
                    for m in range(12):
                        #["com.zhihu.android",'com.tencent.mm'，'tv.danmaku.bili','com.netease.cloudmusic']
                        flow2uid = defaultdict(list)
                        #pkg = 'com.netease.cloudmusic'
                        #backpakage = 'tv.danmaku.bili'
                        path = './flow2uidJson/activity/' + pkg
                        if not os.path.exists(path):
                            os.mkdir(path)
                        path = os.path.join(path, str(act_do))
                        
                        if not os.path.exists(path):
                            os.mkdir(path)
                        
                        if len(os.listdir(path)) >= 12:
                            break
                        _ ,filename = getattr(Trafficsnif, pkg.replace('.','_'))('normal', act_do)
                        
                        with open(os.path.join(path,filename[:-5] + '.json'), 'w') as f:
                            f.write(js.dumps(flow2uid))
                        time.sleep(2)
                    
                    break
                except ReadTimeout:
                    continue

def multi_app_traffic():
    #multi_app
    global flow2uid
    #forelist = ["com.jingdong.app.mall","com.zhihu.android", "com.sina.weibog3"]
    forelist = ["com.baidu.searchbox","com.kmxs.reader", "net.csdn.csdnplus"]
    backlist = ['tv.danmaku.bili',"com.tencent.qqlive",'com.netease.cloudmusic']
    #backlist = ["air.tv.douyu.android",'tv.danmaku.bili',"com.duowan.kiwi"]
    Host = socket.gethostname()
    print(Host)
    port = 5000 
    address = (Host, port)
    buffer = 1024
    print(Host)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)
    print("启动服务器：发起方")
    server.listen(1)
    for forepackage in forelist:
        for backpakage in backlist:
            while True:
                try:
                    for m in range(15):
                        if backpakage in ['com.tencent.mm', 'com.tencent.mobileqq']:
                            while True:
                                print("进入循环,等待客户端连接")
                                conn, addr = server.accept()
                                print('连接的客服端套接字对象为：~{}\n客服端的IP地址（拨进电话号码）：{}'.format(conn, addr))
                                send_str = backpakage+ '_' + str(3)
                                conn.send(send_str.encode('utf-8'))
                                break
                        #["com.zhihu.android",'com.tencent.mm'，'tv.danmaku.bili','com.netease.cloudmusic']
                        flow2uid = defaultdict(list)
                        #backpakage = 'tv.danmaku.bili'
                        path = './flow2uidJson/' + forepackage +'_'  + backpakage
                        if not os.path.exists(path):
                            os.mkdir(path)
                        
                        suffix = '_netlog'
                        log_num = 0
                        for logfile in os.listdir(path):
                            if suffix + '.json' in logfile:
                                log_num += 1
                        if log_num > 29:
                            break
                        connections ,filename = Trafficsnif.backgroud_two_flow(forepackage,backpakage)
                        
                        with open(os.path.join(path,filename[:-5] + suffix + '.json'), 'w') as f:
                            f.write(js.dumps(connections))
                        time.sleep(2)
                        
                    break
                except ReadTimeout:
                    continue

def simple_app_traffic():
    #simple_app
    """
    pkglist = ['com.taobao.taobao', 'com.jingdong.app.mall','com.xunmeng.pinduoduo','com.duowan.kiwi','air.tv.douyu.android'
               ,'com.tencent.qqlive','com.qiyi.video','com.hunantv.imgo.activity',
               'tv.danmaku.bili','com.autonavi.minimap','com.sina.weibog3']
    """
    pkglist = ['com.jingdong.app.mall','net.csdn.csdnplus',
               'com.tencent.qqlive','com.qiyi.video','com.hunantv.imgo.activity',
               'tv.danmaku.bili','com.autonavi.minimap','com.netease.cloudmusic','com.xunmeng.pinduoduo',"com.ss.android.ugc.aweme","com.baidu.searchbox"]
    pkglist += ['com.UCMobile','com.kmxs.reader',
                   'com.smile.gifmaker', 'com.zhihu.android','com.taobao.taobao', 'com.dragon.read','com.sina.weibog3']
    #pkglist = ['com.duowan.kiwi','air.tv.douyu.android']
    for pkg in pkglist:
        while True:
            try:
                for m in range(24):
                    #["com.zhihu.android",'com.tencent.mm'，'tv.danmaku.bili','com.netease.cloudmusic']
                    flow2uid = defaultdict(list)
                    #backpakage = 'tv.danmaku.bili'
                    if not  os.path.exists(flow2uid_path):
                        os.mkdir(flow2uid_path)
                    path = os.path.join(flow2uid_path,pkg)
                    if not os.path.exists(path):
                        os.mkdir(path)
                    if len(os.listdir(path)) > 23:
                        break
                    _ ,filename = getattr(Trafficsnif, pkg.replace('.','_'))(mode='normal')
                    connections = get_connections(pkg)
                    with open(os.path.join(path,filename[:-5] + '_netlog.json'), 'w') as f:
                        f.write(js.dumps(connections))
                    time.sleep(2)
                break
            except ReadTimeout:
                continue

def get_app_info():
# 获取应用的版本信息
    pkglist = ['com.jingdong.app.mall','net.csdn.csdnplus',
               'com.tencent.qqlive','com.qiyi.video','com.hunantv.imgo.activity',
               'tv.danmaku.bili','com.autonavi.minimap','com.sina.weibog3','com.netease.cloudmusic','com.xunmeng.pinduoduo',"com.ss.android.ugc.aweme",'com.taobao.taobao']
    with open('./appversion.txt','w') as f:
        for app in pkglist:
            
            app_info = d.app_info(app)
            version_name = app_info.get("versionName")
            version_code = app_info.get("versionCode")

            f.write(f"{app}\nVersion name: {version_name} ")
            f.write(f"Version code: {version_code}\n")
def reinstall(applist, apppath):
    for i, app in enumerate(applist):
        print(f"processing appname {app}, left: {len(applist) - i + 1}")
        cmd = ['adb','-s', device, 'uninstall', app]
        adbProcess = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = adbProcess.communicate()
        # apkname = app.replace('.', '_') + '.apk'
        apkname = app + '.apk'
        apkpath = os.path.join(apppath,apkname)
        installcmd = ['adb','-s', device, 'install', apkpath]
        adbProcess = subprocess.Popen(installcmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = adbProcess.communicate()
    return ret
if __name__ == "__main__":
    device = "deviceIP:port"
    device = "device_sn"
    d = u2.connect(device)
    host = 'hostIP'
    replace_i = "wlan0"
    replace_i = 'rmnet_data1'
    traffic_path = r'XXX\traffic\Network4G'
    basecmd = ['adb','-s', device, 'shell', 'su','-c','timeout 300']
    goaltime = 300
    flow2uid_path = r'XXX\flow2uidJson\Network4G'
    flow2uid = defaultdict(list)
    pkglist = ['com.jingdong.app.mall','net.csdn.csdnplus',
               'com.tencent.qqlive','com.qiyi.video','com.hunantv.imgo.activity',
               'tv.danmaku.bili','com.autonavi.minimap','com.netease.cloudmusic','com.xunmeng.pinduoduo',"com.ss.android.ugc.aweme","com.baidu.searchbox"]
    pkglist += ['com.UCMobile','com.kmxs.reader', 'com.dragon.read',
                   'com.smile.gifmaker', 'com.zhihu.android','com.sina.weibog3','com.taobao.taobao']

    #multi_app_traffic()
    simple_app_traffic()
    #installtest()
    #get_app_info()