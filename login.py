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
        # 启动浏览器时加入伪装参数，降低被 Cloudflare 拦截的概率
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
            print("正在访问 NodeLoc 登录页面...")
            # 修改 1：将超时时间延长到 60 秒
            # 修改 2：等待状态改为 domcontentloaded（只要 HTML 骨架加载完就算成功，不管后台那些长连接脚本）
            page.goto('https://www.nodeloc.com/login', timeout=60000, wait_until='domcontentloaded')
            
            # 强制等待 3 秒，确保登录框渲染出来
            time.sleep(3)

            print("正在输入账号信息...")
            # 检查元素是否存在，避免直接 fill 报错
            if page.locator('#signin_username').count() == 0:
                print("⚠️ 找不到登录框！可能是被 Cloudflare 拦截了，请查看当前 URL 或尝试更换网络环境。")
                print(f"当前页面 URL: {page.url}")
                return

            page.fill('#signin_username', username)
            page.fill('#signin_password', password)
            
            print("正在提交登录请求...")
            page.click('#signin-button')

            # 同样使用 domcontentloaded
            page.wait_for_load_state('domcontentloaded', timeout=60000)
            time.sleep(5) # 给接口鉴权一点时间
            
            if page.locator('#current-user').count() > 0 or "login" not in page.url:
                print("✅ 登录成功！")
                
                print("正在前往首页检查签到状态...")
                page.goto('https://www.nodeloc.com/', timeout=60000, wait_until='domcontentloaded') 
                time.sleep(4) 

                if page.get_by_text("已签到", exact=True).count() > 0:
                    print("🎉 检查结果: 今日已签到，无需重复操作。")
                else:
                    checkin_btn = page.get_by_text("签到", exact=True)
                    if checkin_btn.count() > 0:
                        checkin_btn.first.click()
                        print("🚀 成功点击签到按钮！")
                        time.sleep(3) 
                        print("🎉 签到流程执行完毕。")
                    else:
                        print("⚠️ 未找到[签到]或[已签到]按钮。")

            else:
                print("❌ 登录可能失败，遇到了验证码或账号密码错误。")
                print(f"当前页面 URL: {page.url}")

        except Exception as e:
            print(f"执行过程中出现错误: {e}")
            # 如果依然报错，打印出当前停留的页面 URL，方便排查
            print(f"崩溃时停留的 URL: {page.url}")
        finally:
            browser.close()

if __name__ == "__main__":
    auto_login_and_checkin()
