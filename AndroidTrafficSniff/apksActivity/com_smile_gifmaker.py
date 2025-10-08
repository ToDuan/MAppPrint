import time
import random
#快手流量采集动作函数
def com_smile_gifmaker(mode,d , goaltime):
    package = "com.smile.gifmaker"
    ctx = d.watch_context()
    ctx.when("允许").click()
    ctx.when("跳过").click()
    ctx.when("同意").click()
    ctx.when("取消").click()
    ctx.when("同意并继续").click()
    ctx.when("我知道了").click()
    ctx.when("以后再说").click()
    ctx.when("手机号登录").call(lambda d: d.press("back"))
    ctx.wait_stable() # 等待界面不在有弹窗了
    start_time = time.time()
    t = True
    act = random.randint(0,1)
    act = 0
    start_time = time.time()
    def act1():
        for i in range(4):
            d.swipe(0.5, 0.8, 0.6, 0.3, 0.2)
            time.sleep(30 + random.randint(5, 8))
    def act2():
        d(resourceId="com.smile.gifmaker:id/comment_icon").click_exists(timeout=1)
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