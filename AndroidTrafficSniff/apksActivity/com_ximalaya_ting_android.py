import time
import random
#喜马拉雅听书流量采集动作函数
def com_ximalaya_ting_android(mode, d, goaltime):
    # package = "com.ximalaya.ting.android"
    
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