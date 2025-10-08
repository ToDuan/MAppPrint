import time
import random
#爱奇艺视频流量采集动作函数
def com_qiyi_video(mode, d, goaltime):
    # package = "com.qiyi.video"

    ctx = d.watch_context()
    ctx.when("允许").click()
    ctx.when("跳过").click()
    ctx.when("同意").click()
    ctx.when("确定").click()
    ctx.when("确认").click()
    ctx.when("同意并继续").click()
    ctx.when("我知道了").click()
    ctx.when('0.01元参与').call(lambda d : d.click(894,501))
    ctx.when("狠心离开").click()
    # ctx.when("不感兴趣").click()
    ctx.wait_stable() # 等待界面不在有弹窗了
    start_time = time.time()
    act = random.randint(0,1)
    act = 0
    def act1():
        d.click(274,1060)
        time.sleep(600)
    def act2():
        d.xpath('随刻视频').click_exists(timeout=1)
        time.sleep(2)
        for i in range(20):
            time.sleep(30)
            d.swipe_ext('up')
    act_funcs = {
        0:act1,
        1:act2
    }
    if mode == 'back':
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