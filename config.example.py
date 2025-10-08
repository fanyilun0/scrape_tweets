# 配置文件模板
# 使用方法：
# 1. 复制 .env.example 为 .env: cp .env.example .env
# 2. 编辑 .env 文件，填入你的实际配置
# 3. 本文件 (config.py) 会自动从 .env 读取配置

# 注意：本文件已被更新为从环境变量读取配置，不再需要手动修改此文件
# 所有敏感配置都应该放在 .env 文件中

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ==================== Webhook配置 ====================
# 从环境变量读取，如果没有则使用默认值
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_WEBHOOK_KEY")

# ==================== 代理配置 ====================
# 从环境变量读取
USE_PROXY = os.getenv("USE_PROXY", "true").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL", "http://127.0.0.1:7890")

# Chrome浏览器代理配置（用于Selenium访问Twitter）
CHROME_PROXY = os.getenv("CHROME_PROXY", "http://127.0.0.1:7890")
if CHROME_PROXY in ["", "None", "none", "null"]:
    CHROME_PROXY = None

# ==================== 监听配置 ====================
# 从环境变量读取
LIST_CHECK_INTERVAL = int(os.getenv("LIST_CHECK_INTERVAL", "300"))
MAX_TWEETS_PER_CHECK = int(os.getenv("MAX_TWEETS_PER_CHECK", "20"))

# ==================== 持久化配置 ====================
USE_PERSISTENT_PROFILE = True
PROFILE_DIR = "./chrome_profile"
PUSHED_IDS_FILE = "pushed_tweet_ids.json"

