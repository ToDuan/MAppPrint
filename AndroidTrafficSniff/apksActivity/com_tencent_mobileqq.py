import time
import random
from ..adb_test import generate_message
#腾讯QQ流量采集动作函数
def com_tencent_mobileqq(mode, d, goaltime, act_do=0, commu_name='龙的分身LG2'):
    # package = "com.tencent.mobileqq"
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
