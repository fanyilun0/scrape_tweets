#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推特列表监听脚本
监听指定推特列表中的新推文，并通过webhook推送
"""

import re
import time
import os
import requests
import random
import json
import asyncio
import base64
from datetime import datetime
from io import BytesIO
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# 导入配置和webhook模块
try:
    from config import (
        CHROME_PROXY, USE_PERSISTENT_PROFILE, PROFILE_DIR,
        PUSHED_IDS_FILE, LIST_CHECK_INTERVAL, MAX_TWEETS_PER_CHECK
    )
    from webhook import send_message_async, send_image_async
except ImportError as e:
    print(f"❌ 导入配置失败: {e}")
    print("请确保 config.py 和 webhook.py 文件存在")
    exit(1)

# ==================== 配置区域 ====================
# 要监听的推特列表URL（可以配置多个）
TWITTER_LISTS = [
    "https://x.com/i/lists/1876489130466816018"  # 测试列表
]

# ==================== 辅助函数 ====================
def load_pushed_ids():
    """加载已推送的推文ID"""
    if os.path.exists(PUSHED_IDS_FILE):
        try:
            with open(PUSHED_IDS_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_pushed_id(tweet_id):
    """保存已推送的推文ID"""
    pushed_ids = load_pushed_ids()
    pushed_ids.add(tweet_id)
    with open(PUSHED_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(pushed_ids), f, indent=2)

def random_sleep(min_sec=2, max_sec=5):
    """随机延时，模拟人类行为"""
    sleep_time = random.uniform(min_sec, max_sec)
    print(f"  随机等待 {sleep_time:.2f} 秒...")
    time.sleep(sleep_time)

def create_undetected_driver():
    """创建反检测的Chrome浏览器实例"""
    print("正在启动 undetected_chromedriver...")
    
    options = uc.ChromeOptions()
    
    # 添加代理配置
    if CHROME_PROXY:
        print(f"  配置代理: {CHROME_PROXY}")
        options.add_argument(f'--proxy-server={CHROME_PROXY}')
    
    # 使用持久化Profile
    if USE_PERSISTENT_PROFILE:
        print(f"  使用持久化Profile: {PROFILE_DIR}")
        options.add_argument(f'--user-data-dir={PROFILE_DIR}')
    
    # 其他优化选项
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = uc.Chrome(options=options)
        print("✓ undetected_chromedriver 启动成功")
        return driver
    except Exception as e:
        print(f"× 启动失败: {e}")
        raise

def download_image_to_base64(url, proxy=None):
    """下载图片并转换为base64编码
    
    Args:
        url: 图片URL
        proxy: 代理配置
    
    Returns:
        str: base64编码的图片，失败返回None
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        if response.status_code == 200:
            # 将图片数据转换为base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            return image_base64
        else:
            print(f"  × 下载图片失败 (状态码: {response.status_code})")
            return None
    except Exception as e:
        print(f"  × 下载图片异常: {e}")
        return None

def extract_tweet_data(tweet_article):
    """从推文元素中提取数据
    
    Args:
        tweet_article: Selenium WebElement，推文的article元素
        
    Returns:
        dict: 包含推文数据的字典，失败返回None
    """
    try:
        # 提取推文ID和URL
        tweet_link_elements = tweet_article.find_elements(By.XPATH, ".//a[contains(@href, '/status/')]")
        tweet_url = None
        tweet_id = None
        
        for link in tweet_link_elements:
            href = link.get_attribute('href')
            if '/status/' in href:
                tweet_url = href
                tweet_id = href.split('/status/')[-1].split('?')[0]
                break
        
        if not tweet_id:
            return None
        
        # 提取推文正文
        tweet_text = ""
        try:
            tweet_text_element = tweet_article.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
            tweet_text = tweet_text_element.text
        except NoSuchElementException:
            pass
        
        # 提取用户名和显示名称
        user_handle = ""
        user_display_name = ""
        try:
            user_name_div = tweet_article.find_element(By.XPATH, ".//div[@data-testid='User-Name']")
            # 提取显示名称
            try:
                display_name_element = user_name_div.find_element(By.XPATH, ".//span[contains(@class, 'css-1jxf684')]")
                user_display_name = display_name_element.text
            except:
                pass
            
            # 提取handle (@username)
            try:
                handle_element = user_name_div.find_element(By.XPATH, ".//a[contains(@href, '/')]")
                user_handle = handle_element.get_attribute('href').split('/')[-1]
                user_handle = f"@{user_handle}"
            except:
                pass
        except NoSuchElementException:
            pass
        
        # 提取推文时间
        tweet_time = ""
        try:
            time_element = tweet_article.find_element(By.XPATH, ".//time")
            tweet_time = time_element.get_attribute('datetime')
            # 格式化时间为更易读的格式
            if tweet_time:
                dt = datetime.fromisoformat(tweet_time.replace('Z', '+00:00'))
                tweet_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except NoSuchElementException:
            pass
        
        # 提取图片URL
        image_urls = []
        try:
            photo_divs = tweet_article.find_elements(By.XPATH, ".//div[@data-testid='tweetPhoto']")
            
            for photo_div in photo_divs:
                img_elements = photo_div.find_elements(By.TAG_NAME, "img")
                for img_element in img_elements:
                    img_url = img_element.get_attribute('src')
                    
                    if img_url:
                        # 将URL参数替换为 'name=orig' 来获取最高清的原图
                        if 'name=' in img_url:
                            orig_img_url = re.sub(r'name=\w+', 'name=orig', img_url)
                        else:
                            orig_img_url = img_url.split('?')[0] + '?format=jpg&name=orig'
                        
                        if orig_img_url not in image_urls:
                            image_urls.append(orig_img_url)
        except:
            pass
        
        return {
            "id": tweet_id,
            "url": tweet_url,
            "handle": user_handle,
            "display_name": user_display_name,
            "time": tweet_time,
            "text": tweet_text,
            "images": image_urls
        }
    except Exception as e:
        print(f"  × 提取推文数据失败: {e}")
        return None

