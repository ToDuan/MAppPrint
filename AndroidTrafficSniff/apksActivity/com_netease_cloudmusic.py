import time
import random
#网易云音乐流量采集动作函数
def com_netease_cloudmusic(mode, d, goaltime):
    # package = "com.netease.cloudmusic"
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
