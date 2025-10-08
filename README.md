# 推特列表高级监听机器人 (Advanced Twitter List Monitor)

这是一个功能强大的 Python 脚本，用于实时监控一个或多个指定的 Twitter/X 列表。当列表中出现新推文时，它能智能识别推文类型（原创、转推、回复、引用），并提取丰富的信息，通过 Webhook 将格式化后的消息推送到你选择的通知服务（如 Discord、Telegram、飞书等）。

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 功能特性

- **多列表监控**: 支持同时监控任意数量的公开 Twitter 列表。
- **实时 Webhook 推送**: 快速将新推文和运行错误推送到指定服务。
- **精准的推文类型识别**:
    - 🐦 **原创推文**: 捕获作者、内容、图片和时间。
    - 🔄 **转推 (Retweet)**: 清晰展示**转推者**和**原作者**，还原信息传播路径。
    - 💬 **回复 (Reply)**: 识别回复行为，并提取**被回复的用户**列表。
    - 📖 **引用 (Quote)**: **同时捕获**新的评论和被引用的**完整原文**，提供完整的对话上下文。
- **强大的用户白名单**: 可选的用户白名单功能，只推送你关心的特定用户的动态（包括他们的原创、转推、回复和引用）。
- **持久化登录**: 利用浏览器 Profile 实现持久化登录，一次登录后无需再次扫码或输入密码。
- **反检测优化**: 基于 `undetected-chromedriver`，有效降低被 Twitter/X 检测为自动化工具的风险。
- **丰富的信息提取**: 全面解析推文，包括作者、转推者、正文、图片、时间、推文链接以及被引用推文的全部信息。
- **健壮的日志与错误处理**:
    - 在终端输出彩色日志，直观了解运行状态。
    - 将所有日志记录到 `monitor.log` 文件中，方便排查问题。
    - 运行中发生严重错误时，会自动将错误详情推送到 Webhook。

## ⚙️ 环境要求

- Python 3.12 或更高版本
- Google Chrome 浏览器
- `pip` 或 `uv` 包管理工具

## 🚀 快速开始

### 1. 下载项目文件

将项目文件下载或克隆到你的本地文件夹。

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. 创建并配置环境

强烈建议使用 Python 虚拟环境。

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境 (macOS/Linux)
source venv/bin/activate
# (Windows)
# venv\Scripts\activate
```

### 3. 安装依赖

项目依赖以下 Python 库：
- `undetected-chromedriver`: 核心驱动库
- `selenium`: 浏览器自动化框架
- `requests`: 用于下载图片和发送 Webhook

创建一个名为 `requirements.txt` 的文件，内容如下：
```txt
undetected-chromedriver
selenium
requests
```

然后运行以下命令安装：
```bash
# 使用 pip
pip install -r requirements.txt

# 或者，如果你使用 uv
uv pip install -r requirements.txt
```

### 4. 配置文件 (`config.py`)

**这是最关键的一步。** 请在项目根目录下创建一个名为 `config.py` 的文件，并根据你的需求填入以下内容：

```python
# ==================== 浏览器配置 ====================
# 代理设置 (如果你的网络环境需要)
# 不需要代理则设置为 None
CHROME_PROXY = "http://127.0.0.1:7890"

# 是否使用持久化 Profile (强烈建议开启)
# 开启后，第一次登录信息会保存在 PROFILE_DIR 文件夹中，后续无需再次登录
USE_PERSISTENT_PROFILE = True
PROFILE_DIR = "./chrome_profile"  # Profile 保存路径

# ==================== 监控配置 ====================
# 你要监控的 Twitter 列表 URL (可以添加多个)
TWITTER_LISTS = [
    "https://x.com/i/lists/1234567890",
    "https://x.com/i/lists/0987654321"
]

# 检查列表的间隔时间 (秒)
LIST_CHECK_INTERVAL = 240

# 每次检查时，最多从列表顶部获取的推文数量
# 建议设为 20-30，以防错过快速刷屏的推文
MAX_TWEETS_PER_CHECK = 20

