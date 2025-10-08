import time
import random
#高德地图流量采集动作函数
def com_autonavi_minimap(mode, d, goaltime):
    # package = "com.autonavi.minimap"
    time.sleep(2)
    ctx = d.watch_context()
    ctx.when("允许").click()
    ctx.when("跳过").click()
    ctx.when("同意").click()
    ctx.when("com.autonavi.minimap:id/iv_close").click()
    ctx.when("同意并继续").click()
    ctx.when("我知道了").click()
    ctx.when("取消").click()
    ctx.wait_stable() # 等待界面不在有弹窗了
    start_time = time.time()
    act = random.randint(0,2)
    act = 0
    def act1():
        dolist = ['up', 'down','left', 'right']
        for i in range(24):
            rnd = random.randint(0,3)
            d.swipe_ext(dolist[rnd])
            time.sleep(5)
    def act2():
        time.sleep(2)
        d.xpath('附近').click_exists(timeout=1)
        
        for i in range(24):
            d.swipe_ext('up')
            time.sleep(5)
    def act3():
        d.xpath("实时公交").click_exists(timeout=1)
        time.sleep(6)
        for i in range(10):
            d.swipe_ext('up')
            time.sleep(5)
    act_funcs = {
        0:act1,
        1:act2,
        2:act3,
    }
    if mode == 'back':
        time.sleep(2)
        d.press('home')
        time.sleep(1)
    else:
        time.sleep(5)
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
    ctx.stop()