import time
import random
#芒果TV流量采集动作函数

def com_hunantv_imgo_activity(mode, d, goaltime):
    # package = "com.hunantv.imgo.activity"
    
    ctx = d.watch_context()
    ctx.when("允许").click()
    ctx.when("跳过").click()
    ctx.when("同意").click()
    ctx.when("确定").click()
    ctx.when("忽略").click()
    ctx.when("同意并继续").click()
    ctx.when("我知道了").click()
    ctx.when('0.01元参与').call(lambda d : d.click(894,501))
    ctx.when("com.hunantv.imgo.activity:id/ivJbpFirstPopClose").click()
    ctx.when("com.hunantv.imgo.activity:id/btnClose").click()
    ctx.when("狠心离开").click()
    ctx.when("同意开启").click()
    ctx.when("不感兴趣").click()
    ctx.wait_stable() # 等待界面不在有弹窗了
    start_time = time.time()
    act = random.randint(0,1)
    act = 0
    def act1():
        d.xpath('返回顶部').click_exists(timeout=1)
        time.sleep(3)
        d.xpath('电影').click_exists(timeout=1)
        time.sleep(10)
        for i in range(random.randint(1,3)):
            d.swipe_ext('up')
            d.sleep(2)
        d.xpath('//android.support.v7.widget.RecyclerView/android.widget.LinearLayout[2]/android.widget.LinearLayout[2]/android.widget.RelativeLayout[1]').click_exists(timeout=1)
        #d.click(268,1707)
        time.sleep(280)
    def act2():
        d.xpath('短视频').click_exists(timeout=1)
        time.sleep(5)
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
                    d.xpath('//*[@resource-id="com.hunantv.imgo.activity:id/tab_host_index"]/android.widget.RelativeLayout[1]/android.view.View[1]').click_exists(timeout=1)
                    t = False
                except:
                    d.press('back')
                    time.sleep(1)
            time.sleep(5)
            act += 1
                
    ctx.stop()
