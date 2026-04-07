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
            print("正在访问 NodeLoc 首页...")
            page.goto('https://www.nodeloc.com/', timeout=60000, wait_until='domcontentloaded')
            time.sleep(3)

            login_btn = page.locator('.login-button')
            if login_btn.count() > 0:
                print("找到登录按钮，正在点击打开登录弹窗...")
                login_btn.first.click()
                time.sleep(2) 

                print("正在输入账号信息...")
                page.fill('#login-account-name', username)
                page.fill('#login-account-password', password)
                
                print("正在提交登录请求...")
                page.click('#login-button')

                print("等待登录完成...")
                time.sleep(6) 
            else:
                print("⚠️ 未找到首页的登录按钮，可能是页面结构变更，或已处于登录状态。")

            # ================= 检查登录状态并签到 =================
            print("正在刷新页面检查状态...")
            page.goto('https://www.nodeloc.com/', timeout=60000, wait_until='domcontentloaded') 
            time.sleep(5) # 多等一会，确保签到插件加载完毕
            
            if page.locator('.current-user').count() > 0 or page.locator('#current-user').count() > 0:
                print("✅ 登录成功！")
                
                # 检查是否已经签到
                if page.locator("text=已签到").count() > 0:
                    print("🎉 检查结果: 今日已签到，无需重复操作。")
                else:
                    print("🔍 正在寻找签到按钮...")
                    # 核心修改：限定必须是按钮（button标签 或 带有btn类名），并且包含“签到”文本
                    checkin_btn = page.locator('button, .btn, .d-button').filter(has_text="签到")
                    
                    if checkin_btn.count() > 0:
                        checkin_btn.first.click()
                        print("🚀 成功点击签到按钮！等待服务器响应...")
                        
                        # 等待网络请求完成，确保 AJAX 请求发送成功
                        page.wait_for_load_state('networkidle', timeout=10000)
                        time.sleep(3) 
                        
                        # 【复查机制】：点击后再次检查页面上是否有“已签到”
                        if page.locator("text=已签到").count() > 0:
                            print("🎉 签到状态已成功变更为'已签到'，流程完美结束！")
                        else:
                            print("⚠️ 警告：虽然点击了，但状态没有变成'已签到'。可能是：1. 点击了错误的元素 2. 需要滑动验证码拦截了 3. 签到弹出了二次确认框。")
                    else:
                        print("⚠️ 找不到可点击的签到按钮。")
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
