import time
import random
from ..adb_test import generate_message
#微信流量采集动作函数
def com_tencent_mm(mode, d, goaltime, act_do=0, commu_name='ljl1'):
    # package = "com.tencent.mm"
   
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