async def send_tweet_to_webhook(tweet_data):
    """将推文数据发送到webhook
    
    Args:
        tweet_data: 推文数据字典
    """
    try:
        # 构建消息内容
        message_parts = []
        message_parts.append(f"🐦 新推文监听")
        message_parts.append(f"")
        
        # 用户信息
        if tweet_data['display_name']:
            message_parts.append(f"👤 作者: {tweet_data['display_name']} ({tweet_data['handle']})")
        else:
            message_parts.append(f"👤 作者: {tweet_data['handle']}")
        
        # 时间
        if tweet_data['time']:
            message_parts.append(f"🕐 时间: {tweet_data['time']}")
        
        # 推文链接
        if tweet_data['url']:
            message_parts.append(f"🔗 链接: {tweet_data['url']}")
        
        message_parts.append(f"")
        
        # 推文内容
        if tweet_data['text']:
            message_parts.append(f"📝 内容:")
            message_parts.append(tweet_data['text'])
            message_parts.append(f"")
        
        # 图片信息
        if tweet_data['images']:
            message_parts.append(f"🖼️ 包含 {len(tweet_data['images'])} 张图片")
        
        # 发送文本消息
        message = "\n".join(message_parts)
        print(f"  发送推文通知...")
        await send_message_async(message, msg_type="text")
        
        # 发送图片（如果有）
        if tweet_data['images']:
            print(f"  准备发送 {len(tweet_data['images'])} 张图片...")
            for idx, img_url in enumerate(tweet_data['images'], 1):
                print(f"  下载图片 {idx}/{len(tweet_data['images'])}...")
                
                # 下载图片并转换为base64
                proxy = CHROME_PROXY if CHROME_PROXY else None
                image_base64 = download_image_to_base64(img_url, proxy)
                
                if image_base64:
                    print(f"  发送图片 {idx}/{len(tweet_data['images'])}...")
                    success = await send_image_async(image_base64=image_base64)
                    if success:
                        print(f"  ✓ 图片 {idx} 发送成功")
                    else:
                        print(f"  × 图片 {idx} 发送失败")
                    
                    # 图片发送间隔
                    if idx < len(tweet_data['images']):
                        await asyncio.sleep(1)
                else:
                    print(f"  × 图片 {idx} 下载失败，跳过")
        
        print(f"✓ 推文推送完成: {tweet_data['id']}")
        return True
        
    except Exception as e:
        print(f"× 推送推文失败: {e}")
        return False

def scrape_list_tweets(driver, list_url, max_tweets=20):
    """抓取推特列表中的推文
    
    Args:
        driver: Selenium WebDriver实例
        list_url: 推特列表URL
        max_tweets: 最多抓取的推文数量
        
    Returns:
        list: 推文数据列表
    """
    print(f"\n访问列表: {list_url}")
    
    try:
        driver.get(list_url)
        
        # 等待页面加载
        wait = WebDriverWait(driver, 15)
        
        # 等待推文加载
        print("  等待推文加载...")
        time.sleep(5)
        
        tweets_data = []
        processed_ids = set()
        scroll_attempts = 0
        max_scroll_attempts = 10
        
        while len(tweets_data) < max_tweets and scroll_attempts < max_scroll_attempts:
            # 查找所有推文元素
            tweet_articles = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
            
            print(f"  当前页面找到 {len(tweet_articles)} 条推文")
            
            # 提取推文数据
            for article in tweet_articles:
                if len(tweets_data) >= max_tweets:
                    break
                
                tweet_data = extract_tweet_data(article)
                
                if tweet_data and tweet_data['id'] not in processed_ids:
                    processed_ids.add(tweet_data['id'])
                    tweets_data.append(tweet_data)
                    print(f"  ✓ 提取推文: {tweet_data['handle']} - {tweet_data['id']}")
            
            # 如果已经获取足够的推文，退出循环
            if len(tweets_data) >= max_tweets:
                break
            
            # 滚动页面加载更多推文
            print(f"  滚动加载更多推文... (已获取 {len(tweets_data)}/{max_tweets})")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            scroll_attempts += 1
        
        print(f"✓ 共提取 {len(tweets_data)} 条推文")
        return tweets_data
        
    except Exception as e:
        print(f"× 抓取列表失败: {e}")
        return []

