import time
import random
#拼多多直播流量采集动作函数
def com_xunmeng_pinduoduo(mode, d, goaltime):
    # package = "com.xunmeng.pinduoduo"
    
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