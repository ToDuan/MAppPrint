import time
import random
#百度流量采集动作函数
def com_baidu_searchbox(mode,d ,goaltime):
    # package = "com.baidu.searchbox"
    
    ctx = d.watch_context()
    ctx.when("允许").click()
    ctx.when("跳过").click()
    ctx.when("以后再说").click()
    ctx.when("同意").click()
    ctx.when("确定").click()
    ctx.when("同意并继续").click()
    ctx.when("我知道了").click()
    ctx.when('0.01元参与').call(lambda d : d.click(894,501))
    ctx.when("狠心离开").click()
    #ctx.when("不感兴趣").click()
    ctx.wait_stable() # 等待界面不在有弹窗了
    start_time = time.time()
    act = random.randint(0,1)
    act = 0
    def act2():
        for i in range(12):
            time.sleep(5)
            d.swipe_ext('up')
    def act1():
        for i in range(3):
            d.swipe_ext('up')
            time.sleep(4)
        time.sleep(3)
        d.xpath('//androidx.recyclerview.widget.RecyclerView/android.widget.RelativeLayout[1]').click_exists(timeout=1)
        time.sleep(5)
        for i in range(10):
            time.sleep(5)
            d.swipe_ext('up')
    def act3():
        d.xpath('//*[@resource-id="android:id/tabcontent"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[2]').click_exists(timeout=1)
        time.sleep(3)
        d(resourceId="com.baidu.searchbox:id/obfuscated", text="搜索").click_exists(timeout=1)
        time.sleep(5)
        for i in range(20):
            d.swipe_ext('up')
            time.sleep(5)
    act_funcs = {
        0:act1,
        1:act2,
        2:act3
    }
    if mode == 'back':
        time.sleep(2)
        d.press('home')
        time.sleep(1)
    else:
        while time.time() - start_time < goaltime:
            if mode == 'fore':
                act = random.randint(1,2)
            func = act_funcs[act % 3]
            func()
            d.app_start('com.baidu.searchbox', 'com.baidu.searchbox.MainActivity')
            time.sleep(5)
            act += 1
                
    ctx.stop()
