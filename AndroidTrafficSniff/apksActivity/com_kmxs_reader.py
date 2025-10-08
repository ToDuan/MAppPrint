import time
import random
#七猫免费小说流量采集动作函数
def com_kmxs_reader(mode, d , goaltime):
    # package = "com.kmxs.reader"

    ctx = d.watch_context()
    ctx.when("允许").click()
    ctx.when("跳过").click()
    ctx.when("同意").click()
    ctx.when("确定").click()
    ctx.when("同意并继续").click()
    ctx.when("我知道了").click()
    ctx.when("知道了").click()
    ctx.when('0.01元参与').call(lambda d : d.click(894,501))
    ctx.when("狠心离开").click()
    ctx.when("以后再说").click()
    ctx.when("残忍离开").click()
    ctx.when("稍后再说").click()
    ctx.when("下次再说").click()
    ctx.when("com.kmxs.reader:id/close_red_packet").click()
    ctx.when("com.kmxs.reader:id/iv_close_bonus").click()
    
    ctx.when("com.kmxs.reader:id/img_close_dialog").click()
    ctx.wait_stable() # 等待界面不在有弹窗了
    start_time = time.time()
    act = random.randint(0,1)
    act = 0
    def act1():
        #书城浏览
        for i in range(20):
            time.sleep(6)
            d.swipe_ext('up')
    def act2():
        #长时间阅读
        d.xpath('推荐').click_exists(timeout=1)
        time.sleep(5)
        d.xpath('//*[@resource-id="com.kmxs.reader:id/book_store_view_pager"]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.view.ViewGroup[3]').click_exists(timeout=1)
        time.sleep(5)
        for i in range(20):
            d.swipe_ext('left')
            time.sleep(10)
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
                try:
                    d.xpath('书城').click(timeout=1)
                    t = False
                except:
                    d.press('back')
                    time.sleep(1)
                    continue
            time.sleep(5)
            act += 1
                
    ctx.stop()