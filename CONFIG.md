# 配置说明

## 📝 可配置参数

在 `main.py` 文件顶部的配置区域，你可以调整以下参数：

```python
# ==================== 配置区域 ====================
# 代理配置（如果不需要代理，设置为None）
PROXY = "http://127.0.0.1:7890"  # 默认代理地址，可以设置为None禁用

# 是否使用持久化Profile（第一次运行需要手动登录，之后会保存登录状态）
USE_PERSISTENT_PROFILE = True
PROFILE_DIR = "./chrome_profile"

# 已抓取推文ID记录文件（避免重复抓取）
SCRAPED_IDS_FILE = "scraped_tweet_ids.json"
```

---

## 🌐 代理配置详解

### 选项1：使用本地代理（默认）
```python
PROXY = "http://127.0.0.1:7890"
```
适用场景：
- 已安装 Clash、V2Ray 等代理工具
- 代理工具监听在 7890 端口（Clash默认端口）

### 选项2：使用其他代理
```python
# HTTP代理
PROXY = "http://your_proxy_ip:port"

# HTTPS代理
PROXY = "https://your_proxy_ip:port"

# 带认证的代理
PROXY = "http://username:password@proxy_ip:port"

# SOCKS5代理
PROXY = "socks5://your_proxy_ip:port"
```

### 选项3：不使用代理
```python
PROXY = None
```
适用场景：
- 网络环境良好，无需代理
- 小规模抓取（<100条）

---

## 💾 持久化Profile配置

### 启用持久化（推荐）
```python
USE_PERSISTENT_PROFILE = True
PROFILE_DIR = "./chrome_profile"
```

**优势**：
- ✅ 首次登录后，之后自动保持登录状态
- ✅ 避免频繁登录触发风险检测
- ✅ 提升运行效率

**注意**：
- `chrome_profile` 目录会保存你的登录信息和浏览器数据
- 请妥善保管该目录，不要提交到Git仓库
- 如需切换账号，删除该目录即可

### 禁用持久化
```python
USE_PERSISTENT_PROFILE = False
```

**场景**：
- 每次运行都想用不同的账号
- 测试环境，不想保存数据

---

## 📊 抓取记录配置

### 启用断点续传（推荐）
```python
SCRAPED_IDS_FILE = "scraped_tweet_ids.json"
```

**功能**：
- 自动记录已抓取的推文ID
- 重复运行时跳过已抓取内容
- 支持中断后继续抓取

### 禁用记录
如果不需要此功能，可以在代码中注释掉相关逻辑：
```python
# 注释掉这些行
# scraped_ids = load_scraped_ids()
# if tweet_id in scraped_ids:
#     continue
# save_scraped_id(tweet_id)
```

---

## ⏱️ 延时配置

### 调整随机延时范围

在主循环中找到 `random_sleep()` 调用：

```python
# 默认配置：3-7秒随机延时
random_sleep(3, 7)
```

#### 更保守（推荐用于大规模抓取）
```python
random_sleep(5, 10)  # 5-10秒
```

#### 更激进（风险较高，仅限小规模测试）
```python
random_sleep(2, 4)   # 2-4秒
```

#### 固定延时（不推荐）
```python
time.sleep(5)  # 固定5秒
```

---

## 🎲 行为随机化配置

### 调整"意外"操作概率

在主循环中找到：

```python
# 默认：5%概率执行随机操作
if random.random() < 0.05:
```

#### 提高概率（更像人类）
```python
if random.random() < 0.10:  # 10%概率
```

#### 降低概率
```python
if random.random() < 0.02:  # 2%概率
```

#### 禁用此功能
```python
if False:  # 永远不执行
```

### 调整滚动次数

在 `simulate_human_scroll()` 函数中：

```python
# 默认：随机滚动1-3次
scroll_times = random.randint(1, 3)
```

#### 增加滚动次数
```python
scroll_times = random.randint(2, 5)  # 2-5次
```

#### 减少滚动次数
```python
scroll_times = 1  # 固定1次
```

---

## 🔧 Chrome选项配置

在 `create_undetected_driver()` 函数中，可以添加更多Chrome选项：

### 无头模式（后台运行，不显示浏览器窗口）
```python
options.add_argument('--headless')
```
⚠️ 注意：无头模式更容易被检测，不推荐用于反爬虫场景

### 禁用图片加载（提升速度）
```python
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
```

### 设置窗口大小
```python
options.add_argument('--window-size=1920,1080')
```

### 禁用GPU加速
```python
options.add_argument('--disable-gpu')
```

---

## 📁 文件和目录说明

| 文件/目录 | 说明 | 是否提交到Git |
|----------|------|---------------|
| `chrome_profile/` | Chrome浏览器Profile数据 | ❌ 不提交（已在.gitignore） |
| `scraped_tweet_ids.json` | 已抓取推文ID记录 | ✅ 可提交 |
| `tweets_images_*/` | 下载的图片目录 | ❌ 不提交（文件太大） |
| `tweets_data_*.csv` | 导出的CSV数据 | ✅ 可提交 |
| `tweets_data_*.md` | 导出的Markdown文档 | ✅ 可提交 |

---

## 🎯 不同场景的推荐配置

### 场景1：首次使用 / 测试
```python
PROXY = None  # 先不用代理测试
USE_PERSISTENT_PROFILE = True
random_sleep(3, 7)  # 默认延时
```

### 场景2：日常使用（<100条）
```python
PROXY = "http://127.0.0.1:7890"  # 使用本地代理
USE_PERSISTENT_PROFILE = True
random_sleep(3, 7)  # 默认延时
```

### 场景3：大规模抓取（>500条）
```python
PROXY = "http://residential_proxy:port"  # 使用住宅代理
USE_PERSISTENT_PROFILE = True
random_sleep(5, 10)  # 增加延时
# 提高"意外"操作概率到10%
```

### 场景4：临时快速抓取（风险自负）
```python
PROXY = None
USE_PERSISTENT_PROFILE = True
random_sleep(2, 4)  # 减少延时
# 禁用"意外"操作
```

---

## ⚠️ 重要提示

1. **代理端口检查**
   - Clash 默认：`7890`
   - V2Ray 默认：`10808`（HTTP）/ `10809`（SOCKS5）
   - 请根据你的代理工具配置调整

2. **首次运行**
   - 建议先用少量推文测试（修改 `original_text`）
   - 确认配置正确后再进行大规模抓取

3. **安全建议**
   - 不要将 `chrome_profile` 目录提交到Git
   - 不要在代码中硬编码敏感的代理认证信息
   - 定期清理旧的图片目录释放磁盘空间

4. **性能vs安全**
   - 延时越短，速度越快，但风险越高
   - 建议在安全和效率之间找到平衡点

---

## 🔍 检查配置是否正确

运行前检查清单：

- [ ] 代理服务是否正常运行？（如使用代理）
- [ ] Chrome浏览器是否已安装？
- [ ] 依赖是否已安装？`pip install -r requirements.txt`
- [ ] 首次运行是否准备好手动登录？
- [ ] 磁盘空间是否充足？（图片会占用空间）

---

## 📞 问题反馈

如配置遇到问题，请检查：
1. 代理是否能正常访问 Twitter/X？
2. 终端是否有详细的错误信息？
3. 是否有防火墙或安全软件阻止？

更多帮助请查看：
- [USAGE_GUIDE.md](./USAGE_GUIDE.md) - 完整使用指南
- [OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md) - 优化总结

