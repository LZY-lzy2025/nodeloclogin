import os
import time
from playwright.sync_api import sync_playwright

def auto_login_and_checkin():
    # 从 GitHub Secrets 获取账号和密码
    username = os.environ.get('NODELOC_USERNAME')
    password = os.environ.get('NODELOC_PASSWORD')

    if not username or not password:
        print("错误: 未找到账号或密码，请检查 GitHub Secrets 配置。")
        return

    with sync_playwright() as p:
        # 启动 Chromium 无头浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("正在访问 NodeLoc 登录页面...")
            page.goto('https://www.nodeloc.com/login', timeout=30000)
            page.wait_for_load_state('networkidle')

            print("正在输入账号信息...")
            page.fill('#signin_username', username)
            page.fill('#signin_password', password)
            
            print("正在提交登录请求...")
            page.click('#signin-button')

            # 等待页面跳转或加载完成
            page.wait_for_load_state('networkidle')
            time.sleep(5) # 额外等待，确保 Cookie 写入
            
            # 验证登录状态
            if page.locator('#current-user').count() > 0 or "login" not in page.url:
                print("✅ 登录成功！")
                
                # ================= 开始签到逻辑 =================
                print("正在前往首页检查签到状态...")
                page.goto('https://www.nodeloc.com/') 
                page.wait_for_load_state('networkidle')
                time.sleep(3) # 等待页面 DOM 和插件完全渲染

                # 1. 检查是否已经签到
                if page.get_by_text("已签到", exact=True).count() > 0:
                    print("🎉 检查结果: 今日已签到，无需重复操作。")
                else:
                    # 2. 没签到的话，找“签到”按钮并点击
                    checkin_btn = page.get_by_text("签到", exact=True)
                    if checkin_btn.count() > 0:
                        # 可能会有多个匹配的元素，点击第一个可见的
                        checkin_btn.first.click()
                        print("🚀 成功点击签到按钮！")
                        time.sleep(3) # 等待签到接口请求完成
                        print("🎉 签到流程执行完毕。")
                    else:
                        print("⚠️ 未找到[签到]或[已签到]按钮，可能页面结构有变或今天没有签到权限。")
                # ================================================

            else:
                print("❌ 登录可能失败，遇到了验证码或账号密码错误。")
                print(f"当前页面 URL: {page.url}")

        except Exception as e:
            print(f"执行过程中出现错误: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    auto_login_and_checkin()
