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

            # ================= 登录流程 =================
            login_btn = page.locator('.login-button')
            if login_btn.count() > 0:
                print("找到登录按钮，正在打开登录弹窗...")
                login_btn.first.click()
                time.sleep(2) 

                page.fill('#login-account-name', username)
                page.fill('#login-account-password', password)
                page.click('#login-button')
                time.sleep(6) 
            else:
                print("⚠️ 未找到首页的登录按钮，尝试直接检查是否已登录。")

            # 刷新页面确保拿到登录后的 Cookie
            page.goto('https://www.nodeloc.com/', timeout=60000, wait_until='domcontentloaded') 
            time.sleep(4) 
            
            # ================= 签到流程 =================
            if page.locator('.current-user').count() > 0 or page.locator('#current-user').count() > 0:
                print("✅ 登录成功！")
                
                print("🔍 正在使用精确 CSS 选择器寻找签到按钮...")
                # 照搬 Selenium 脚本的终极选择器
                checkin_selector = "li.header-dropdown-toggle.checkin-icon button.checkin-button"
                checkin_btn = page.locator(checkin_selector)
                
                if checkin_btn.count() > 0:
                    btn = checkin_btn.first
                    
                    # 照搬判定逻辑：检查是否有 checked-in 类名或 disabled 属性
                    class_attr = btn.get_attribute("class") or ""
                    is_disabled = btn.is_disabled()
                    
                    if "checked-in" in class_attr or is_disabled:
                        print("🎉 检查结果: 今日已签到，无需重复操作。")
                    else:
                        print("👉 尝试执行签到...")
                        # 模仿 Selenium 触发 Hover
                        btn.hover()
                        time.sleep(1)
                        
                        # 照搬最狠的点击方式：直接注入 JS 触发点击，无视一切前端拦截
                        btn.evaluate("node => node.click()")
                        print("🚀 JS 点击命令已发送，等待服务器响应...")
                        time.sleep(4) 
                        
                        # 再次获取状态，复查是否签到成功
                        class_attr_after = btn.get_attribute("class") or ""
                        is_disabled_after = btn.is_disabled()
                        
                        if "checked-in" in class_attr_after or is_disabled_after:
                            print("🎉 签到大成功！(按钮状态已变为已签到)")
                        else:
                            print("⚠️ 点击已执行，但按钮状态未变。请留意账号积分是否增加。")
                else:
                    print("❌ 找不到签到按钮，请检查论坛是否更换了前端主题或结构。")
            else:
                print("❌ 登录失败，请检查账号密码或验证码拦截。")

        except Exception as e:
            print(f"执行过程中出现错误: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    auto_login_and_checkin()
