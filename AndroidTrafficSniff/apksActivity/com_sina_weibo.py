import time
import random
#微博流量采集动作函数
def com_sina_weibo(mode, d, goaltime, act_do=0):
    # package = "com.sina.weibo"
    
    
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