import time
import random
#淘宝流量采集动作函数
def com_taobao_taobao(mode, d, goaltime, act_do = 0):
        # package = "com.taobao.taobao"
       
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