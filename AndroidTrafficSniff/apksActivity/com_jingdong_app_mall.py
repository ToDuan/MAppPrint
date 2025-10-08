import time
import random
#京东流量采集动作函数
def com_jingdong_app_mall(mode,d, goaltime, act_do = 0):
    
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