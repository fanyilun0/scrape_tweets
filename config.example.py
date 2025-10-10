# 配置文件模板
# 使用方法：
# 1. 创建 .env 文件，添加以下配置
# 2. 编辑 .env 文件，填入你的实际配置
# 3. 本文件 (config.py) 会自动从 .env 读取配置

# 注意：本文件已被更新为从环境变量读取配置，不再需要手动修改此文件
# 所有敏感配置都应该放在 .env 文件中

# .env 文件示例内容：
# WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_WEBHOOK_KEY
# USE_WEBHOOK_PROXY=false
# WEBHOOK_PROXY_URL=http://127.0.0.1:7890
# USE_CHROME_PROXY=false
# CHROME_PROXY_URL=http://127.0.0.1:7890
# LIST_CHECK_INTERVAL=240
# MAX_TWEETS_PER_CHECK=10

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ==================== Webhook配置 ====================
# 从环境变量读取，如果没有则使用默认值
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_WEBHOOK_KEY")

# ==================== 代理配置 ====================
# Webhook 代理配置（独立控制）
USE_WEBHOOK_PROXY = os.getenv("USE_WEBHOOK_PROXY", "false").lower() == "true"
WEBHOOK_PROXY_URL = os.getenv("WEBHOOK_PROXY_URL", "http://127.0.0.1:7890")

# Chrome 代理配置（独立控制，用于Selenium访问Twitter）
USE_CHROME_PROXY = os.getenv("USE_CHROME_PROXY", "false").lower() == "true"
CHROME_PROXY_URL = os.getenv("CHROME_PROXY_URL", "http://127.0.0.1:7890")

# 根据开关决定实际使用的代理
CHROME_PROXY = CHROME_PROXY_URL if USE_CHROME_PROXY else None

# ==================== 监听配置 ====================
# 从环境变量读取
LIST_CHECK_INTERVAL = int(os.getenv("LIST_CHECK_INTERVAL", "300"))
MAX_TWEETS_PER_CHECK = int(os.getenv("MAX_TWEETS_PER_CHECK", "20"))

# ==================== 持久化配置 ====================
USE_PERSISTENT_PROFILE = True
PROFILE_DIR = "./chrome_profile"
PUSHED_IDS_FILE = "pushed_tweet_ids.json"

