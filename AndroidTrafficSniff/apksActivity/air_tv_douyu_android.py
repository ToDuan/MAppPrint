import time
import random
#斗鱼直播流量采集动作函数
def air_tv_douyu_android(mode, d, goaltime):
    ctx = d.watch_context()
    ctx.when("允许").click()
    ctx.when("跳过").click()
    ctx.when("同意").click()
    ctx.when("等待").click()
    ctx.when("忽略").click()
    ctx.when("稍后再说").click()
    ctx.when("下次再说").click()
    ctx.when("确定").click()
    ctx.when("同意并继续").click()
    ctx.when("我知道了").click()
    ctx.when('0.01元参与').call(lambda d : d.click(894,501))
    ctx.when("狠心离开").click()
    ctx.when("残忍离开").click()
    ctx.when("不感兴趣").click()
    ctx.wait_stable() # 等待界面不在有弹窗了
    start_time = time.time()
    act = random.randint(0,1)
    act = 0
    def act1():
        for i in range(5):
            d.swipe_ext('up')
            time.sleep(60)
    def act2():
        time.sleep(2)
        d.click(250,1100)
        time.sleep(300)
    act_funcs = {
        0:act1,
        1:act2
    }
    if mode == 'back':
        while True:
            try:
                d.xpath('首页').click()
                break
            except:
                continue
        time.sleep(5)
        d.xpath('//*[@resource-id="air.tv.douyu.android:id/kc_"]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]').click_exists(timeout=1)
        time.sleep(4)
        d.press('home')
        time.sleep(1)
    else:
        while time.time() - start_time < goaltime:
            #func = act_funcs[act % 2]
            func = act_funcs[0]
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