import time
import random
#QQ音乐流量采集动作函数
def com_tencent_qqmusic(mode,d ,goaltime):
    # package = "com.tencent.qqmusic"

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
