# 📖 完整配置与部署指南

本文档包含 A股智能分析系统的完整配置说明，适合需要高级功能或特殊部署方式的用户。

> 💡 快速上手请参考 [README.md](../README.md)，本文档为进阶配置。

## 📑 目录

- [GitHub Actions 详细配置](#github-actions-详细配置)
- [环境变量完整列表](#环境变量完整列表)
- [Docker 部署](#docker-部署)
- [本地运行详细配置](#本地运行详细配置)
- [定时任务配置](#定时任务配置)
- [通知渠道详细配置](#通知渠道详细配置)
- [数据源配置](#数据源配置)
- [高级功能](#高级功能)
- [本地 WebUI 管理界面](#本地-webui-管理界面)

---

## GitHub Actions 详细配置

### 1. Fork 本仓库

点击右上角 `Fork` 按钮

### 2. 配置 Secrets

进入你 Fork 的仓库 → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

<div align="center">
  <img src="../sources/secret_config.png" alt="GitHub Secrets 配置示意图" width="600">
</div>

#### AI 模型配置（二选一）

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) 获取免费 Key | ✅* |
| `OPENAI_API_KEY` | OpenAI 兼容 API Key（支持 DeepSeek、通义千问等） | 可选 |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 地址（如 `https://api.deepseek.com/v1`） | 可选 |
| `OPENAI_MODEL` | 模型名称（如 `deepseek-chat`） | 可选 |

> *注：`GEMINI_API_KEY` 和 `OPENAI_API_KEY` 至少配置一个

#### 通知渠道配置（可同时配置多个，全部推送）

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `WECHAT_WEBHOOK_URL` | 企业微信 Webhook URL | 可选 |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL | 可选 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token（@BotFather 获取） | 可选 |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | 可选 |
| `EMAIL_SENDER` | 发件人邮箱（如 `xxx@qq.com`） | 可选 |
| `EMAIL_PASSWORD` | 邮箱授权码（非登录密码） | 可选 |
| `EMAIL_RECEIVERS` | 收件人邮箱（多个用逗号分隔，留空则发给自己） | 可选 |
| `CUSTOM_WEBHOOK_URLS` | 自定义 Webhook（支持钉钉等，多个用逗号分隔） | 可选 |
| `CUSTOM_WEBHOOK_BEARER_TOKEN` | 自定义 Webhook 的 Bearer Token（用于需要认证的 Webhook） | 可选 |
| `SINGLE_STOCK_NOTIFY` | 单股推送模式：设为 `true` 则每分析完一只股票立即推送 | 可选 |

> *注：至少配置一个渠道，配置多个则同时推送

#### 其他配置

| Secret 名称 | 说明 | 必填 |
|------------|------|:----:|
| `STOCK_LIST` | 自选股代码，如 `600519,300750,002594` | ✅ |
| `TAVILY_API_KEYS` | [Tavily](https://tavily.com/) 搜索 API（新闻搜索） | 推荐 |
| `BOCHA_API_KEYS` | [博查搜索](https://open.bocha.cn/) Web Search API（中文搜索优化，支持AI摘要，多个key用逗号分隔） | 可选 |
| `SERPAPI_API_KEYS` | [SerpAPI](https://serpapi.com/) 备用搜索 | 可选 |
| `TUSHARE_TOKEN` | [Tushare Pro](https://tushare.pro/) Token | 可选 |

#### ✅ 最小配置示例

如果你想快速开始，最少需要配置以下项：

1. **AI 模型**：`GEMINI_API_KEY`（推荐）或 `OPENAI_API_KEY`
2. **通知渠道**：至少配置一个，如 `WECHAT_WEBHOOK_URL` 或 `EMAIL_SENDER` + `EMAIL_PASSWORD`
3. **股票列表**：`STOCK_LIST`（必填）
4. **搜索 API**：`TAVILY_API_KEYS`（强烈推荐，用于新闻搜索）

> 💡 配置完以上 4 项即可开始使用！

### 3. 启用 Actions

1. 进入你 Fork 的仓库
2. 点击顶部的 `Actions` 标签
3. 如果看到提示，点击 `I understand my workflows, go ahead and enable them`

### 4. 手动测试

1. 进入 `Actions` 标签
2. 左侧选择 `每日股票分析` workflow
3. 点击右侧的 `Run workflow` 按钮
4. 选择运行模式
5. 点击绿色的 `Run workflow` 确认

### 5. 完成！

默认每个工作日 **18:00（北京时间）** 自动执行。

---

## 环境变量完整列表

### AI 模型配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|:----:|
| `GEMINI_API_KEY` | Google Gemini API Key | - | ✅* |
| `GEMINI_MODEL` | 主模型名称 | `gemini-3-flash-preview` | 否 |
| `GEMINI_MODEL_FALLBACK` | 备选模型 | `gemini-2.5-flash` | 否 |
| `OPENAI_API_KEY` | OpenAI 兼容 API Key | - | 可选 |
| `OPENAI_BASE_URL` | OpenAI 兼容 API 地址 | - | 可选 |
| `OPENAI_MODEL` | OpenAI 模型名称 | `gpt-4o` | 可选 |

> *注：`GEMINI_API_KEY` 和 `OPENAI_API_KEY` 至少配置一个

### 通知渠道配置

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `WECHAT_WEBHOOK_URL` | 企业微信机器人 Webhook URL | 可选 |
| `FEISHU_WEBHOOK_URL` | 飞书机器人 Webhook URL | 可选 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 可选 |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID | 可选 |
| `EMAIL_SENDER` | 发件人邮箱 | 可选 |
| `EMAIL_PASSWORD` | 邮箱授权码（非登录密码） | 可选 |
| `EMAIL_RECEIVERS` | 收件人邮箱（逗号分隔，留空发给自己） | 可选 |
| `CUSTOM_WEBHOOK_URLS` | 自定义 Webhook（逗号分隔） | 可选 |
| `CUSTOM_WEBHOOK_BEARER_TOKEN` | 自定义 Webhook Bearer Token | 可选 |
| `PUSHOVER_USER_KEY` | Pushover 用户 Key | 可选 |
| `PUSHOVER_API_TOKEN` | Pushover API Token | 可选 |

#### 飞书云文档配置（可选，解决消息截断问题）

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `FEISHU_APP_ID` | 飞书应用 ID | 可选 |
| `FEISHU_APP_SECRET` | 飞书应用 Secret | 可选 |
| `FEISHU_FOLDER_TOKEN` | 飞书云盘文件夹 Token | 可选 |

> 飞书云文档配置步骤：
> 1. 在 [飞书开发者后台](https://open.feishu.cn/app) 创建应用
> 2. 配置 GitHub Secrets
> 3. 创建群组并添加应用机器人
> 4. 在云盘文件夹中添加群组为协作者（可管理权限）

### 搜索服务配置

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `TAVILY_API_KEYS` | Tavily 搜索 API Key（推荐） | 推荐 |
| `BOCHA_API_KEYS` | 博查搜索 API Key（中文优化） | 可选 |
| `SERPAPI_API_KEYS` | SerpAPI 备用搜索 | 可选 |

### 数据源配置

| 变量名 | 说明 | 必填 |
|--------|------|:----:|
| `TUSHARE_TOKEN` | Tushare Pro Token | 可选 |

### 其他配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `STOCK_LIST` | 自选股代码（逗号分隔） | - |
| `MAX_WORKERS` | 并发线程数 | `3` |
| `MARKET_REVIEW_ENABLED` | 启用大盘复盘 | `true` |
| `SCHEDULE_ENABLED` | 启用定时任务 | `false` |
| `SCHEDULE_TIME` | 定时执行时间 | `18:00` |
| `LOG_DIR` | 日志目录 | `./logs` |

---

## Docker 部署

### 快速启动

```bash
# 1. 克隆仓库
git clone https://github.com/ZhuLinsen/daily_stock_analysis.git
cd daily_stock_analysis

# 2. 配置环境变量
cp .env.example .env
vim .env  # 填入 API Key 和配置

# 3. 启动容器
docker-compose up -d webui      # WebUI 模式（推荐）
docker-compose up -d analyzer   # 定时任务模式
docker-compose up -d            # 同时启动两种模式

# 4. 访问 WebUI
# http://localhost:8000

# 5. 查看日志
docker-compose logs -f webui
```

### 运行模式说明

| 命令 | 说明 | 端口 |
|------|------|------|
| `docker-compose up -d webui` | WebUI 模式，手动触发分析 | 8000 |
| `docker-compose up -d analyzer` | 定时任务模式，每日自动执行 | - |
| `docker-compose up -d` | 同时启动两种模式 | 8000 |

### Docker Compose 配置

`docker-compose.yml` 使用 YAML 锚点复用配置：

```yaml
version: '3.8'

x-common: &common
  build: .
  restart: unless-stopped
  env_file:
    - .env
  environment:
    - TZ=Asia/Shanghai
  volumes:
    - ./data:/app/data
    - ./logs:/app/logs
    - ./reports:/app/reports
    - ./.env:/app/.env

services:
  # 定时任务模式
  analyzer:
    <<: *common
    container_name: stock-analyzer

  # WebUI 模式
  webui:
    <<: *common
    container_name: stock-webui
    command: ["python", "main.py", "--webui-only"]
    ports:
      - "8000:8000"
```

### 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f webui

# 停止服务
docker-compose down

# 重建镜像（代码更新后）
docker-compose build --no-cache
docker-compose up -d webui
```

### 手动构建镜像

```bash
docker build -t stock-analysis .
docker run -d --env-file .env -p 8000:8000 -v ./data:/app/data stock-analysis python main.py --webui-only
```

---

## 本地运行详细配置

### 安装依赖

```bash
# Python 3.10+ 推荐
pip install -r requirements.txt

# 或使用 conda
conda create -n stock python=3.10
conda activate stock
pip install -r requirements.txt
```

### 命令行参数

```bash
python main.py                        # 完整分析（个股 + 大盘复盘）
python main.py --market-review        # 仅大盘复盘
python main.py --no-market-review     # 仅个股分析
python main.py --stocks 600519,300750 # 指定股票
python main.py --dry-run              # 仅获取数据，不 AI 分析
python main.py --no-notify            # 不发送推送
python main.py --schedule             # 定时任务模式
python main.py --debug                # 调试模式（详细日志）
python main.py --workers 5            # 指定并发数
```

---

## 定时任务配置

### GitHub Actions 定时

编辑 `.github/workflows/daily_analysis.yml`:

```yaml
schedule:
  # UTC 时间，北京时间 = UTC + 8
  - cron: '0 10 * * 1-5'   # 周一到周五 18:00（北京时间）
```

常用时间对照：

| 北京时间 | UTC cron 表达式 |
|---------|----------------|
| 09:30 | `'30 1 * * 1-5'` |
| 12:00 | `'0 4 * * 1-5'` |
| 15:00 | `'0 7 * * 1-5'` |
| 18:00 | `'0 10 * * 1-5'` |
| 21:00 | `'0 13 * * 1-5'` |

### 本地定时任务

```bash
# 启动定时模式（默认 18:00 执行）
python main.py --schedule

# 或使用 crontab
crontab -e
# 添加：0 18 * * 1-5 cd /path/to/project && python main.py
```

---

## 通知渠道详细配置

### 企业微信

1. 在企业微信群聊中添加"群机器人"
2. 复制 Webhook URL
3. 设置 `WECHAT_WEBHOOK_URL`

### 飞书

1. 在飞书群聊中添加"自定义机器人"
2. 复制 Webhook URL
3. 设置 `FEISHU_WEBHOOK_URL`

### Telegram

1. 与 @BotFather 对话创建 Bot
2. 获取 Bot Token
3. 获取 Chat ID（可通过 @userinfobot）
4. 设置 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`

### 邮件

1. 开启邮箱的 SMTP 服务
2. 获取授权码（非登录密码）
3. 设置 `EMAIL_SENDER`、`EMAIL_PASSWORD`、`EMAIL_RECEIVERS`

支持的邮箱：
- QQ 邮箱：smtp.qq.com:465
- 163 邮箱：smtp.163.com:465
- Gmail：smtp.gmail.com:587

### 自定义 Webhook

支持任意 POST JSON 的 Webhook，包括：
- 钉钉机器人
- Discord Webhook
- Slack Webhook
- Bark（iOS 推送）
- 自建服务

设置 `CUSTOM_WEBHOOK_URLS`，多个用逗号分隔。

### Pushover（iOS/Android 推送）

[Pushover](https://pushover.net/) 是一个跨平台的推送服务，支持 iOS 和 Android。

1. 注册 Pushover 账号并下载 App
2. 在 [Pushover Dashboard](https://pushover.net/) 获取 User Key
3. 创建 Application 获取 API Token
4. 配置环境变量：

```bash
PUSHOVER_USER_KEY=your_user_key
PUSHOVER_API_TOKEN=your_api_token
```

特点：
- 支持 iOS/Android 双平台
- 支持通知优先级和声音设置
- 免费额度足够个人使用（每月 10,000 条）
- 消息可保留 7 天

---

## 数据源配置

系统默认使用 AkShare（免费），也支持其他数据源：

### AkShare（默认）
- 免费，无需配置
- 数据来源：东方财富爬虫

### Tushare Pro
- 需要注册获取 Token
- 更稳定，数据更全
- 设置 `TUSHARE_TOKEN`

### Baostock
- 免费，无需配置
- 作为备用数据源

### YFinance
- 免费，无需配置
- 支持美股/港股数据

---

## 高级功能

### 港股支持

使用 `hk` 前缀指定港股代码：

```bash
STOCK_LIST=600519,hk00700,hk01810
```

### 多模型切换

配置多个模型，系统自动切换：

```bash
# Gemini（主力）
GEMINI_API_KEY=xxx
GEMINI_MODEL=gemini-3-flash-preview

# OpenAI 兼容（备选）
OPENAI_API_KEY=xxx
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
```

### 调试模式

```bash
python main.py --debug
```

日志文件位置：
- 常规日志：`logs/stock_analysis_YYYYMMDD.log`
- 调试日志：`logs/stock_analysis_debug_YYYYMMDD.log`

---

## 本地 WebUI 管理界面

WebUI 提供配置管理和快速分析功能，支持页面触发单只股票分析。

### 启动方式

| 命令 | 说明 |
|------|------|
| `python main.py --webui` | 启动 WebUI + 执行一次完整分析 |
| `python main.py --webui-only` | 仅启动 WebUI，手动触发分析 |

**永久启用**：在 `.env` 中设置：
```env
WEBUI_ENABLED=true
```

### 功能特性

- 📝 **配置管理** - 查看/修改 `.env` 里的自选股列表
- 🚀 **快速分析** - 页面输入股票代码，一键触发分析
- 📊 **实时进度** - 分析任务状态实时更新，支持多任务并行
- 🔗 **API 接口** - 支持程序化调用

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 配置管理页面 |
| `/health` | GET | 健康检查 |
| `/analysis?code=xxx` | GET | 触发单只股票异步分析 |
| `/tasks` | GET | 查询所有任务状态 |
| `/task?id=xxx` | GET | 查询单个任务状态 |

**调用示例**：
```bash
# 健康检查
curl http://127.0.0.1:8000/health

# 触发分析（A股）
curl "http://127.0.0.1:8000/analysis?code=600519"

# 触发分析（港股）
curl "http://127.0.0.1:8000/analysis?code=hk00700"

# 查询任务状态
curl "http://127.0.0.1:8000/task?id=<task_id>"
```

### 自定义配置

修改默认端口或允许局域网访问：

```env
WEBUI_HOST=0.0.0.0    # 默认 127.0.0.1
WEBUI_PORT=8888       # 默认 8000
```

### 支持的股票代码格式

| 类型 | 格式 | 示例 |
|------|------|------|
| A股 | 6位数字 | `600519`、`000001`、`300750` |
| 港股 | hk + 5位数字 | `hk00700`、`hk09988` |

### 注意事项

- 浏览器访问：`http://127.0.0.1:8000`（或您配置的端口）
- 分析完成后自动推送通知到配置的渠道
- 此功能在 GitHub Actions 环境中会自动禁用

---

## 常见问题

### Q: 推送消息被截断？
A: 企业微信/飞书有消息长度限制，系统已自动分段发送。如需完整内容，可配置飞书云文档功能。

### Q: 数据获取失败？
A: AkShare 使用爬虫机制，可能被临时限流。系统已配置重试机制，一般等待几分钟后重试即可。

### Q: 如何添加自选股？
A: 修改 `STOCK_LIST` 环境变量，多个代码用逗号分隔。

### Q: GitHub Actions 没有执行？
A: 检查是否启用了 Actions，以及 cron 表达式是否正确（注意是 UTC 时间）。

---

更多问题请 [提交 Issue](https://github.com/ZhuLinsen/daily_stock_analysis/issues)
