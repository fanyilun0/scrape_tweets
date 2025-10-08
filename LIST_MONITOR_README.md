# 推特列表监听功能

## 📌 概述

基于 `main.py` 的推特爬虫模板，新增了 **推特列表监听功能**，可以自动监听指定的 Twitter 列表，并将新推文实时推送到企业微信群。

## 🎯 主要功能

- ✅ **自动监听**: 定时检查指定的推特列表
- ✅ **实时推送**: 新推文自动推送到企业微信
- ✅ **图片支持**: 自动下载并推送推文中的图片
- ✅ **去重机制**: 避免重复推送已推送过的推文
- ✅ **多列表支持**: 可同时监听多个推特列表
- ✅ **断点续传**: 中断后重启不会丢失记录
- ✅ **持久登录**: 首次登录后自动保持登录状态

## 📂 新增文件说明

### 核心文件

| 文件 | 说明 | 用途 |
|-----|------|------|
| `list_monitor.py` | 主脚本 | 推特列表监听的核心逻辑 |
| `config.py` | 配置文件 | Webhook、代理、监听参数配置 |
| `config.example.py` | 配置模板 | 配置文件的模板和示例 |

### 数据文件

| 文件 | 说明 | 是否提交Git |
|-----|------|-----------|
| `pushed_tweet_ids.json` | 已推送记录 | ❌ 可选 |
| `chrome_profile/` | 浏览器数据 | ❌ 不提交 |

### 文档文件

| 文件 | 说明 |
|-----|------|
| `LIST_MONITOR_QUICKSTART.md` | 快速开始指南 |
| `LIST_MONITOR_GUIDE.md` | 详细使用文档 |
| `TEST_LIST_MONITOR.md` | 测试指南 |
| `LIST_MONITOR_README.md` | 本文档 |

## 🚀 快速开始

### 1. 准备配置文件

```bash
cp config.example.py config.py
```

### 2. 编辑配置

最少需要修改 `config.py` 中的：

```python
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key"
```

### 3. 配置监听列表

编辑 `list_monitor.py`，修改：

```python
TWITTER_LISTS = [
    "https://x.com/i/lists/1876489130466816018"  # 改为你的列表URL
]
```

### 4. 运行

```bash
python list_monitor.py
```

首次运行需要在浏览器中手动登录 Twitter，登录成功后按 Enter 开始监听。

## 📚 详细文档

- 🚀 **快速开始**: [LIST_MONITOR_QUICKSTART.md](./LIST_MONITOR_QUICKSTART.md) - 3分钟快速上手
- 📖 **使用指南**: [LIST_MONITOR_GUIDE.md](./LIST_MONITOR_GUIDE.md) - 完整功能说明
- 🧪 **测试指南**: [TEST_LIST_MONITOR.md](./TEST_LIST_MONITOR.md) - 测试和调试方法

## ⚙️ 配置说明

### 主要配置项

```python
# Webhook配置
WEBHOOK_URL = "企业微信webhook地址"

# 代理配置
CHROME_PROXY = "http://127.0.0.1:7890"  # 或 None

# 监听间隔
LIST_CHECK_INTERVAL = 300  # 秒，默认5分钟

# 每次抓取数量
MAX_TWEETS_PER_CHECK = 20  # 默认20条
```

### 监听列表配置

```python
# 单个列表
TWITTER_LISTS = [
    "https://x.com/i/lists/1876489130466816018"
]

# 多个列表
TWITTER_LISTS = [
    "https://x.com/i/lists/list1",
    "https://x.com/i/lists/list2",
    "https://x.com/i/lists/list3",
]
```

## 📊 推送消息格式

### 文本消息

```
🐦 新推文监听

👤 作者: 显示名称 (@username)
🕐 时间: 2025-10-08 12:34:56
🔗 链接: https://x.com/username/status/1234567890

📝 内容:
推文的内容会在这里显示...

🖼️ 包含 2 张图片
```

### 图片推送

文本消息后会自动推送推文中的所有图片（原图质量）。

## 🔧 技术实现

### 核心技术栈

- `undetected-chromedriver`: 反检测浏览器驱动
- `selenium`: 网页自动化和数据提取
- `aiohttp`: 异步 HTTP 请求（Webhook 推送）
- `requests`: 图片下载

### 工作流程

```
启动脚本
    ↓
加载已推送记录
    ↓
启动浏览器 & 检查登录
    ↓
┌─────────────────┐
│   监听循环      │
│                 │
│  访问列表页面   │
│       ↓         │
│  抓取推文数据   │
│       ↓         │
│  过滤新推文     │
│       ↓         │
│  推送到Webhook  │
│       ↓         │
│  保存推送记录   │
│       ↓         │
│  等待下次检查   │
└─────────────────┘
```

### 去重机制

1. 使用 `pushed_tweet_ids.json` 记录所有已推送的推文ID
2. 每次抓取后与记录对比，过滤掉已推送的推文
3. 推送成功后立即保存ID，确保不丢失
4. 即使脚本重启，也能正确识别已推送的推文

## 🎯 应用场景

### 场景1: 行业动态监听

监听行业专家和意见领袖，第一时间获取行业动态。

```python
TWITTER_LISTS = ["https://x.com/i/lists/tech_experts"]
LIST_CHECK_INTERVAL = 300  # 5分钟
```

