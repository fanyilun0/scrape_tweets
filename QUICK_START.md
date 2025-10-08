# 快速开始指南

## 🚀 5分钟快速上手

### 步骤1: 安装依赖（1分钟）

```bash
pip install -r requirements.txt
```

如果安装速度慢，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### 步骤2: 检查代理（可选）

如果你使用代理工具（如Clash、V2Ray）：

1. 确保代理工具正在运行
2. 检查代理端口（通常是7890或10808）
3. 在浏览器中测试能否访问 https://x.com

**不使用代理？** 
编辑 `main.py`，将这行改为：
```python
PROXY = None
```

---

### 步骤3: 运行脚本（1分钟）

```bash
python main.py
```

你会看到类似这样的输出：

```
检测到 48 条推文链接。
已抓取的推文数: 0

正在启动浏览器...
正在启动 undetected_chromedriver...
  配置代理: http://127.0.0.1:7890
  使用持久化Profile: ./chrome_profile
✓ undetected_chromedriver 启动成功
```

---

### 步骤4: 首次登录（2分钟）

**仅首次运行需要：**

1. 脚本会自动打开Chrome浏览器
2. 如果未登录，会看到提示：
   ```
   ==================================================
   检测到未登录状态
   浏览器已打开登录页面，请在浏览器窗口中手动登录你的X账号。
   登录成功后，回到这里，按Enter键继续执行抓取...
   注意：登录信息将保存到本地，下次运行时无需重复登录
   ==================================================
   ```

3. 在浏览器中完成登录：
   - 输入用户名/邮箱
   - 输入密码
   - 完成两步验证（如有）

4. 登录成功后，回到终端按 **Enter** 键

5. 脚本开始自动抓取推文

---

### 步骤5: 查看结果（1分钟）

抓取完成后，会生成：

```
📊 数据摘要:
  - CSV文件: tweets_data_20251008_123456.csv
  - Markdown文档: tweets_data_20251008_123456.md
  - 图片目录: tweets_images_20251008_123456/
  - 推文总数: 48
  - 图片总数: 127
```

**输出文件：**
- 📄 `tweets_data_*.csv` - Excel可打开的表格
- 📝 `tweets_data_*.md` - 可读性更好的Markdown文档
- 🖼️ `tweets_images_*/` - 所有下载的图片

---

## ✨ 后续运行

第二次及以后运行脚本：

```bash
python main.py
```

会看到：
```
✓ 检测到已登录状态，无需重复登录
提示：如需切换账号，请删除 chrome_profile 目录后重新运行

开始抓取推文内容...
```

**无需再次登录！** 🎉

---

## 🎯 常见场景

### 场景1: 测试运行（抓取前3条）

编辑 `main.py`，在提取URL后添加：

```python
tweet_urls = re.findall(r'https://x\.com/\w+/status/\d+', original_text)
tweet_urls = tweet_urls[:3]  # 只抓取前3条
print(f"检测到 {len(tweet_urls)} 条推文链接。")
```

### 场景2: 切换账号

```bash
# 删除保存的登录信息
rm -rf chrome_profile/

# 重新运行，会要求重新登录
python main.py
```

### 场景3: 不使用代理

编辑 `main.py` 配置区域：

```python
PROXY = None  # 设置为None
```

### 场景4: 继续未完成的抓取

如果抓取中断，直接重新运行即可：

```bash
python main.py
```

脚本会自动跳过已抓取的推文。

---

## ❓ 遇到问题？

### 问题1: 代理连接失败

**错误信息**：
```
ERR_PROXY_CONNECTION_FAILED
```

**解决方案**：
1. 检查代理软件是否运行
2. 检查端口是否正确（7890 / 10808）
3. 或者设置 `PROXY = None` 不使用代理

---

### 问题2: "Could not log you in now"

**说明**：这就是本次优化要解决的问题！

**解决方案**：
- ✅ 已优化：使用 `undetected_chromedriver`
- ✅ 已优化：持久化登录状态
- ✅ 已优化：随机延时和行为模拟

**如果仍然遇到：**
1. 确保代理正常（或禁用代理）
2. 手动完成所有验证步骤
3. 不要在短时间内多次登录

---

### 问题3: Chrome版本不匹配

**错误信息**：
```
This version of ChromeDriver only supports Chrome version XX
```

**解决方案**：
`undetected_chromedriver` 会自动处理版本匹配，通常不会遇到此问题。

如果确实遇到，更新Chrome浏览器：
- macOS: 打开Chrome → 帮助 → 关于Google Chrome
- 会自动检查并更新

---

### 问题4: 推文加载超时

**错误信息**：
```
TimeoutException
```

**解决方案**：
1. 检查网络连接
2. 检查代理是否稳定
3. 可以在代码中增加等待时间：
   ```python
   wait = WebDriverWait(driver, 30)  # 从15秒改为30秒
   ```

---

## 📚 进阶配置

想要自定义更多设置？查看：

- **[CONFIG.md](./CONFIG.md)** - 详细配置说明
- **[USAGE_GUIDE.md](./USAGE_GUIDE.md)** - 完整使用指南
- **[OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)** - 优化技术详解

---

## 💡 小贴士

### 提高抓取成功率

1. ✅ **使用代理** - 避免IP被限制
2. ✅ **保持登录** - 不要删除 `chrome_profile`
3. ✅ **分批抓取** - 不要一次抓取太多
4. ✅ **耐心等待** - 随机延时是必要的

### 节省时间

1. **首次运行** - 先用几条测试
2. **大规模抓取** - 可以睡前开始运行
3. **中断继续** - 利用断点续传功能

### 数据管理

1. **定期清理** - 图片目录会很大
2. **备份重要数据** - CSV和Markdown文件
3. **Git管理** - `.gitignore` 已配置好

---

## ✅ 检查清单

开始抓取前，确认：

- [ ] Python 3.7+ 已安装
- [ ] 依赖已安装 `pip install -r requirements.txt`
- [ ] Chrome浏览器已安装
- [ ] 代理配置正确（或已禁用）
- [ ] 有稳定的网络连接
- [ ] 准备好Twitter/X账号和密码

---

## 🎉 开始使用

一切准备就绪！运行：

```bash
python main.py
```

享受自动化抓取的乐趣吧！ 🚀

---

## 📞 获取帮助

- 查看完整文档：[USAGE_GUIDE.md](./USAGE_GUIDE.md)
- 了解技术细节：[OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)
- 自定义配置：[CONFIG.md](./CONFIG.md)
- 原始需求：[todo.md](./todo.md)

