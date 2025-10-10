# 代理配置说明

## 概述

从本版本开始，Chrome 浏览器和 Webhook 的代理配置已经完全独立，你可以分别控制它们是否使用代理。

## 配置方式

在 `.env` 文件中添加以下配置：

```env
# ==================== Webhook 代理配置 ====================
# 是否为 Webhook 请求使用代理（默认：false，不使用）
USE_WEBHOOK_PROXY=false
# Webhook 代理地址
WEBHOOK_PROXY_URL=http://127.0.0.1:7890

# ==================== Chrome 代理配置 ====================
# 是否为 Chrome 浏览器使用代理（默认：false，不使用）
USE_CHROME_PROXY=false
# Chrome 代理地址
CHROME_PROXY_URL=http://127.0.0.1:7890
```

## 使用场景

### 场景 1：两者都不使用代理（默认）
```env
USE_WEBHOOK_PROXY=false
USE_CHROME_PROXY=false
```
适用于：在中国大陆以外的服务器上运行，可以直接访问 Twitter 和企业微信。

### 场景 2：只有 Chrome 使用代理
```env
USE_WEBHOOK_PROXY=false
USE_CHROME_PROXY=true
CHROME_PROXY_URL=http://127.0.0.1:7890
```
适用于：在中国大陆服务器上运行，需要通过代理访问 Twitter，但可以直接访问企业微信。

### 场景 3：只有 Webhook 使用代理
```env
USE_WEBHOOK_PROXY=true
WEBHOOK_PROXY_URL=http://127.0.0.1:7890
USE_CHROME_PROXY=false
```
适用于：服务器可以直接访问 Twitter，但需要通过代理访问企业微信（少见场景）。

### 场景 4：两者都使用代理
```env
USE_WEBHOOK_PROXY=true
WEBHOOK_PROXY_URL=http://127.0.0.1:7890
USE_CHROME_PROXY=true
CHROME_PROXY_URL=http://127.0.0.1:7890
```
适用于：在网络受限环境中运行，所有外部请求都需要通过代理。

### 场景 5：使用不同的代理地址
```env
USE_WEBHOOK_PROXY=true
WEBHOOK_PROXY_URL=http://proxy1.example.com:8080
USE_CHROME_PROXY=true
CHROME_PROXY_URL=http://proxy2.example.com:7890
```
适用于：有多个代理服务器，需要分别配置。

## 配置文件示例

完整的 `.env` 文件示例：

```env
# 企业微信 Webhook 配置
WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_WEBHOOK_KEY

# Webhook 代理配置
USE_WEBHOOK_PROXY=false
WEBHOOK_PROXY_URL=http://127.0.0.1:7890

# Chrome 代理配置
USE_CHROME_PROXY=false
CHROME_PROXY_URL=http://127.0.0.1:7890

# 推特列表监听配置
LIST_CHECK_INTERVAL=240
MAX_TWEETS_PER_CHECK=10
```

## 注意事项

1. **默认不使用代理**：如果环境变量未设置，默认两者都不使用代理
2. **开关控制**：`USE_WEBHOOK_PROXY` 和 `USE_CHROME_PROXY` 接受的值：
   - `true` / `True` / `TRUE` - 启用代理
   - `false` / `False` / `FALSE` - 禁用代理（默认）
3. **代理地址格式**：支持 `http://` 和 `socks5://` 协议
   - HTTP 代理：`http://127.0.0.1:7890`
   - SOCKS5 代理：`socks5://127.0.0.1:1080`
4. **验证配置**：启动程序时，会在日志中显示是否使用代理

## 迁移指南

### 从旧版本升级

旧版本的配置方式：
```env
USE_PROXY=true
PROXY_URL=http://127.0.0.1:7890
CHROME_PROXY=http://127.0.0.1:7890
```

新版本的等效配置：
```env
USE_WEBHOOK_PROXY=true
WEBHOOK_PROXY_URL=http://127.0.0.1:7890
USE_CHROME_PROXY=true
CHROME_PROXY_URL=http://127.0.0.1:7890
```

**重要**：旧的环境变量 `USE_PROXY`、`PROXY_URL`、`CHROME_PROXY` 已被弃用，请更新为新的变量名。