### 场景2: 新闻事件追踪

监听新闻媒体和记者，追踪突发事件。

```python
TWITTER_LISTS = ["https://x.com/i/lists/breaking_news"]
LIST_CHECK_INTERVAL = 60  # 1分钟，实时性要求高
```

### 场景3: 竞品情报收集

监听竞争对手和相关公司，收集市场情报。

```python
TWITTER_LISTS = ["https://x.com/i/lists/competitors"]
LIST_CHECK_INTERVAL = 600  # 10分钟
```

### 场景4: 投资信息追踪

监听加密货币、股票相关账号，捕捉投资信号。

```python
TWITTER_LISTS = [
    "https://x.com/i/lists/crypto_influencers",
    "https://x.com/i/lists/stock_analysts"
]
LIST_CHECK_INTERVAL = 120  # 2分钟
```

## ⚠️ 注意事项

### 账号安全

- ✅ 使用持久化登录，避免频繁登录
- ✅ 合理设置检查间隔，避免过于频繁
- ✅ 使用固定代理，避免频繁切换IP
- ❌ 不要设置过短的检查间隔（<1分钟）

### 数据安全

- ✅ `config.py` 已加入 `.gitignore`，不会提交敏感配置
- ✅ `chrome_profile` 已加入 `.gitignore`，保护登录信息
- ❌ 不要分享你的 Webhook URL
- ❌ 不要将配置文件上传到公开仓库

### 使用限制

- 企业微信机器人：每分钟最多20条消息
- Twitter API：无API key要求，但需要人工登录
- 图片大小：建议<2MB（企业微信限制）

## 🆚 与 main.py 的区别

| 特性 | main.py | list_monitor.py |
|-----|---------|-----------------|
| 用途 | 一次性抓取指定推文 | 持续监听列表新推文 |
| 运行方式 | 运行一次后结束 | 循环运行，定时检查 |
| 数据来源 | 手动指定的推文URL | 推特列表中的推文 |
| 输出方式 | 保存为CSV和MD文件 | 推送到企业微信 |
| 去重方式 | scraped_tweet_ids.json | pushed_tweet_ids.json |
| 图片处理 | 下载到本地 | 下载并推送到webhook |

## 🔄 与原有项目的关系

```
scrape_tweets/
├── main.py              # 原有脚本：批量抓取推文
├── webhook.py           # Webhook推送模块（复用）
│
├── list_monitor.py      # 🆕 新增：列表监听脚本
├── config.py            # 🆕 新增：统一配置文件
├── config.example.py    # 🆕 新增：配置模板
│
├── scraped_tweet_ids.json   # main.py使用
├── pushed_tweet_ids.json    # 🆕 list_monitor.py使用
│
└── docs/
    ├── LIST_MONITOR_QUICKSTART.md  # 🆕 快速开始
    ├── LIST_MONITOR_GUIDE.md       # 🆕 详细指南
    └── TEST_LIST_MONITOR.md        # 🆕 测试指南
```

**互不影响**：
- `main.py` 和 `list_monitor.py` 可以独立运行
- 使用不同的记录文件，互不干扰
- 共享 `webhook.py` 模块和 `chrome_profile` 目录

## 📈 性能参考

### 资源占用

- **内存**: 200-500MB（主要是Chrome浏览器）
- **CPU**: 10-30%（非持续，仅抓取时）
- **网络**: 取决于推文数量和图片数量

### 时间消耗

- **启动时间**: 10-20秒
- **单次检查**: 10-30秒（取决于推文数量）
- **推送延时**: 1-5秒/条

### 建议配置

| 监听强度 | 列表数 | 检查间隔 | 每次抓取 |
|---------|-------|---------|---------|
| 低频 | 1-3 | 10-30分钟 | 10条 |
| 中频 | 3-5 | 5-10分钟 | 20条 |
| 高频 | 5-10 | 2-5分钟 | 20-30条 |
| 实时 | 1-2 | 1-2分钟 | 30-50条 |

## 🐛 故障排查

### 常见问题

1. **无法启动**: 检查 Chrome 和依赖是否安装
2. **登录失败**: 删除 `chrome_profile` 重新登录
3. **抓取失败**: 检查列表URL和网络连接
4. **推送失败**: 检查 Webhook URL 和网络

详细排查方法请参考 [LIST_MONITOR_GUIDE.md](./LIST_MONITOR_GUIDE.md)

## 📞 获取帮助

- 📖 阅读 [详细指南](./LIST_MONITOR_GUIDE.md)
- 🚀 查看 [快速开始](./LIST_MONITOR_QUICKSTART.md)
- 🧪 参考 [测试指南](./TEST_LIST_MONITOR.md)
- 📝 查看终端日志输出

## 🎉 开始使用

准备好了吗？

```bash
# 1. 配置
cp config.example.py config.py
nano config.py  # 修改 WEBHOOK_URL

# 2. 运行
python list_monitor.py

# 3. 首次登录
# 在浏览器中登录 Twitter，然后按 Enter

# 4. 开始监听
# 脚本会自动循环检查并推送新推文
```

祝使用愉快！🎊

---

**项目地址**: [scrape_tweets](https://github.com/your-repo/scrape_tweets)

**最后更新**: 2025-10-08

