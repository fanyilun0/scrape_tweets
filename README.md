# Twitter/X 推文抓取工具

这是一个用于批量抓取 Twitter(X) 推文内容的 Python 脚本，支持自动提取推文文本、发布时间、高清图片等信息，并生成 CSV 和 Markdown 格式的输出文件。

## ✨ 最新更新（v2.0）

**全面优化反爬虫策略，解决登录限制问题！**

- 🚀 **使用 undetected_chromedriver** - 自动移除浏览器自动化检测特征
- 🔐 **持久化登录状态** - 首次手动登录，之后自动保持登录
- 🌐 **代理服务器支持** - 默认支持本地代理（http://127.0.0.1:7890）
- 🎭 **人类行为模拟** - 随机延时、自动滚动、意外操作
- 📊 **断点续传** - 自动记录已抓取推文，支持中断后继续
- ⚡ **智能登录检测** - 自动判断是否需要登录

详细更新说明：[OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)

## 功能特性

- ✅ 批量抓取推文内容
- ✅ 提取推文发布时间和用户信息
- ✅ 自动下载推文中的高清图片（原图质量）
- ✅ 生成 CSV 文件（适合数据分析）
- ✅ 生成 Markdown 文档（带图片预览，适合阅读）
- ✅ 反检测技术（undetected_chromedriver）
- ✅ 行为随机化，极大降低被封锁风险
- ✅ 持久化登录，避免重复登录触发风险
- ✅ 断点续传，支持中断后继续抓取

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `undetected-chromedriver` - 反检测浏览器驱动
- `selenium` - Web自动化框架
- `requests` - HTTP请求库

### 2. 配置代理（可选）

编辑 `main.py` 顶部配置：

```python
# 使用代理（默认）
PROXY = "http://127.0.0.1:7890"

# 不使用代理
PROXY = None
```

### 3. 运行脚本

```bash
python main.py
```

### 4. 首次登录（仅首次需要）

- 脚本自动打开 Chrome 浏览器
- 如检测到未登录，按提示手动登录
- 登录成功后按 Enter 键继续
- **登录信息会自动保存，下次无需重复登录！**

### 5. 查看结果

生成的文件：
- 📄 `tweets_data_*.csv` - 结构化数据
- 📝 `tweets_data_*.md` - Markdown文档
- 🖼️ `tweets_images_*/` - 图片目录
- 📊 `scraped_tweet_ids.json` - 抓取记录

更详细的使用说明：**[QUICK_START.md](./QUICK_START.md)** ⭐

## 输出文件

运行完成后会生成以下文件：

### 1. CSV 文件 (`tweets_data_YYYYMMDD_HHMMSS.csv`)
包含字段：
- 序号
- 用户名
- 发布时间
- 推文链接
- 推文内容
- 图片数量
- 图片URL

### 2. Markdown 文档 (`tweets_data_YYYYMMDD_HHMMSS.md`)
包含：
- 每条推文的完整内容
- 发布时间和链接
- 嵌入的本地图片（可预览）
- 原图 URL 链接

### 3. 图片目录 (`tweets_images_YYYYMMDD_HHMMSS/`)
存储所有下载的推文图片，命名格式：
- `tweet_1_img_1.jpg`
- `tweet_1_img_2.jpg`
- `tweet_2_img_1.jpg`
- ...

## 📚 文档导航

- **[QUICK_START.md](./QUICK_START.md)** - 5分钟快速上手指南 ⭐ 推荐新手阅读
- **[OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)** - 反爬虫优化总结
- **[CONFIG.md](./CONFIG.md)** - 详细配置说明
- **[USAGE_GUIDE.md](./USAGE_GUIDE.md)** - 完整使用指南
- **[todo.md](./todo.md)** - 原始需求和技术分析

## ⚙️ 配置说明

### 自定义推文链接

修改 `main.py` 中的 `original_text` 变量，替换为你需要抓取的推文链接。

### 代理配置

```python
# 默认使用本地代理
PROXY = "http://127.0.0.1:7890"

# 使用其他代理
PROXY = "http://your_proxy:port"

# 不使用代理
PROXY = None
```

### 延时配置

在 `random_sleep()` 调用处调整：

```python
# 默认 3-7 秒随机延时
random_sleep(3, 7)

# 更保守（5-10秒）
random_sleep(5, 10)
```

详细配置请参考：[CONFIG.md](./CONFIG.md)

## 🛡️ 反爬虫策略

本工具采用多层反检测技术：

| 策略 | 实施方式 | 效果 |
|------|---------|------|
| **浏览器指纹消除** | undetected_chromedriver | ⭐⭐⭐⭐⭐ |
| **持久化登录** | Chrome Profile | ⭐⭐⭐⭐⭐ |
| **行为随机化** | 随机延时+滚动 | ⭐⭐⭐⭐ |
| **意外操作** | 5%概率随机动作 | ⭐⭐⭐ |
| **代理支持** | 可配置代理服务器 | ⭐⭐⭐⭐⭐ |

## ❓ 常见问题

### Q: 遇到"Could not log you in now"错误？
**A:** 这正是本次优化要解决的问题！现在使用了 `undetected_chromedriver` 和持久化登录，极大降低了此错误的发生率。

### Q: 代理连接失败？
**A:** 检查代理是否运行，或设置 `PROXY = None` 不使用代理。

### Q: 如何切换账号？
**A:** 删除 `chrome_profile` 目录，重新运行脚本。

### Q: 抓取速度能否更快？
**A:** 可以调整延时参数，但不建议过快，会增加被检测风险。

更多问题解答：[QUICK_START.md](./QUICK_START.md)

## ⚠️ 注意事项

1. **首次运行**：需要手动登录，之后自动保持登录状态
2. **代理配置**：默认使用 `http://127.0.0.1:7890`，请确保代理运行或禁用
3. **抓取频率**：默认 3-7 秒随机延时，不建议调整过快
4. **合法使用**：请遵守 Twitter/X 服务条款，仅用于个人学习研究

## 📋 系统要求

- Python 3.7+
- Chrome 浏览器（最新版）
- 稳定的网络连接
- （可选）代理服务器

## 📦 依赖项

```
selenium>=4.0.0
undetected-chromedriver>=3.5.0
requests>=2.28.0
```

## 许可证

MIT License


