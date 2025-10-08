import time
import random
#CSDN流量采集动作函数
def net_csdn_csdnplus(mode, d , goaltime):
    # package = "net.csdn.csdnplus"
    ctx = d.watch_context()
    ctx.when("允许").click()
    ctx.when("跳过").click()
    ctx.when("以后再说").click()
    ctx.when("同意").click()
    ctx.when("同意并继续").click()
    ctx.when("我知道了").click()
    ctx.when("手机号登录").call(lambda d: d.press("back"))
    ctx.wait_stable() # 等待界面不在有弹窗了
    start_time = time.time()
    act = random.randint(0,1)
    act = 0
    def act1():
        for i in range(20):
            d.swipe_ext('up')
            time.sleep(5)
    def act2():
        time.sleep(4)
        d.xpath('//*[@resource-id="net.csdn.csdnplus:id/fl_container"]/android.widget.LinearLayout[1]/androidx.viewpager.widget.ViewPager[1]/android.widget.LinearLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]/android.view.ViewGroup[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[2]').click_exists(timeout=1)
        time.sleep(4)
        for j in range(12):
            d.swipe_ext("up")
            time.sleep(5)
    act_funcs = {
        0:act1,
        1:act2
    }
    if mode =='back':
        time.sleep(4)
        d.press('home')
        time.sleep(1)
    else:
        while time.time() - start_time < goaltime:
            if mode == 'fore':
                act = 0
            func = act_funcs[act % 2]
            func()
            t = True
            while t:
                try:
                    d.xpath('//*[@resource-id="net.csdn.csdnplus:id/ll_bar_content"]/android.widget.LinearLayout[1]').click(timeout=1)
                    t = False
                except:
                    d.press('back')
                    time.sleep(1)
            time.sleep(5)
            act += 1                    
    ctx.stop()