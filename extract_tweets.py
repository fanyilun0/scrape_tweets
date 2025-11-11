import re
import time
import csv
import os
import requests
import random
import json
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

# 你提供的包含推文链接的原始文本
# original_text = """
# 这段时间重新翻看了自己的推文，把其中我觉得比较精华的内容和一些高光操作整理了出来，虽然市场状况一直在变化，具体的方法未必适用了，但是如何寻找alpha、怎么将认知与实践相结合，这些思维依然是有共性的，希望能对大家有所帮助。 以下按时间顺序列出： 2022.04.22 NFT图狗Mint指南 
# https://x.com/0xSunNFT/status/1517468623207424003
# …2022.05.02 猴地逃顶获利200ETH 
# https://x.com/0xSunNFT/status/1521151261193560065
# … 2022.07.21 NFT抢购Bot指南
# https://x.com/0xSunNFT/status/1538916947647430656
# … 2022.09.21 DogeClub单个图狗获利70ETH 
# https://x.com/0xSunNFT/status/1572257431178342400
# … 2023.04.19 Memecoin基础科普（当时市场热点正从NFT转移到土狗币） 
# https://x.com/0xSunNFT/status/1648673250845790209
# … 2023.05.09 重心换到土狗币后单周浮盈100ETH 
# https://x.com/0xSunNFT/status/1655926338778464259
# … 2023.07.29 Pauly的Pond开盘3分钟1ETH变成44.5ETH
# https://x.com/0xSunNFT/status/1684957909887954944
# … 2023.09.12 香蕉枪Banana Gun发币复盘，白名单+开盘限购获利50ETH
# https://x.com/0xSunNFT/status/1701321628859433004
# … 2024.01.05 节点猴NodeMonkes复盘，参与荷兰拍，0.03BTC成本最高地板价0.8BTC，获利3BTC 
# https://x.com/0xSunNFT/status/1743160314982724012
# … 2024.01.29 从1万~1000万资金量级，各个阶段的思考与经历
# https://x.com/0xSunNFT/status/1751888091487580633
# … 2024.02.26 通过链上交易一个月赚$1M的复盘（发射台Moby的预售、Shib官方的404项目Sheb、DN404项目ASTX、公售随便打开盘上币安的Portal、Merlin链的$Huhu等）
# https://x.com/0xSunNFT/status/1761953815765696648
# … 2024.06.19 反思自己在擅长的链上赛道过于谨慎，在不熟的山寨操作上仓位过重
# https://x.com/0xSunNFT/status/1803282305886330944
# … 2024.07.08 各种原因导致一天踏空数个金狗后的思考 
# https://x.com/0xSunNFT/status/1799387231456833976
# …2024.07.17 特朗普枪击事件，相关热点土狗$Fight获利13万u复盘 
# https://x.com/0xSunNFT/status/1813419967930667051
# … 2024.07.24 关于“聪明钱”和“跟单”的看法 
# https://x.com/0xSunNFT/status/1815968611384819977
# … 2024.07.31 麻吉图币项目“BAYC”开盘发现套利方法，1分钟收获15万u 
# https://x.com/0xSunNFT/status/1818666552461570284
# … 2024.08.23 Simon Cat预售复盘，一次堪称完美的打新机会
# https://x.com/0xSunNFT/status/1826924435930333294
# … 2024.10.11 2M市值开始转推Goat相关内容，获利10万u 
# https://x.com/0xSunNFT/status/1844761629705318449
# …2024.11.03 马斯克置顶松鼠第一时间发推，获利19万u 
# https://x.com/0xSunNFT/status/1852831467119743143
# … 2024.11.11 复盘SOL单链单月1M收益 
# https://x.com/0xSunNFT/status/1855882780334604736
# … 2024.11.16 DeSci生态起飞前梳理线索，RIF+URO获利30万u
# https://x.com/0xSunNFT/status/1857710057124728961
# … 2024.12.14 复盘为什么会卖飞自己早期发掘的项目，做多Goat和Pnut获利$2M
# https://x.com/0xSunNFT/status/1867845182001229920
# … 2025.01.05 AI赛道相关代币一周获利$1M复盘 
# https://x.com/0xSunNFT/status/1875720961775083896
# … 2025.01.18 特朗普推特发布代币合约后“人只活一次” 
# https://x.com/0xSunNFT/status/1880446520627196118
# … 2025.01.19 $Trump单币浮盈$20M+
# https://x.com/0xSunNFT/status/1880769711480389784
# … 2025.01.25 特朗普老婆发币$Melania，对后市看法由乐观变为不确定
# https://x.com/0xSunNFT/status/1882971617783173341
# … 2025.02.03 认为不存在全面普涨，开始低倍做空山寨币 
# https://x.com/0xSunNFT/status/1886229854385025198
# …2025.03.30 对自己三年来币圈笔记的整理与分享 
# https://x.com/0xSunNFT/status/1906249868798230597
# … 2025.04.07 做空山寨币的黄金期已经过去 
# https://x.com/0xSunNFT/status/1909151413822980357
# … 2025.04.19 不要用战术上的勤奋掩盖战略上的懒惰 
# https://x.com/0xSunNFT/status/1913608106275397829
# …2025.05.01 $Gork获利18万u 
# https://x.com/0xSunNFT/status/1917685646409490783
# … 2025.05.31 认为大部分山寨已经重新进入下跌趋势
# https://x.com/0xSunNFT/status/1928769488146804791
# … 2025.07.08 PumpFun公售是机会 
# https://x.com/0xSunNFT/status/1942314375051960807
# … 2025.07.23 链上Meme两大方法论，叙事交易和地址挖掘 
# https://x.com/0xSunNFT/status/1948021791487824032
# … 2025.08.01 做多ETH，做空山寨币对冲
# https://x.com/0xSunNFT/status/1951099879906058707
# … 2025.09.02 复盘做空WLFI获利$1M 
# https://x.com/0xSunNFT/status/1962792706905915473
# """


