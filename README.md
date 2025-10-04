# Twitter/X 推文抓取工具

这是一个用于批量抓取 Twitter(X) 推文内容的 Python 脚本，支持自动提取推文文本、发布时间、高清图片等信息，并生成 CSV 和 Markdown 格式的输出文件。

## 功能特性

- ✅ 批量抓取推文内容
- ✅ 提取推文发布时间
- ✅ 自动下载推文中的高清图片（点击大图后获取原图）
- ✅ 生成 CSV 文件（适合数据分析）
- ✅ 生成 Markdown 文档（带图片预览，适合阅读）
- ✅ 多种浏览器启动方式（避免 SSL 错误）
- ✅ 模拟人类行为，降低被封锁风险

## 安装依赖

### 方法 1: 使用 pip
```bash
pip install -r requirements.txt
```

### 方法 2: 使用 uv（推荐）
```bash
uv pip install -r requirements.txt
```

### 安装 ChromeDriver
```bash
brew install chromedriver
```

## 使用方法

1. **激活虚拟环境**（如果使用）：
   ```bash
   source .venv/bin/activate
   ```

2. **运行脚本**：
   ```bash
   python main.py
   ```

3. **手动登录**：
   - 脚本会自动打开 Chrome 浏览器并导航到 X(Twitter) 登录页
   - 在浏览器中手动登录你的 X 账号
   - 登录成功后，回到终端窗口，按 **Enter** 键继续

4. **等待抓取完成**：
   - 脚本会自动访问所有推文链接
   - 抓取内容、时间和图片
   - 显示进度信息

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

## 配置说明

如果需要抓取不同的推文，修改 `main.py` 中的 `original_text` 变量，将其中的推文链接替换为你需要抓取的链接。

## 注意事项

1. **网络连接**：确保网络稳定，能够访问 Twitter/X
2. **登录状态**：需要有效的 X 账号进行登录
3. **抓取速度**：脚本内置延时机制，避免过快请求被封锁
4. **图片下载**：如果图片较多，下载时间可能较长
5. **浏览器版本**：确保 Chrome 浏览器为最新版本

## 故障排除

### 无法启动浏览器
脚本会尝试 3 种不同的方式启动浏览器：
1. 使用 webdriver-manager 自动下载
2. 使用系统已安装的 ChromeDriver
3. 使用特殊选项启动

如果都失败，请手动安装 ChromeDriver：
```bash
brew install chromedriver
```

### SSL 错误
如果遇到 SSL 连接错误，脚本会自动切换到备选方法。

### 图片下载失败
- 检查网络连接
- 某些图片可能受到访问限制
- 脚本会跳过失败的图片，继续下载其他内容

## 依赖项

- Python 3.7+
- selenium >= 4.0.0
- webdriver-manager >= 4.0.0
- requests >= 2.28.0
- Chrome 浏览器

## 许可证

MIT License


