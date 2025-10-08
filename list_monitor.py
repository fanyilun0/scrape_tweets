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
import logging
import sys
import traceback
from datetime import datetime
from io import BytesIO
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# ==================== 日志配置 ====================
class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)

def setup_logger():
    """设置日志系统"""
    logger = logging.getLogger('ListMonitor')
    logger.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # 彩色格式
    formatter = ColoredFormatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 文件处理器（保存所有日志）
    file_handler = logging.FileHandler('list_monitor.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 初始化logger
logger = setup_logger()

# 导入配置和webhook模块
try:
    from config import (
        CHROME_PROXY, USE_PERSISTENT_PROFILE, PROFILE_DIR,
        PUSHED_IDS_FILE, LIST_CHECK_INTERVAL, MAX_TWEETS_PER_CHECK,
        TWITTER_LISTS, MONITORED_USERS, ENABLE_USER_FILTER
    )
    from webhook import send_message_async, send_image_async
except ImportError as e:
    logger.critical(f"导入配置失败: {e}")
    logger.critical("请确保 config.py 和 webhook.py 文件存在")
    exit(1)

# ==================== 异常处理 ====================
async def send_error_to_webhook(error_msg, error_detail=""):
    """发送错误信息到webhook
    
    Args:
        error_msg: 错误消息
        error_detail: 错误详情
    """
    try:
        message_parts = [
            "⚠️ 列表监听程序异常",
            f"{'='*50}",
            f"❌ 错误: {error_msg}",
        ]
        
        if error_detail:
            message_parts.append(f"\n📋 详情:\n{error_detail}")
        
        message_parts.append(f"\n⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        message = "\n".join(message_parts)
        await send_message_async(message, msg_type="text")
        logger.info("错误信息已推送到webhook")
    except Exception as e:
        logger.error(f"推送错误信息失败: {e}")

# ==================== 辅助函数 ====================
def load_pushed_ids():
    """加载已推送的推文ID"""
    if os.path.exists(PUSHED_IDS_FILE):
        try:
            with open(PUSHED_IDS_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception as e:
            logger.warning(f"加载已推送ID失败: {e}")
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
    logger.debug(f"随机等待 {sleep_time:.2f} 秒...")
    time.sleep(sleep_time)

def create_undetected_driver():
    """创建反检测的Chrome浏览器实例"""
    logger.info("正在启动 undetected_chromedriver...")
    
    options = uc.ChromeOptions()
    
    # 添加代理配置
    if CHROME_PROXY:
        logger.info(f"配置代理: {CHROME_PROXY}")
        options.add_argument(f'--proxy-server={CHROME_PROXY}')
    
    # 使用持久化Profile
    if USE_PERSISTENT_PROFILE:
        logger.info(f"使用持久化Profile: {PROFILE_DIR}")
        options.add_argument(f'--user-data-dir={PROFILE_DIR}')
    
    # 其他优化选项
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = uc.Chrome(options=options)
        logger.info("✓ undetected_chromedriver 启动成功")
        return driver
    except Exception as e:
        logger.error(f"启动失败: {e}")
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
            logger.warning(f"下载图片失败 (状态码: {response.status_code})")
            return None
    except Exception as e:
        logger.error(f"下载图片异常: {e}")
        return None

def extract_tweet_data(tweet_article):
    """从推文元素中提取数据，能够区分原创和转推
    
    Args:
        tweet_article: Selenium WebElement，推文的article元素
        
    Returns:
        dict: 包含推文数据的字典，如果不符合白名单要求则返回None
    """
    try:
        is_retweet = False
        retweeter_handle_raw = ""
        retweeter_display_name = ""
        
        # 获取推文的原始HTML用于调试 (仅在需要时启用)
        # tweet_html = tweet_article.get_attribute('outerHTML')
        # logger.debug(f"推文HTML片段: {tweet_html[:200]}...")
        
        # 检测是否为转推 - 多种策略
        try:
            # 策略1: 检查socialContext (最常见)
            social_context = tweet_article.find_element(By.XPATH, ".//div[@data-testid='socialContext']")
            context_text = social_context.text
            logger.debug(f"找到socialContext，内容: {context_text}")
            
            # 转推关键词列表 (支持多语言)
            retweets_keywords = [
                "Retweeted", "转推了", "已转推", "已转帖", 
                "reposted", "转发了", "retweet", "Retweet",
                "Reposted"  # X 的新术语
            ]
            matched_keyword = None
            
            for keyword in retweets_keywords:
                if keyword.lower() in context_text.lower():  # 不区分大小写
                    matched_keyword = keyword
                    is_retweet = True
                    logger.debug(f"✓ 匹配到转推关键词: {keyword}")
                    break
            
            if is_retweet:
                # 提取转推者的用户名
                try:
                    # 方法1: 从socialContext中的链接提取 (最可靠)
                    retweeter_links = social_context.find_elements(By.TAG_NAME, "a")
                    for link in retweeter_links:
                        href = link.get_attribute('href')
                        if href and '/status/' not in href and '/photo/' not in href:
                            # 提取用户名
                            retweeter_handle_raw = href.split('/')[-1].split('?')[0].split('#')[0]
                            if retweeter_handle_raw:
                                break
                    
                    # 方法2: 提取显示名称
                    # 清理显示名称，移除"Retweeted"等文字和多余空格
                    retweeter_display_name = context_text
                    if matched_keyword:
                        retweeter_display_name = retweeter_display_name.replace(matched_keyword, "").strip()
                    # 移除其他可能的干扰文本
                    retweeter_display_name = re.sub(r'\s+', ' ', retweeter_display_name).strip()
                    
                    # 方法3: 如果上面的方法都失败，尝试从span中提取
                    if not retweeter_display_name:
                        try:
                            spans = social_context.find_elements(By.TAG_NAME, "span")
                            for span in spans:
                                text = span.text.strip()
                                if text and text not in retweets_keywords:
                                    retweeter_display_name = text
                                    break
                        except:
                            pass
                    
                    logger.debug(f"检测到转推 - 转推者: @{retweeter_handle_raw} ({retweeter_display_name})")
                except Exception as e:
                    logger.debug(f"提取转推者信息失败: {e}")
                    
        except NoSuchElementException:
            # logger.debug("未找到socialContext元素")
            # 策略2: 检查是否有转推图标 (backup)
            try:
                retweet_icon = tweet_article.find_element(By.XPATH, ".//div[@data-testid='retweet']")
                # 如果找到了转推图标，说明可能是转推
                # 但这个不太可靠，仅作为备用检测
                #logger.debug("找到retweet图标，但无socialContext，可能是特殊情况")
                pass
            except NoSuchElementException:
                #logger.debug("也未找到retweet图标")
                pass
            
            # 找不到socialContext，说明很可能是原创推文
            is_retweet = False
            # logger.debug("判定为原创推文")
        
        # 提取用户名和显示名称（这是原作者的信息）
        user_handle_raw = ""
        user_display_name = ""
        try:
            user_name_div = tweet_article.find_element(By.XPATH, ".//div[@data-testid='User-Name']")
            
            # 提取handle (@username) - 优先级更高，因为更准确
            try:
                # 尝试多种方法提取用户名
                handle_links = user_name_div.find_elements(By.XPATH, ".//a[contains(@href, '/')]")
                for link in handle_links:
                    href = link.get_attribute('href')
                    if href and '/status/' not in href and '/photo/' not in href:
                        # 提取用户名，确保清理所有多余参数
                        user_handle_raw = href.split('/')[-1].split('?')[0].split('#')[0]
                        if user_handle_raw:  # 找到了就退出
                            break
                
                logger.debug(f"提取到用户名: @{user_handle_raw}")
            except Exception as e:
                logger.debug(f"提取用户名失败: {e}")
            
            # 提取显示名称
            try:
                # 尝试多种选择器
                display_name_element = None
                
                # 方法1: 通过CSS类名
                try:
                    display_name_element = user_name_div.find_element(By.XPATH, ".//span[contains(@class, 'css-1jxf684')]")
                except:
                    pass
                
                # 方法2: 通过结构查找 (backup)
                if not display_name_element:
                    try:
                        spans = user_name_div.find_elements(By.TAG_NAME, "span")
                        for span in spans:
                            text = span.text.strip()
                            # 显示名称通常是第一个非@开头的文本
                            if text and not text.startswith('@') and len(text) > 0:
                                display_name_element = span
                                break
                    except:
                        pass
                
                if display_name_element:
                    user_display_name = display_name_element.text.strip()
                    logger.debug(f"提取到显示名称: {user_display_name}")
                    
            except Exception as e:
                logger.debug(f"提取显示名称失败: {e}")
                
        except NoSuchElementException:
            #logger.debug("未找到User-Name元素")
            pass
        
        # 白名单过滤逻辑
        # 如果是转推，检查转推者是否在白名单
        if is_retweet:
            # logger.debug(f"转推检测 - 转推者: @{retweeter_handle_raw}, 原作者: @{user_handle_raw}")
            if not is_user_in_whitelist(retweeter_handle_raw):
                # logger.debug(f"跳过转推 - 转推者 @{retweeter_handle_raw} 不在白名单")
                return None  # 转推者不在白名单，跳过
            # logger.debug(f"✓ 转推者 @{retweeter_handle_raw} 在白名单中")
        # 如果是原创，检查作者是否在白名单
        else:
            # logger.debug(f"原创推文检测 - 作者: @{user_handle_raw}")
            if not is_user_in_whitelist(user_handle_raw):
                # logger.debug(f"跳过原创 - 作者 @{user_handle_raw} 不在白名单")
                return None  # 作者不在白名单，跳过
            # logger.debug(f"✓ 作者 @{user_handle_raw} 在白名单中")
        
        # 只有通过白名单检查的推文才会继续提取其他信息
        
        # 验证提取的用户信息
        if is_retweet:
            if not retweeter_handle_raw:
                logger.warning("转推检测成功，但未能提取到转推者用户名，可能存在解析问题")
            if not user_handle_raw:
                logger.warning("转推检测成功，但未能提取到原作者用户名，可能存在解析问题")
        else:
            if not user_handle_raw:
                logger.warning("原创推文未能提取到作者用户名，可能存在解析问题")
        
        # 提取推文ID和URL
        tweet_link_elements = tweet_article.find_elements(By.XPATH, ".//a[contains(@href, '/status/')]")
        tweet_url = None
        tweet_id = None
        
        for link in tweet_link_elements:
            href = link.get_attribute('href')
            if '/status/' in href and '/analytics' not in href:  # 排除analytics链接
                tweet_url = href
                # 清理URL，移除额外的路径
                tweet_id = href.split('/status/')[-1].split('?')[0].split('/')[0]
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
        
        # 构建返回数据
        tweet_data = {
            "id": tweet_id,
            "url": tweet_url,
            "is_retweet": is_retweet,
            "retweeter": {  # 转推者信息
                "handle_raw": retweeter_handle_raw,
                "display_name": retweeter_display_name
            },
            "original_author": {  # 原作者信息
                "handle_raw": user_handle_raw,
                "display_name": user_display_name
            },
            "time": tweet_time,
            "text": tweet_text,
            "images": image_urls
        }
        
        # 输出提取成功的摘要信息
        if is_retweet:
            logger.debug(f"✓ 成功提取转推数据 - ID: {tweet_id}, 转推者: @{retweeter_handle_raw}, 原作者: @{user_handle_raw}")
        else:
            logger.debug(f"✓ 成功提取原创数据 - ID: {tweet_id}, 作者: @{user_handle_raw}")
        
        return tweet_data
        
    except Exception as e:
        logger.debug(f"提取推文数据失败: {e}")
        logger.debug(traceback.format_exc())
        return None

async def send_tweet_to_webhook(tweet_data):
    """将推文数据发送到webhook，为转推提供专门格式
    
    Args:
        tweet_data: 推文数据字典
    """
    try:
        # 构建消息内容
        message_parts = []
        
        # 根据是否为转推，生成不同格式的消息
        if tweet_data.get('is_retweet'):
            # 这是转推
            message_parts.append(f"🔄 用户转推提醒")
            retweeter = tweet_data['retweeter']
            original_author = tweet_data['original_author']
            
            # 突出转推者
            if retweeter['display_name']:
                message_parts.append(f"👤 转推者: {retweeter['display_name']} (@{retweeter['handle_raw']})")
            else:
                message_parts.append(f"👤 转推者: @{retweeter['handle_raw']}")
            
            # 标明原作者
            if original_author['display_name']:
                message_parts.append(f"✍️ 原作者: {original_author['display_name']} (@{original_author['handle_raw']})")
            else:
                message_parts.append(f"✍️ 原作者: @{original_author['handle_raw']}")
        else:
            # 这是原创推文
            message_parts.append(f"🐦 新推文监听")
            author = tweet_data['original_author']  # 对于原创，original_author就是作者
            
            if author['display_name']:
                message_parts.append(f"👤 作者: {author['display_name']} (@{author['handle_raw']})")
            else:
                message_parts.append(f"👤 作者: @{author['handle_raw']}")
        
        # 时间
        if tweet_data['time']:
            message_parts.append(f"🕐 时间: {tweet_data['time']}")
        
        message_parts.append(f"")
        
        # 推文内容
        if tweet_data['text']:
            message_parts.append(f"📝 内容:")
            message_parts.append(tweet_data['text'])
            message_parts.append(f"")
        
        # 推文链接
        if tweet_data['url']:
            message_parts.append(f"🔗 链接: {tweet_data['url']}")
        
        # 图片信息
        if tweet_data['images']:
            message_parts.append(f"🖼️ 包含 {len(tweet_data['images'])} 张图片")
        
        # 发送文本消息
        message = "\n".join(message_parts)
        
        # 发送前先输出推文内容到日志
        logger.info("=" * 60)
        logger.info("准备发送推文到webhook:")
        logger.info("-" * 60)
        for line in message.split('\n'):
            logger.info(line)
        logger.info("=" * 60)
        
        await send_message_async(message, msg_type="text")
        
        # 发送图片（如果有）
        if tweet_data['images']:
            logger.info(f"准备发送 {len(tweet_data['images'])} 张图片...")
            for idx, img_url in enumerate(tweet_data['images'], 1):
                logger.info(f"下载图片 {idx}/{len(tweet_data['images'])}...")
                
                # 下载图片并转换为base64
                proxy = CHROME_PROXY if CHROME_PROXY else None
                image_base64 = download_image_to_base64(img_url, proxy)
                
                if image_base64:
                    logger.info(f"发送图片 {idx}/{len(tweet_data['images'])}...")
                    success = await send_image_async(image_base64=image_base64)
                    if success:
                        logger.info(f"✓ 图片 {idx} 发送成功")
                    else:
                        logger.warning(f"图片 {idx} 发送失败")
                    
                    # 图片发送间隔
                    if idx < len(tweet_data['images']):
                        await asyncio.sleep(1)
                else:
                    logger.warning(f"图片 {idx} 下载失败，跳过")
        
        logger.info(f"✓ 推文推送完成: {tweet_data['id']}")
        return True
        
    except Exception as e:
        logger.error(f"推送推文失败: {e}")
        error_detail = traceback.format_exc()
        await send_error_to_webhook("推送推文到webhook失败", error_detail)
        return False

def is_user_in_whitelist(user_handle_raw):
    """检查用户是否在白名单中
    
    Args:
        user_handle_raw: 用户名（不含@）
        
    Returns:
        bool: 如果用户在白名单或未启用过滤，返回True
    """
    # 如果未启用用户过滤，返回True（允许所有用户）
    if not ENABLE_USER_FILTER:
        return True
    
    # 如果白名单为空，返回True（允许所有用户）
    if not MONITORED_USERS:
        return True
    
    # 检查用户是否在白名单中（不区分大小写）
    return user_handle_raw.lower() in [u.lower() for u in MONITORED_USERS]

def scrape_list_tweets(driver, list_url, max_tweets=20):
    """抓取推特列表中的推文
    
    Args:
        driver: Selenium WebDriver实例
        list_url: 推特列表URL
        max_tweets: 最多抓取的推文数量
        
    Returns:
        list: 推文数据列表
    """
    logger.info(f"访问列表: {list_url}")
    
    try:
        driver.get(list_url)
        
        # 等待页面加载
        wait = WebDriverWait(driver, 15)
        
        # 等待推文加载
        logger.info("等待推文加载...")
        time.sleep(5)
        
        tweets_data = []
        processed_ids = set()
        no_new_tweets_count = 0  # 连续未发现新推文的次数
        max_no_new_tweets = 3     # 最多允许3次未发现新推文
        
        # 先获取当前可见的推文（不滚动）
        logger.info("抓取当前可见推文...")
        tweet_articles = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
        logger.info(f"找到 {len(tweet_articles)} 条可见推文")
        
        for article in tweet_articles:
            if len(tweets_data) >= max_tweets:
                break
            
            # extract_tweet_data 现在会在内部进行白名单过滤，返回None表示不符合要求
            tweet_data = extract_tweet_data(article)
            
            if tweet_data and tweet_data['id'] not in processed_ids:
                processed_ids.add(tweet_data['id'])
                tweets_data.append(tweet_data)
                
                # 根据是否为转推显示不同的日志
                if tweet_data['is_retweet']:
                    logger.info(f"✓ 提取转推: @{tweet_data['retweeter']['handle_raw']} RT @{tweet_data['original_author']['handle_raw']} - {tweet_data['id']}")
                else:
                    logger.info(f"✓ 提取原创: @{tweet_data['original_author']['handle_raw']} - {tweet_data['id']}")
        
        # 如果需要更多推文，才进行滚动
        if len(tweets_data) < max_tweets:
            logger.info(f"当前获取 {len(tweets_data)} 条，需要更多推文，开始滚动...")
            
            while len(tweets_data) < max_tweets and no_new_tweets_count < max_no_new_tweets:
                # 记录滚动前的推文数量
                before_scroll_count = len(tweets_data)
                
                # 滚动页面
                driver.execute_script("window.scrollBy(0, 800);")  # 每次只滚动800像素，避免跳过内容
                time.sleep(2)
                
                # 获取新出现的推文
                tweet_articles = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
                
                # 提取新推文
                for article in tweet_articles:
                    if len(tweets_data) >= max_tweets:
                        break
                    
                    # extract_tweet_data 现在会在内部进行白名单过滤
                    tweet_data = extract_tweet_data(article)
                    
                    if tweet_data and tweet_data['id'] not in processed_ids:
                        processed_ids.add(tweet_data['id'])
                        tweets_data.append(tweet_data)
                        
                        # 根据是否为转推显示不同的日志
                        if tweet_data['is_retweet']:
                            logger.info(f"✓ 提取转推: @{tweet_data['retweeter']['handle_raw']} RT @{tweet_data['original_author']['handle_raw']} - {tweet_data['id']}")
                        else:
                            logger.info(f"✓ 提取原创: @{tweet_data['original_author']['handle_raw']} - {tweet_data['id']}")
                
                # 检查是否有新推文
                if len(tweets_data) == before_scroll_count:
                    no_new_tweets_count += 1
                    logger.warning(f"未发现新的符合条件的推文 ({no_new_tweets_count}/{max_no_new_tweets})")
                else:
                    no_new_tweets_count = 0  # 重置计数器
                    logger.info(f"已获取 {len(tweets_data)}/{max_tweets} 条推文")
        
        logger.info(f"✓ 共提取 {len(tweets_data)} 条推文")
        
        # 如果启用了用户过滤，显示统计信息
        if ENABLE_USER_FILTER and MONITORED_USERS:
            logger.info(f"已启用用户白名单过滤，监听 {len(MONITORED_USERS)} 个用户")
        
        return tweets_data
        
    except Exception as e:
        logger.error(f"抓取列表失败: {e}")
        logger.error(traceback.format_exc())
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
    logger.info("=" * 60)
    logger.info(f"开始监听列表: {list_url}")
    logger.info("=" * 60)
    
    # 抓取列表中的推文（增强异常处理）
    tweets = []
    try:
        tweets = scrape_list_tweets(driver, list_url, MAX_TWEETS_PER_CHECK)
    except Exception as e:
        error_msg = f"抓取列表 {list_url} 时发生严重错误: {e}"
        logger.error(error_msg)
        error_detail = traceback.format_exc()
        logger.error(error_detail)
        # 发送错误到webhook
        await send_error_to_webhook(error_msg, error_detail)
        # 返回0，让主循环继续
        return 0
    
    if not tweets:
        logger.info("未获取到推文")
        return 0
    
    # 过滤出新推文（未推送过的）
    new_tweets = [t for t in tweets if t['id'] not in pushed_ids]
    
    if not new_tweets:
        logger.info(f"没有新推文（共检查了 {len(tweets)} 条推文）")
        return 0
    
    logger.info(f"发现 {len(new_tweets)} 条新推文，准备推送...")
    
    # 按时间排序（旧的在前，新的在后）
    # 这样推送时就是从旧到新的顺序
    new_tweets.sort(key=lambda x: x['time'] if x['time'] else '')
    
    # 推送新推文
    pushed_count = 0
    for idx, tweet in enumerate(new_tweets, 1):
        logger.info("-" * 60)
        logger.info(f"推送第 {idx}/{len(new_tweets)} 条新推文")
        logger.info(f"ID: {tweet['id']}")
        if tweet['is_retweet']:
            logger.info(f"转推者: @{tweet['retweeter']['handle_raw']}")
            logger.info(f"原作者: @{tweet['original_author']['handle_raw']}")
        else:
            logger.info(f"作者: @{tweet['original_author']['handle_raw']}")
        logger.info(f"时间: {tweet['time']}")
        
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
    
    logger.info(f"✓ 本次成功推送 {pushed_count} 条新推文")
    return pushed_count

def check_login_status(driver):
    """检查登录状态"""
    try:
        driver.get("https://x.com/home")
        time.sleep(3)
        
        current_url = driver.current_url
        if "login" in current_url or "i/flow/login" in current_url:
            logger.warning("=" * 60)
            logger.warning("检测到未登录状态")
            logger.warning("浏览器已打开登录页面，请在浏览器窗口中手动登录你的X账号。")
            logger.warning("登录成功后，回到这里，按Enter键继续执行监听...")
            logger.warning("注意：登录信息将保存到本地，下次运行时无需重复登录")
            logger.warning("=" * 60)
            input()
            return True
        else:
            logger.info("✓ 检测到已登录状态，无需重复登录")
            return True
    except Exception as e:
        logger.error(f"检查登录状态失败: {e}")
        return False

async def monitor_lists_loop():
    """主监听循环"""
    logger.info("=" * 60)
    logger.info("推特列表监听脚本启动")
    logger.info("=" * 60)
    
    # 加载已推送的推文ID
    pushed_ids = load_pushed_ids()
    logger.info(f"已推送的推文数: {len(pushed_ids)}")
    
    # 启动浏览器
    driver = None
    try:
        driver = create_undetected_driver()
        
        # 检查登录状态
        if not check_login_status(driver):
            logger.error("登录检查失败，退出程序")
            await send_error_to_webhook("登录检查失败", "无法登录Twitter，程序退出")
            return
        
        logger.info(f"开始监听 {len(TWITTER_LISTS)} 个推特列表...")
        logger.info(f"检查间隔: {LIST_CHECK_INTERVAL} 秒")
        logger.info(f"每次最多获取: {MAX_TWEETS_PER_CHECK} 条推文")
        logger.info("提示: 按 Ctrl+C 停止监听")
        
        loop_count = 0
        # 增加一个登录检查的计数器
        login_check_interval_loops = 100  # 每100次循环检查一次登录
        
        while True:
            loop_count += 1
            logger.info("#" * 60)
            logger.info(f"第 {loop_count} 次检查")
            logger.info("#" * 60)
            
            # 定期检查登录状态
            if loop_count % login_check_interval_loops == 0:
                logger.info("定期检查登录状态...")
                check_login_status(driver)
            
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
                    error_msg = f"监听列表出错: {e}"
                    logger.error(error_msg)
                    error_detail = traceback.format_exc()
                    logger.error(error_detail)
                    await send_error_to_webhook(error_msg, error_detail)
                    continue
            
            # 打印本轮总结
            logger.info("=" * 60)
            logger.info(f"第 {loop_count} 次检查完成")
            logger.info(f"本轮共推送 {total_new_tweets} 条新推文")
            logger.info(f"下次检查时间: {LIST_CHECK_INTERVAL} 秒后")
            logger.info("=" * 60)
            
            # 等待下次检查
            logger.debug(f"等待 {LIST_CHECK_INTERVAL} 秒...")
            time.sleep(LIST_CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\n收到停止信号，正在退出...")
        
    except Exception as e:
        error_msg = f"监听过程发生严重错误: {e}"
        logger.critical(error_msg)
        error_detail = traceback.format_exc()
        logger.critical(error_detail)
        await send_error_to_webhook(error_msg, error_detail)
        
    finally:
        if driver:
            logger.info("关闭浏览器...")
            driver.quit()
        logger.info("监听已停止")

# ==================== 主程序入口 ====================
if __name__ == "__main__":
    # 运行监听循环
    asyncio.run(monitor_lists_loop())