original_text ="""
https://x.com/TingHu888/status/1988123397319200795
https://x.com/TingHu888/status/1988082000264335693
https://x.com/TingHu888/status/1987856180694413457
https://x.com/TingHu888/status/1987786875747389833
https://x.com/TingHu888/status/1987757492596847048
https://x.com/TingHu888/status/1987376007154905519
https://x.com/TingHu888/status/1987004310497251728
https://x.com/TingHu888/status/1986999026252976425
https://x.com/TingHu888/status/1986996340493295989
https://x.com/TingHu888/status/1986814825654353951
https://x.com/TingHu888/status/1986808847504482612
https://x.com/TingHu888/status/1986807227496411265
https://x.com/TingHu888/status/1986364658786443528
https://x.com/TingHu888/status/1986303935968387147
https://x.com/TingHu888/status/1986297924125663562
https://x.com/TingHu888/status/1986277122105876730
https://x.com/TingHu888/status/1986090834199273935
https://x.com/TingHu888/status/1986081605040124179
https://x.com/TingHu888/status/1986077001397223472
https://x.com/TingHu888/status/1986074709658910992
https://x.com/TingHu888/status/1986010071491543158
https://x.com/TingHu888/status/1986008321963573361
https://x.com/TingHu888/status/1986002985898680756
https://x.com/TingHu888/status/1985370005425553747
https://x.com/TingHu888/status/1983841722766647783
https://x.com/TingHu888/status/1980263750117859773
https://x.com/TingHu888/status/1977618151929205162
https://x.com/TingHu888/status/1977445851296669926
https://x.com/TingHu888/status/1972912363428012431
https://x.com/TingHu888/status/1960788158368412007
https://x.com/TingHu888/status/1960168872407163279
https://x.com/TingHu888/status/1955650244760461802
https://x.com/TingHu888/status/1917058963339940004
https://x.com/TingHu888/status/1892878860519145875
https://x.com/TingHu888/status/1880121476453646473
https://x.com/TingHu888/status/1878824888276054275
https://x.com/TingHu888/status/1872202526835229136
https://x.com/TingHu888/status/1870791121024282858
https://x.com/TingHu888/status/1866894859245850722
https://x.com/TingHu888/status/1865453960854982843
https://x.com/TingHu888/status/1864258526627156448
https://x.com/TingHu888/status/1862061149090681302
https://x.com/TingHu888/status/1859823309418021014
https://x.com/TingHu888/status/1785329783146258454
https://x.com/TingHu888/status/1745348180483699022
https://x.com/TingHu888/status/1599699347033456640
https://x.com/TingHu888/status/1557618125612339201
https://x.com/TingHu888/status/1536342879039172609
https://x.com/TingHu888/status/1529484387221651457
https://x.com/TingHu888/status/1527639728585326592
https://x.com/TingHu888/status/1525037842485116928
https://x.com/TingHu888/status/1524023604002050054
https://x.com/TingHu888/status/1523705712140255232
https://x.com/TingHu888/status/1522614203982696448
https://x.com/TingHu888/status/1522483527178387456
https://x.com/TingHu888/status/1520655908916785152
https://x.com/TingHu888/status/1520409694883676160
https://x.com/TingHu888/status/1518628879794991104
https://x.com/TingHu888/status/1516830342015258626
https://x.com/TingHu888/status/1515979885046509572
https://x.com/TingHu888/status/1515620527670398978
https://x.com/TingHu888/status/1514496947507572737
https://x.com/TingHu888/status/1513043200830676994
https://x.com/TingHu888/status/1510879716290744325
https://x.com/TingHu888/status/1510507737394073600
https://x.com/TingHu888/status/1510136534066155520
https://x.com/TingHu888/status/1504514378548523008
https://x.com/TingHu888/status/1502968630262534144
https://x.com/TingHu888/status/1497467639924674563
https://x.com/TingHu888/status/1495406320929112064
https://x.com/TingHu888/status/1495307872779247616
https://x.com/TingHu888/status/1491720862319648771
https://x.com/TingHu888/status/1488772594715475969
"""

