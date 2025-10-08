import time
import random
#腾讯视频流量采集动作函数
def com_tencent_qqlive(mode, d, goaltime):
    # package = "com.tencent.qqlive"

    ctx = d.watch_context()
    ctx.when("允许").click()
    ctx.when("跳过").click()
    ctx.when("同意").click()
    ctx.when("确定").click()
    ctx.when("同意并继续").click()
    ctx.when("我知道了").click()
    ctx.when('0.01元参与').call(lambda d : d.click(894,501))
    ctx.when("狠心离开").click()
    ctx.when("不感兴趣").click()
    ctx.wait_stable() # 等待界面不在有弹窗了
    start_time = time.time()
    act = random.randint(0,1)
    act = 0
    def act1():
        d.xpath('返回顶部').click_exists(timeout=1)
        time.sleep(10)
        #d.xpath('电影').click_exists(timeout=1)
        #time.sleep(10)
        d.xpath(f'//androidx.viewpager.widget.ViewPager/android.widget.RelativeLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.FrameLayout[{random.randint(1,4)}]/android.view.ViewGroup[1]/android.view.ViewGroup[1]').click_exists(timeout=1)
        d.click(268,1707)
        time.sleep(300)
    def act2():
        d.xpath('短片').click_exists(timeout=1)
        time.sleep(2)
        for i in range(20):
            time.sleep(30)
            d.swipe_ext('up')
    act_funcs = {
        0:act1,
        1:act2
    }
    if mode == 'back':
        while True:
            try:
                d.xpath('首页').click()
                time.sleep(3)
                break
            except:
                continue
        d.xpath('电视剧').click_exists(timeout=1)
        time.sleep(5)
        d.xpath(f'//androidx.viewpager.widget.ViewPager/android.widget.RelativeLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.FrameLayout[{random.randint(2,5)}]/android.view.ViewGroup[1]/android.view.ViewGroup[1]').click_exists(timeout=1)
        time.sleep(3)
        d.press('home')
        time.sleep(1)
    else:
        while time.time() - start_time < goaltime:
            if act == 1:
                continue
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