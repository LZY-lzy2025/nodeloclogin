import os
import time
from playwright.sync_api import sync_playwright

def auto_login_and_checkin():
    username = os.environ.get('NODELOC_USERNAME')
    password = os.environ.get('NODELOC_PASSWORD')

    if not username or not password:
        print("错误: 未找到账号或密码，请检查 GitHub Secrets 配置。")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled'] 
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        try:
            # 策略改变：直接访问首页，通过点击右上角的按钮唤出登录弹窗
            print("正在访问 NodeLoc 首页...")
            page.goto('https://www.nodeloc.com/', timeout=60000, wait_until='domcontentloaded')
            time.sleep(3)

            # 查找并点击首页右上角的“登录”按钮（Discourse 默认类名为 .login-button）
            login_btn = page.locator('.login-button')
            if login_btn.count() > 0:
                print("找到登录按钮，正在点击打开登录弹窗...")
                login_btn.first.click()
                time.sleep(2) # 等待弹窗动画出现

                print("正在输入账号信息...")
                # Discourse 弹窗里的标准输入框 ID 是 login-account-name
                page.fill('#login-account-name', username)
                page.fill('#login-account-password', password)
                
                print("正在提交登录请求...")
                # 点击弹窗里的登录确认按钮
                page.click('#login-button')

                print("等待登录完成...")
                time.sleep(6) # 给接口鉴权和页面刷新一点时间
            else:
                print("⚠️ 未找到首页的登录按钮，可能是页面结构变更，或已处于登录状态。")

            # ================= 检查登录状态并签到 =================
            print("正在刷新页面检查状态...")
            page.goto('https://www.nodeloc.com/', timeout=60000, wait_until='domcontentloaded') 
            time.sleep(4) 
            
            # Discourse 登录后右上角会显示用户头像菜单，通常带有 .current-user 类名
            if page.locator('.current-user').count() > 0 or page.locator('#current-user').count() > 0:
                print("✅ 登录成功！")
                
                # 检查签到
                # 这里去掉了 exact=True，为了兼容可能叫"每日签到"或"签到"的情况
                if page.locator("text=已签到").count() > 0:
                    print("🎉 检查结果: 今日已签到，无需重复操作。")
                else:
                    checkin_btn = page.locator("text=签到")
                    if checkin_btn.count() > 0:
                        checkin_btn.first.click()
                        print("🚀 成功点击签到按钮！")
                        time.sleep(3) 
                        print("🎉 签到流程执行完毕。")
                    else:
                        print("⚠️ 未找到包含[签到]字样的按钮，可能论坛今日未开启签到，或按钮在更深的菜单里。")
            else:
                print("❌ 登录可能失败，遇到了验证码或账号密码错误。")
                print(f"当前页面 URL: {page.url}")

        except Exception as e:
            print(f"执行过程中出现错误: {e}")
            print(f"崩溃时停留的 URL: {page.url}")
        finally:
            browser.close()

if __name__ == "__main__":
    auto_login_and_checkin()