# ==================== 配置区域 ====================
# 代理配置（如果不需要代理，设置为None）
PROXY = "http://127.0.0.1:7890"  # 默认代理地址，可以设置为None禁用

# 是否使用持久化Profile（第一次运行需要手动登录，之后会保存登录状态）
USE_PERSISTENT_PROFILE = True
PROFILE_DIR = "./chrome_profile"

# 已抓取推文ID记录文件（避免重复抓取）
SCRAPED_IDS_FILE = "scraped_tweet_ids.json"

# 抓取配置
MAX_RETRIES = 3  # 每条推文最大重试次数
REQUEST_DELAY_MIN = 5  # 请求间隔最小秒数
REQUEST_DELAY_MAX = 10  # 请求间隔最大秒数
TIMEOUT_SECONDS = 30  # 页面加载超时时间（秒）

# ==================== 辅助函数 ====================
def load_scraped_ids():
    """加载已抓取的推文ID"""
    if os.path.exists(SCRAPED_IDS_FILE):
        try:
            with open(SCRAPED_IDS_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_scraped_id(tweet_id):
    """保存已抓取的推文ID"""
    scraped_ids = load_scraped_ids()
    scraped_ids.add(tweet_id)
    with open(SCRAPED_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(scraped_ids), f, indent=2)

def random_sleep(min_sec=1, max_sec=3):
    """随机延时，模拟人类行为"""
    sleep_time = random.uniform(min_sec, max_sec)
    print(f"  随机等待 {sleep_time:.2f} 秒...")
    time.sleep(sleep_time)

def simulate_human_scroll(driver):
    """模拟人类滚动行为"""
    print("  模拟页面滚动...")
    scroll_times = random.randint(1, 3)
    for _ in range(scroll_times):
        scroll_amount = random.randint(200, 500)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.5))

def create_undetected_driver():
    """创建反检测的Chrome浏览器实例"""
    print("正在启动 undetected_chromedriver...")
    
    options = uc.ChromeOptions()
    
    # 添加代理配置
    if PROXY:
        print(f"  配置代理: {PROXY}")
        options.add_argument(f'--proxy-server={PROXY}')
    
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
        print("\n请尝试以下解决方案:")
        print("1. 安装undetected-chromedriver: pip install undetected-chromedriver")
        print("2. 确保Chrome浏览器已安装")
        print("3. 如果使用代理，请确保代理服务正常运行")
        raise

# ==================== 主程序 ====================