async def monitor_list_once(driver, list_url, pushed_ids):
    """监听列表一次
    
    Args:
        driver: Selenium WebDriver实例
        list_url: 推特列表URL
        pushed_ids: 已推送的推文ID集合
        
    Returns:
        int: 新推送的推文数量
    """
    print(f"\n{'='*60}")
    print(f"开始监听列表: {list_url}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 抓取列表中的推文
    tweets = scrape_list_tweets(driver, list_url, MAX_TWEETS_PER_CHECK)
    
    if not tweets:
        print("未获取到推文")
        return 0
    
    # 过滤出新推文（未推送过的）
    new_tweets = [t for t in tweets if t['id'] not in pushed_ids]
    
    if not new_tweets:
        print(f"没有新推文（共检查了 {len(tweets)} 条推文）")
        return 0
    
    print(f"\n发现 {len(new_tweets)} 条新推文，准备推送...")
    
    # 按时间排序（旧的在前，新的在后）
    # 这样推送时就是从旧到新的顺序
    new_tweets.sort(key=lambda x: x['time'] if x['time'] else '')
    
    # 推送新推文
    pushed_count = 0
    for idx, tweet in enumerate(new_tweets, 1):
        print(f"\n--- 推送第 {idx}/{len(new_tweets)} 条新推文 ---")
        print(f"ID: {tweet['id']}")
        print(f"作者: {tweet['handle']}")
        print(f"时间: {tweet['time']}")
        
        # 发送到webhook
        success = await send_tweet_to_webhook(tweet)
        
        if success:
            # 保存已推送ID
            save_pushed_id(tweet['id'])
            pushed_ids.add(tweet['id'])
            pushed_count += 1
        
        # 推文之间间隔
        if idx < len(new_tweets):
            await asyncio.sleep(2)
    
    print(f"\n✓ 本次成功推送 {pushed_count} 条新推文")
    return pushed_count

def check_login_status(driver):
    """检查登录状态"""
    try:
        driver.get("https://x.com/home")
        time.sleep(3)
        
        current_url = driver.current_url
        if "login" in current_url or "i/flow/login" in current_url:
            print("\n" + "="*60)
            print("检测到未登录状态")
            print("浏览器已打开登录页面，请在浏览器窗口中手动登录你的X账号。")
            print("登录成功后，回到这里，按Enter键继续执行监听...")
            print("注意：登录信息将保存到本地，下次运行时无需重复登录")
            print("="*60)
            input()
            return True
        else:
            print("\n✓ 检测到已登录状态，无需重复登录")
            return True
    except Exception as e:
        print(f"× 检查登录状态失败: {e}")
        return False

async def monitor_lists_loop():
    """主监听循环"""
    print("\n" + "="*60)
    print("推特列表监听脚本")
    print("="*60)
    
    # 加载已推送的推文ID
    pushed_ids = load_pushed_ids()
    print(f"已推送的推文数: {len(pushed_ids)}")
    
    # 启动浏览器
    driver = None
    try:
        driver = create_undetected_driver()
        
        # 检查登录状态
        if not check_login_status(driver):
            print("× 登录检查失败，退出程序")
            return
        
        print(f"\n开始监听 {len(TWITTER_LISTS)} 个推特列表...")
        print(f"检查间隔: {LIST_CHECK_INTERVAL} 秒")
        print(f"每次最多获取: {MAX_TWEETS_PER_CHECK} 条推文")
        print("\n提示: 按 Ctrl+C 停止监听\n")
        
        loop_count = 0
        
        while True:
            loop_count += 1
            print(f"\n{'#'*60}")
            print(f"第 {loop_count} 次检查")
            print(f"{'#'*60}")
            
            total_new_tweets = 0
            
            # 遍历所有列表
            for list_url in TWITTER_LISTS:
                try:
                    new_count = await monitor_list_once(driver, list_url, pushed_ids)
                    total_new_tweets += new_count
                    
                    # 列表之间的间隔
                    if list_url != TWITTER_LISTS[-1]:
                        random_sleep(3, 6)
                        
                except Exception as e:
                    print(f"× 监听列表出错: {e}")
                    continue
            
            # 打印本轮总结
            print(f"\n{'='*60}")
            print(f"第 {loop_count} 次检查完成")
            print(f"本轮共推送 {total_new_tweets} 条新推文")
            print(f"下次检查时间: {LIST_CHECK_INTERVAL} 秒后")
            print(f"{'='*60}")
            
            # 等待下次检查
            print(f"\n等待 {LIST_CHECK_INTERVAL} 秒...")
            time.sleep(LIST_CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n收到停止信号，正在退出...")
        
    except Exception as e:
        print(f"\n× 监听过程发生错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("\n关闭浏览器...")
            driver.quit()
        print("监听已停止")

# ==================== 主程序入口 ====================
if __name__ == "__main__":
    # 运行监听循环
    asyncio.run(monitor_lists_loop())