# ==================== 用户过滤配置 ====================
# 是否启用用户白名单过滤
# True: 只推送 MONITORED_USERS 中用户的推文/转推/回复/引用
# False: 推送列表中的所有新推文
ENABLE_USER_FILTER = True

# 用户白名单 (Twitter Handle，不带@)
# 仅在 ENABLE_USER_FILTER = True 时生效
MONITORED_USERS = [
    "elonmusk",
    "VitalikButerin"
]

# ==================== 文件路径配置 ====================
# 用于记录已推送推文ID的文件，防止重复推送
PUSHED_IDS_FILE = "./pushed_ids.json"
```

### 5. Webhook 配置 (`webhook.py`)

你需要根据你使用的通知服务（如 Discord、Telegram、飞书等）来实现具体的推送逻辑。在项目根目录下创建一个 `webhook.py` 文件，并参考以下模板进行修改：

```python
# 以 Discord 为例
import requests
import asyncio

# 你的企业微信 Webhook URL
WEBHOOK_URL = ""

async def send_message_async(message, msg_type="text"):
    """异步发送文本消息"""
    payload = {
        "content": message
    }
    try:
        loop = asyncio.get_event_loop()
        # 在异步函数中使用 run_in_executor 来运行同步的网络请求
        await loop.run_in_executor(
            None, 
            lambda: requests.post(WEBHOOK_URL, json=payload, timeout=10)
        )
        return True
    except Exception as e:
        print(f"发送 Webhook 消息失败: {e}")
        return False

async def send_image_async(image_base64):
    """异步发送图片消息 (Base64 格式)"""
    # 此处仅为功能占位，请根据你的服务自行实现。
    return True
```

## ▶️ 运行脚本

1.  确保你的虚拟环境已激活，并且所有配置都已完成。
2.  在终端中运行主脚本：

    ```bash
    python list_monitor.py
    # 或者
    uv run list_monitor.py
    ```
3.  **首次运行**: 脚本会自动打开一个 Chrome 浏览器。如果检测到你未登录 Twitter/X，它会在终端提示你手动登录。请在弹出的浏览器窗口中完成登录操作，然后回到终端按 `Enter` 键继续。你的登录状态会被保存到 `chrome_profile` 文件夹中，后续运行无需再次登录。
4.  脚本启动成功后，将开始按设定的间隔周期性检查列表。
5.  要停止脚本，请在终端中按 `Ctrl + C`。

## 📁 文件结构

```
.
├── list_monitor.py     # 主脚本
├── config.py           # 配置文件 (需自行创建) ❗️
├── webhook.py          # Webhook推送实现 (需自行创建) ❗️
├── requirements.txt    # 依赖库清单
├── monitor.log         # 运行日志（自动生成）
└── pushed_ids.json     # 已推送推文ID记录（自动生成）
```

## ⚠️ 故障排查

- **脚本启动时 Chrome 崩溃**:
  - **原因**: `undetected-chromedriver` 与你的 Chrome 浏览器版本不兼容。这通常发生在 Chrome 自动更新后。
  - **解决方案**:
    1.  运行 `pip install --upgrade undetected-chromedriver` 更新库。
    2.  如果问题依旧，在 `list_monitor.py` 的 `create_undetected_driver` 函数中明确指定 Chrome 版本号，例如 `driver = uc.Chrome(version_main=141, options=options)`（请将 `141` 替换为你的 Chrome 主版本号）。

- **无法加载已推送 ID / JSON 错误**:
  - **原因**: `pushed_ids.json` 文件可能为空或内容损坏。
  - **解决方案**: 删除 `pushed_ids.json` 文件，脚本下次运行时会自动重新创建。

- **无法提取推文 / 频繁报错**:
  - **原因**: Twitter/X 更新了前端页面结构，导致脚本中的 XPath 选择器失效。
  - **解决方案**: 这是 Web 爬虫的常见问题。需要分析新的 HTML 结构，并更新 `extract_tweet_data` 函数中的 XPath 表达式。

## 📜 许可

本项目采用 [MIT License](https://opensource.org/licenses/MIT) 授权。