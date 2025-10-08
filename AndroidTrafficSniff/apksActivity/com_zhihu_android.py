import time
import random
#知乎流量采集动作函数
def com_zhihu_android(mode, d, goaltime):
        # package = "com.zhihu.android"
        ctx = d.watch_context()
        ctx.when("允许").click()
        ctx.when("等待").click()
        ctx.when("跳过").click()
        ctx.when("同意").click()
        ctx.when("取消").click()
        ctx.when("同意并继续").click()
        ctx.when("我知道了").click()
        ctx.when("com.zhihu.android:id/iv_close").click()
        ctx.when("手机号登录").call(lambda d: d.press("back"))
        ctx.wait_stable() # 等待界面不在有弹窗了
        start_time = time.time()
        act = random.randint(0,1)
        act = 0
        def act1():
            for i in range(20):
                d.swipe_ext('up')
                time.sleep(6)
        def act2():
            time.sleep(4)
            d.click(333,814)
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
                d.app_start('com.zhihu.android','com.zhihu.android.app.ui.activity.MainActivity')
                
                time.sleep(5)
                act += 1                    
        ctx.stop()