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

            # 点击右上角登录按钮
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
                time.sleep(8) 
            else:
                print("⚠️ 未找到首页的登录按钮，可能是已处于登录状态。")

            # ================= 检查登录状态并签到 =================
            print("正在刷新页面确保状态更新...")
            page.goto('https://www.nodeloc.com/', timeout=60000, wait_until='domcontentloaded') 
            time.sleep(5) 
            
            # 判断是否登录成功
            if page.locator('.current-user').count() > 0 or page.locator('#current-user').count() > 0:
                print("✅ 登录成功！")
                
                print("🔍 正在右上角寻找签到日历图标...")
                # 【核心修改】：直接通过 title 属性（鼠标悬停提示词）来定位那个日历图标！
                checkin_icon = page.locator('[title*="签到"]')
                
                if checkin_icon.count() > 0:
                    # 获取当前的悬停提示文字
                    hover_text = checkin_icon.first.get_attribute('title')
                    print(f"找到图标！当前状态显示为: [{hover_text}]")
                    
                    if "已签到" in hover_text:
                        print("🎉 今日已签到，无需重复操作。")
                    else:
                        print("👉 尝试点击签到图标...")
                        checkin_icon.first.click()
                        time.sleep(3) # 等待签到请求发送和页面状态刷新
                        
                        # 【点击后的二次处理】
                        # 有些论坛点完日历图标后，还会弹出一个弹窗让你再点一次"签到"按钮
                        confirm_btn = page.locator('.d-modal button').filter(has_text="签到")
                        if confirm_btn.count() > 0 and confirm_btn.first.is_visible():
                            print("发现二次确认弹窗，正在点击确认...")
                            confirm_btn.first.click()
                            time.sleep(3)
                        
                        # 再次获取悬停提示，检查是否变成了"已签到"
                        new_hover_text = checkin_icon.first.get_attribute('title')
                        if new_hover_text and "已签到" in new_hover_text:
                            print("🎉 签到成功！状态已完美更新。")
                        else:
                            print("✅ 已执行点击操作，请留意账号积分是否增加。")
                else:
                    print("❌ 找不到右上角的签到图标，可能是页面还没加载完。")
            else:
                print("❌ 登录失败，请检查账号密码或是否遇到了安全验证拦截。")

        except Exception as e:
            print(f"执行过程中出现错误: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    auto_login_and_checkin()
