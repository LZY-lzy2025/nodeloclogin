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
                time.sleep(8) 
            else:
                print("⚠️ 未找到首页的登录按钮，可能是已处于登录状态。")

            # ================= 检查登录状态并签到 =================
            print("正在刷新页面确保状态更新...")
            page.goto('https://www.nodeloc.com/', timeout=60000, wait_until='domcontentloaded') 
            time.sleep(5) 
            
            if page.locator('.current-user').count() > 0 or page.locator('#current-user').count() > 0:
                print("✅ 登录成功！")
                
                print("🔍 正在右上角寻找签到日历图标...")
                checkin_icon = page.locator('[title*="签到"]')
                
                if checkin_icon.count() > 0:
                    hover_text = checkin_icon.first.get_attribute('title')
                    print(f"找到图标！当前状态显示为: [{hover_text}]")
                    
                    if "已签到" in hover_text:
                        print("🎉 今日已签到，无需重复操作。")
                    else:
                        print("👉 尝试点击签到图标...")
                        checkin_icon.first.click()
                        time.sleep(3) 
                        
                        # 处理可能出现的二次确认弹窗
                        confirm_btn = page.locator('.d-modal button').filter(has_text="签到")
                        if confirm_btn.count() > 0 and confirm_btn.first.is_visible():
                            print("发现二次确认弹窗，正在点击确认...")
                            confirm_btn.first.click()
                            time.sleep(3)
                        
                        # 获取点击后的提示文字
                        new_hover_text = checkin_icon.first.get_attribute('title')
                        print(f"🔄 点击操作后的图标状态变为: [{new_hover_text}]")
                        
                        # 很多时候前端提示不会立刻变化，所以我们强制刷新一次页面做最终确认
                        print("正在刷新页面进行最终确认...")
                        page.reload(timeout=60000, wait_until='domcontentloaded')
                        time.sleep(4)
                        
                        final_icon = page.locator('[title*="签到"]')
                        if final_icon.count() > 0:
                            final_text = final_icon.first.get_attribute('title')
                            print(f"🏁 刷新页面后，最终的图标状态为: [{final_text}]")
                            
                            if "已签到" in final_text:
                                print("🎉 签到大成功！")
                            else:
                                print("⚠️ 签到可能未成功，请根据上述最终状态排查原因。")
                        else:
                            print("⚠️ 刷新后找不到了签到图标。")
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
