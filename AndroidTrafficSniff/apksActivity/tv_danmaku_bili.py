import time
import random
#b站流量采集动作函数
def tv_danmaku_bili(mode, d, goaltime):
    # package = "tv.danmaku.bili"
    
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