# 1. 从文本中提取所有推文URL
tweet_urls = re.findall(r'https://x\.com/\w+/status/\d+', original_text)
print(f"检测到 {len(tweet_urls)} 条推文链接。")

# 加载已抓取的推文ID
scraped_ids = load_scraped_ids()
print(f"已抓取的推文数: {len(scraped_ids)}")

# 2. 初始化Selenium WebDriver
print("\n正在启动浏览器...")
driver = create_undetected_driver()

try:
    # 3. 检查登录状态
    driver.get("https://x.com/home")
    time.sleep(3)
    
    # 检查是否需要登录
    current_url = driver.current_url
    if "login" in current_url or "i/flow/login" in current_url:
        print("\n" + "="*50)
        print("检测到未登录状态")
        print("浏览器已打开登录页面，请在浏览器窗口中手动登录你的X账号。")
        print("登录成功后，回到这里，按Enter键继续执行抓取...")
        print("注意：登录信息将保存到本地，下次运行时无需重复登录")
        print("="*50)
        input() # 等待用户按Enter键
    else:
        print("\n✓ 检测到已登录状态，无需重复登录")
        print("提示：如需切换账号，请删除 chrome_profile 目录后重新运行")

    print("\n开始抓取推文内容...\n")
    
    # 4. 创建图片保存目录和输出文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    images_dir = f"tweets_images_{timestamp}"
    os.makedirs(images_dir, exist_ok=True)
    
    csv_filename = f"tweets_data_{timestamp}.csv"
    md_filename = f"tweets_data_{timestamp}.md"
    
    # 初始化CSV文件（写入表头）
    csv_file = open(csv_filename, 'w', newline='', encoding='utf-8-sig')
    fieldnames = ['序号', '用户名', '发布时间', '推文链接', '推文内容', '图片数量', '图片URL']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    csv_file.flush()  # 立即刷新到磁盘
    print(f"✓ 已创建CSV文件: {csv_filename}")
    
    # 初始化Markdown文件（写入头部信息）
    md_file = open(md_filename, 'w', encoding='utf-8')
    md_file.write(f"# 推文合集\n\n")
    md_file.write(f"**抓取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    md_file.write(f"**推文总数**: 待统计...\n\n")
    md_file.write("---\n\n")
    md_file.flush()  # 立即刷新到磁盘
    print(f"✓ 已创建Markdown文件: {md_filename}\n")
    
    # 计数器
    success_count = 0
    total_images_count = 0
    
    # 5. 循环访问每个URL并抓取内容
    for i, url in enumerate(tweet_urls):
        # 提取推文ID
        tweet_id = url.split('/')[-1]
        
        # 检查是否已抓取
        if tweet_id in scraped_ids:
            print(f"--- 跳过第 {i+1}/{len(tweet_urls)} 条（已抓取）: {url} ---")
            continue
            
        print(f"--- 正在抓取第 {i+1}/{len(tweet_urls)} 条: {url} ---")
        
        # 重试机制
        retry_count = 0
        success = False
        
        while retry_count < MAX_RETRIES and not success:
            try:
                if retry_count > 0:
                    print(f"  第 {retry_count + 1} 次尝试...")
                    # 重试前等待更长时间（逐次增加等待时间）
                    wait_time = random.uniform(10, 20) * (retry_count + 1)
                    print(f"  等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                
                driver.get(url)
                
                # 增加初始等待时间，让页面完全加载
                time.sleep(random.uniform(2, 4))
                
                # 检查是否被限流（查看页面标题）
                try:
                    page_title = driver.title.lower()
                    if 'rate limit' in page_title or 'error' in page_title:
                        print(f"  ⚠️ 检测到限流页面，等待更长时间...")
                        time.sleep(random.uniform(30, 60))
                        raise TimeoutException("Rate limited")
                except:
                    pass
                
                # 等待推文内容加载出来
                wait = WebDriverWait(driver, TIMEOUT_SECONDS)
                tweet_article = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//article[@data-testid='tweet']"))
                )
                
                success = True  # 成功加载
                
            except TimeoutException:
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    print(f"  × 超时：页面加载失败，已尝试 {MAX_RETRIES} 次")
                    break
                else:
                    print(f"  ⚠️ 超时，准备重试 ({retry_count}/{MAX_RETRIES})")
                    continue
            except Exception as e:
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    print(f"  × 错误：{str(e)[:100]}")
                    break
                else:
                    print(f"  ⚠️ 出现错误，准备重试 ({retry_count}/{MAX_RETRIES})")
                    continue
        
        if not success:
            print(f"抓取失败: {url}\n已达到最大重试次数\n")
            # 失败后等待更长时间，避免触发更严格的限流
            time.sleep(random.uniform(20, 30))
            continue
        
        try:
            
            # 模拟人类滚动行为
            simulate_human_scroll(driver)
            
            # 提取推文正文
            try:
                tweet_text_element = tweet_article.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
                tweet_text = tweet_text_element.text
            except NoSuchElementException:
                tweet_text = ""
            
            # 提取用户名（@handle）
            try:
                user_handle_element = tweet_article.find_element(By.XPATH, ".//div[@data-testid='User-Name']//a[contains(@href, '/')]")
                user_handle = user_handle_element.get_attribute('href').split('/')[-1]
                user_handle = f"@{user_handle}"
            except NoSuchElementException:
                user_handle = ""
            
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
            

            # 提取图片（新方法：直接从缩略图URL推导原图）
            image_urls = []
            try:
                # 查找所有包含图片的 div 元素
                photo_divs = tweet_article.find_elements(By.XPATH, ".//div[@data-testid='tweetPhoto']")
                
                # 遍历每个图片元素，提取其 src
                for photo_div in photo_divs:
                    # 在每个 div 中找到 img 标签
                    img_elements = photo_div.find_elements(By.TAG_NAME, "img")
                    for img_element in img_elements:
                        img_url = img_element.get_attribute('src')
                        
                        if img_url:
                            # 将URL参数替换为 'name=orig' 来获取最高清的原图
                            # 使用正则表达式确保替换的准确性
                            if 'name=' in img_url:
                                orig_img_url = re.sub(r'name=\w+', 'name=orig', img_url)
                            else:
                                # 如果URL中没有 name 参数，可能需要添加 format=...&name=orig
                                # 但通常直接在末尾添加 ?name=orig 也能奏效
                                orig_img_url = img_url.split('?')[0] + '?format=jpg&name=orig'
                            
                            if orig_img_url not in image_urls:
                                image_urls.append(orig_img_url)
                                
                                # 下载图片
                                try:
                                    # 从URL中提取文件名和扩展名
                                    file_name_part = orig_img_url.split('/')[-1].split('?')[0]
                                    ext_match = re.search(r'format=(\w+)', orig_img_url)
                                    ext = ext_match.group(1) if ext_match else 'jpg'
                                    
                                    img_filename = f"{file_name_part}.{ext}"
                                    img_path = os.path.join(images_dir, img_filename)

                                    # 使用带有 User-Agent 的 requests session 来下载
                                    session = requests.Session()
                                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                                    img_response = session.get(orig_img_url, headers=headers, timeout=15)
                                    
                                    if img_response.status_code == 200:
                                        with open(img_path, 'wb') as f:
                                            f.write(img_response.content)
                                        print(f"  ✓ 已保存图片: {img_filename}")
                                    else:
                                        print(f"  × 下载图片失败 (状态码: {img_response.status_code})")
                                except Exception as download_error:
                                    print(f"  × 下载图片时发生错误: {download_error}")

            except NoSuchElementException:
                pass  # 该推文没有图片

            
            print(f"用户名: {user_handle}")
            print(f"发布时间: {tweet_time}")
            print(f"内容:\n{tweet_text}")
            print(f"图片数量: {len(image_urls)}\n")
            
            # 立即写入CSV文件
            success_count += 1
            total_images_count += len(image_urls)
            images_str = '; '.join(image_urls) if image_urls else ''
            
            csv_writer.writerow({
                '序号': success_count,
                '用户名': user_handle,
                '发布时间': tweet_time,
                '推文链接': url,
                '推文内容': tweet_text,
                '图片数量': len(image_urls),
                '图片URL': images_str
            })
            csv_file.flush()  # 立即刷新到磁盘
            
            # 立即写入Markdown文件
            md_file.write(f"## {success_count}. 推文 - {user_handle}\n\n")
            md_file.write(f"**发布时间**: {tweet_time}\n\n")
            md_file.write(f"**推文链接**: [{url}]({url})\n\n")
            
            # 推文内容
            if tweet_text:
                md_file.write(f"**内容**:\n\n")
                content_lines = tweet_text.split('\n')
                for line in content_lines:
                    if line.strip():
                        md_file.write(f"{line}\n\n")
                    else:
                        md_file.write("\n")
            
            # 图片
            if image_urls:
                md_file.write(f"**图片** ({len(image_urls)} 张):\n\n")
                for img_idx, img_url in enumerate(image_urls, 1):
                    # 本地图片路径
                    local_img = f"{images_dir}/tweet_{success_count}_img_{img_idx}.jpg"
                    if os.path.exists(local_img):
                        md_file.write(f"![图片 {img_idx}]({local_img})\n\n")
                    elif os.path.exists(local_img.replace('.jpg', '.png')):
                        local_img = local_img.replace('.jpg', '.png')
                        md_file.write(f"![图片 {img_idx}]({local_img})\n\n")
                    elif os.path.exists(local_img.replace('.jpg', '.gif')):
                        local_img = local_img.replace('.jpg', '.gif')
                        md_file.write(f"![图片 {img_idx}]({local_img})\n\n")
                    
                    # 同时保留原始URL链接
                    md_file.write(f"*原图链接*: [{img_url}]({img_url})\n\n")
                    md_file.write(f"![image]({img_url})\n\n")
            
            md_file.write("---\n\n")
            md_file.flush()  # 立即刷新到磁盘
            
            print(f"✓ 已写入到文件 (序号: {success_count})\n")
            
            # 保存已抓取的推文ID
            save_scraped_id(tweet_id)
            
            # 随机执行一些"意外"操作（5%概率）
            if random.random() < 0.05:
                action = random.choice(['refresh', 'scroll_top', 'mouse_move'])
                if action == 'refresh':
                    print("  [模拟行为] 刷新页面...")
                    driver.refresh()
                    time.sleep(random.uniform(2, 4))
                elif action == 'scroll_top':
                    print("  [模拟行为] 滚动到页面顶部...")
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(random.uniform(1, 2))
                elif action == 'mouse_move':
                    print("  [模拟行为] 随机移动鼠标...")
                    try:
                        actions = ActionChains(driver)
                        actions.move_by_offset(random.randint(50, 200), random.randint(50, 200))
                        actions.perform()
                    except:
                        pass

            # 随机延时，模仿人类行为，降低被封锁的风险
            random_sleep(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)

        except Exception as e:
            print(f"数据提取失败: {url}\n错误信息: {e}\n")
            # 即使失败也随机等待一下
            time.sleep(random.uniform(5, 10))
            continue

finally:
    # 关闭文件
    try:
        csv_file.close()
        md_file.close()
        print(f"\n✓ 文件已关闭并保存")
    except:
        pass
    
    # 关闭浏览器
    print("所有抓取任务完成，关闭浏览器。")
    driver.quit()

# 6. 更新Markdown文件的推文总数并输出统计信息
try:
    # 重新打开Markdown文件，更新推文总数
    with open(md_filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换"待统计..."为实际数量
    content = content.replace('**推文总数**: 待统计...', f'**推文总数**: {success_count} 条')
    
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n📊 数据摘要:")
    print(f"  - CSV文件: {csv_filename}")
    print(f"  - Markdown文档: {md_filename}")
    print(f"  - 图片目录: {images_dir}/")
    print(f"  - 推文总数: {success_count}")
    print(f"  - 图片总数: {total_images_count}")
    
    if success_count == 0:
        print("\n⚠️ 未成功抓取到任何推文数据")
    else:
        print(f"\n✓ 所有数据已实时保存，即使中途中断也不会丢失已抓取的数据")
        
except Exception as e:
    print(f"\n⚠️ 更新统计信息时出错: {e}")
    print(f"但已抓取的 {success_count} 条推文数据已安全保存")