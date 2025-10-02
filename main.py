import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 你提供的包含推文链接的原始文本
original_text = """
这段时间重新翻看了自己的推文，把其中我觉得比较精华的内容和一些高光操作整理了出来，虽然市场状况一直在变化，具体的方法未必适用了，但是如何寻找alpha、怎么将认知与实践相结合，这些思维依然是有共性的，希望能对大家有所帮助。 以下按时间顺序列出： 2022.04.22 NFT图狗Mint指南 
https://x.com/0xSunNFT/status/1517468623207424003
…2022.05.02 猴地逃顶获利200ETH 
https://x.com/0xSunNFT/status/1521151261193560065
… 2022.07.21 NFT抢购Bot指南
https://x.com/0xSunNFT/status/1538916947647430656
… 2022.09.21 DogeClub单个图狗获利70ETH 
https://x.com/0xSunNFT/status/1572257431178342400
… 2023.04.19 Memecoin基础科普（当时市场热点正从NFT转移到土狗币） 
https://x.com/0xSunNFT/status/1648673250845790209
… 2023.05.09 重心换到土狗币后单周浮盈100ETH 
https://x.com/0xSunNFT/status/1655926338778464259
… 2023.07.29 Pauly的Pond开盘3分钟1ETH变成44.5ETH
https://x.com/0xSunNFT/status/1684957909887954944
… 2023.09.12 香蕉枪Banana Gun发币复盘，白名单+开盘限购获利50ETH
https://x.com/0xSunNFT/status/1701321628859433004
… 2024.01.05 节点猴NodeMonkes复盘，参与荷兰拍，0.03BTC成本最高地板价0.8BTC，获利3BTC 
https://x.com/0xSunNFT/status/1743160314982724012
… 2024.01.29 从1万~1000万资金量级，各个阶段的思考与经历
https://x.com/0xSunNFT/status/1751888091487580633
… 2024.02.26 通过链上交易一个月赚$1M的复盘（发射台Moby的预售、Shib官方的404项目Sheb、DN404项目ASTX、公售随便打开盘上币安的Portal、Merlin链的$Huhu等）
https://x.com/0xSunNFT/status/1761953815765696648
… 2024.06.19 反思自己在擅长的链上赛道过于谨慎，在不熟的山寨操作上仓位过重
https://x.com/0xSunNFT/status/1803282305886330944
… 2024.07.08 各种原因导致一天踏空数个金狗后的思考 
https://x.com/0xSunNFT/status/1799387231456833976
…2024.07.17 特朗普枪击事件，相关热点土狗$Fight获利13万u复盘 
https://x.com/0xSunNFT/status/1813419967930667051
… 2024.07.24 关于“聪明钱”和“跟单”的看法 
https://x.com/0xSunNFT/status/1815968611384819977
… 2024.07.31 麻吉图币项目“BAYC”开盘发现套利方法，1分钟收获15万u 
https://x.com/0xSunNFT/status/1818666552461570284
… 2024.08.23 Simon Cat预售复盘，一次堪称完美的打新机会
https://x.com/0xSunNFT/status/1826924435930333294
… 2024.10.11 2M市值开始转推Goat相关内容，获利10万u 
https://x.com/0xSunNFT/status/1844761629705318449
…2024.11.03 马斯克置顶松鼠第一时间发推，获利19万u 
https://x.com/0xSunNFT/status/1852831467119743143
… 2024.11.11 复盘SOL单链单月1M收益 
https://x.com/0xSunNFT/status/1855882780334604736
… 2024.11.16 DeSci生态起飞前梳理线索，RIF+URO获利30万u
https://x.com/0xSunNFT/status/1857710057124728961
… 2024.12.14 复盘为什么会卖飞自己早期发掘的项目，做多Goat和Pnut获利$2M
https://x.com/0xSunNFT/status/1867845182001229920
… 2025.01.05 AI赛道相关代币一周获利$1M复盘 
https://x.com/0xSunNFT/status/1875720961775083896
… 2025.01.18 特朗普推特发布代币合约后“人只活一次” 
https://x.com/0xSunNFT/status/1880446520627196118
… 2025.01.19 $Trump单币浮盈$20M+
https://x.com/0xSunNFT/status/1880769711480389784
… 2025.01.25 特朗普老婆发币$Melania，对后市看法由乐观变为不确定
https://x.com/0xSunNFT/status/1882971617783173341
… 2025.02.03 认为不存在全面普涨，开始低倍做空山寨币 
https://x.com/0xSunNFT/status/1886229854385025198
…2025.03.30 对自己三年来币圈笔记的整理与分享 
https://x.com/0xSunNFT/status/1906249868798230597
… 2025.04.07 做空山寨币的黄金期已经过去 
https://x.com/0xSunNFT/status/1909151413822980357
… 2025.04.19 不要用战术上的勤奋掩盖战略上的懒惰 
https://x.com/0xSunNFT/status/1913608106275397829
…2025.05.01 $Gork获利18万u 
https://x.com/0xSunNFT/status/1917685646409490783
… 2025.05.31 认为大部分山寨已经重新进入下跌趋势
https://x.com/0xSunNFT/status/1928769488146804791
… 2025.07.08 PumpFun公售是机会 
https://x.com/0xSunNFT/status/1942314375051960807
… 2025.07.23 链上Meme两大方法论，叙事交易和地址挖掘 
https://x.com/0xSunNFT/status/1948021791487824032
… 2025.08.01 做多ETH，做空山寨币对冲
https://x.com/0xSunNFT/status/1951099879906058707
… 2025.09.02 复盘做空WLFI获利$1M 
https://x.com/0xSunNFT/status/1962792706905915473
"""

