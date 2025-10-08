import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# Webhook配置（从环境变量读取）
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_WEBHOOK_KEY")

# 代理配置（从环境变量读取）
USE_PROXY = os.getenv("USE_PROXY", "true").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL", "http://127.0.0.1:7890")

# Chrome代理配置（用于Selenium）
CHROME_PROXY = os.getenv("CHROME_PROXY", "http://127.0.0.1:7890")
# 如果环境变量设置为空字符串或 "None"，则设置为 None
if CHROME_PROXY in ["", "None", "none", "null"]:
    CHROME_PROXY = None

# 推特列表监听配置
LIST_CHECK_INTERVAL = int(os.getenv("LIST_CHECK_INTERVAL", "240"))  # 检查间隔（秒），默认240秒(4分钟)
MAX_TWEETS_PER_CHECK = int(os.getenv("MAX_TWEETS_PER_CHECK", "20"))  # 每次检查最多获取的推文数量

# 持久化配置
USE_PERSISTENT_PROFILE = True
PROFILE_DIR = "./chrome_profile"

# 已推送推文ID记录文件
PUSHED_IDS_FILE = "pushed_tweet_ids.json"

# 要监听的推特列表URL（可以配置多个）
TWITTER_LISTS = [
    "https://x.com/i/lists/1876489130466816018"  # 测试列表
]

# 要监听的用户白名单（只推送这些用户的推文或转推）
# 格式：用户名（不含@符号），例如 "elonmusk", "0xSunNFT"
# 如果列表为空，则推送所有用户的推文
MONITORED_USERS = [
    'pepeboost888',
    'Arya_web3',    
    'web3feng',
    'cryptoDevinL',
    'brc20niubi',
    '0xcryptowizard',
    'cryptocishanjia',
    '0xsunnft',
    'cz_binance',
    'heyibinance',
    'huigendeshen',
    'ouyoung11'
]

# 是否启用用户白名单过滤（True=只推送白名单用户，False=推送所有用户）
ENABLE_USER_FILTER = True

