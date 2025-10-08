import time
import random
#抖音流量采集动作函数
def com_ss_android_ugc_aweme(mode, d, goaltime):
    package = "com.ss.android.ugc.aweme"
  
    d.app_start(package,'.splash.SplashActivity')
    ctx = d.watch_context()
    ctx.when("允许").click()
    ctx.when("跳过").click()
    ctx.when("同意").click()
    ctx.when("关闭").click()
    ctx.when("以后再说").click()
    ctx.when("同意并继续").click()
    ctx.when("我知道了").click()
    ctx.when("我要投广告").call(lambda d: d.press("back"))
    ctx.when("登录").call(lambda d: d.press("back"))
    ctx.when("密码登录").call(lambda d: d.press("back"))
    ctx.wait_stable() # 等待界面不在有弹窗了
    d.implicitly_wait(10)
    width, height = d.window_size()
    time.sleep(2)
    start_time = time.time()
    t = True
    act = random.randint(0,1)
    act = 0
    start_time = time.time()
    def act1():
        for i in range(10):
            d.swipe_ext('up')
            time.sleep(30 + random.randint(5, 8))
    def act2():
        d.xpath('评论%').click_exists(timeout=1)
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
            func = act_funcs[act % 2]
            func()
            d.press('back')
            time.sleep(4)
            d.press('back')
            time.sleep(4)
            act += 1
    ctx.stop()