# 1. 从文本中提取所有推文URL
tweet_urls = re.findall(r'https://x\.com/\w+/status/\d+', original_text)
print(f"检测到 {len(tweet_urls)} 条推文链接。")

# 2. 初始化Selenium WebDriver
# webdriver-manager会自动下载并配置匹配你Chrome版本的ChromeDriver
print("正在启动浏览器...")
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # 3. 手动登录
    driver.get("https://x.com/login")
    print("\n" + "="*50)
    print("浏览器已打开，请在浏览器窗口中手动登录你的X账号。")
    print("登录成功后，回到这里，按Enter键继续执行抓取...")
    print("="*50)
    input() # 等待用户按Enter键

    print("\n登录确认，开始抓取推文内容...\n")
    
    all_tweets_data = []

    # 4. 循环访问每个URL并抓取内容
    for i, url in enumerate(tweet_urls):
        print(f"--- 正在抓取第 {i+1}/{len(tweet_urls)} 条: {url} ---")
        try:
            driver.get(url)
            
            # 等待推文内容加载出来。我们等待一个关键元素出现，这里用 'article' 标签。
            # X使用 'data-testid' 属性来标识元素，这比CSS类名更稳定。
            # 我们等待包含 'tweet' 的 'article' 元素出现，最多等15秒。
            wait = WebDriverWait(driver, 15)
            tweet_article = wait.until(
                EC.presence_of_element_located((By.XPATH, "//article[@data-testid='tweet']"))
            )
            
            # 提取推文正文
            # 推文文本通常在 'data-testid' 为 'tweetText' 的元素内
            tweet_text_element = tweet_article.find_element(By.XPATH, ".//div[@data-testid='tweetText']")
            tweet_text = tweet_text_element.text
            
            # 提取作者信息
            author_name_element = tweet_article.find_element(By.XPATH, ".//div[@data-testid='User-Name']//span")
            author_name = author_name_element.text
            
            # 提取用户名（@handle）
            user_handle_element = tweet_article.find_element(By.XPATH, ".//div[@data-testid='User-Name']//div[contains(@class, 'r-1wbh5a2')]")
            user_handle = user_handle_element.text
            
            print(f"作者: {author_name} ({user_handle})")
            print(f"内容:\n{tweet_text}\n")
            
            # 将抓取的数据存起来
            all_tweets_data.append({
                "url": url,
                "author": author_name,
                "handle": user_handle,
                "text": tweet_text
            })

            # 增加一个小的随机延时，模仿人类行为，降低被封锁的风险
            time.sleep(2)

        except Exception as e:
            print(f"抓取失败: {url}\n错误信息: {e}\n")
            continue

finally:
    # 5. 关闭浏览器
    print("所有抓取任务完成，关闭浏览器。")
    driver.quit()

# 你可以在这里对 all_tweets_data 做进一步处理，比如保存到文件
# print(all_tweets_data)