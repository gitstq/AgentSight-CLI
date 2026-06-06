<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="Version" />
  <img src="https://img.shields.io/badge/python-3.9+-green?style=flat-square" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-orange?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/tests-53%20passed-success?style=flat-square" alt="Tests" />
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform" />
</p>

<h1 align="center">🦞 AgentSight-CLI</h1>

<p align="center">
  <strong>Lightweight Terminal AI Agent Multi-Source Web Data Intelligent Collection & Structured Extraction Engine</strong>
</p>

<p align="center">
  Give your AI agent eyes to see the entire internet — one CLI, zero API fees.
</p>

<p align="center">
  <a href="#-project-introduction">English</a> •
  <a href="#-项目介绍">简体中文</a> •
  <a href="#-專案介紹">繁體中文</a>
</p>

---

<a id="-project-introduction"></a>

## 🎉 Project Introduction

**AgentSight-CLI** is a lightweight, zero-dependency terminal CLI tool that gives AI agents the ability to read and collect data from the internet. It supports **6 major platforms** (GitHub Trending, Reddit, Hacker News, Weibo Hot Search, Zhihu Hot List, Bilibili Popular), automatically extracts structured data, and outputs in multiple formats directly usable by RAG pipelines and LLM contexts.

### 💡 Why AgentSight-CLI?

In the era of AI agents, one of the biggest bottlenecks is **data access**. AI agents are powerful, but they're often trapped in a sandbox with no ability to read real-time internet data. AgentSight-CLI bridges this gap by providing a simple CLI that:

- 🔍 **Collects** trending content from multiple platforms in real-time
- 🧠 **Extracts** structured data (title, content, author, date, links, engagement metrics)
- 📦 **Outputs** in formats directly usable by RAG pipelines (JSON, Markdown, CSV, JSONL)
- 💰 **Costs nothing** — zero API fees, pure local scraping
- ⚡ **Runs anywhere** — cross-platform, minimal dependencies

### ✨ Differentiation Highlights

| Feature | AgentSight-CLI | Typical Alternatives |
|---------|----------------|---------------------|
| Chinese Platform Support | ✅ Weibo, Zhihu, Bilibili | ❌ Usually missing |
| API Cost | Free (local scraping) | $10-100+/month |
| RAG Output | Native JSONL format | Manual conversion needed |
| Dependencies | Minimal (4 packages) | Heavy frameworks |
| Offline Cache | Built-in TTL cache | Not available |

---

## ✨ Core Features

- 🌐 **Multi-Source Data Collection** — GitHub Trending, Reddit, Hacker News, Weibo Hot Search, Zhihu Hot List, Bilibili Popular
- 🧠 **Intelligent Structured Extraction** — Automatically extracts title, content, author, date, link, engagement metrics
- 📊 **Multiple Output Formats** — JSON, Markdown, CSV, RAG-optimized JSONL
- 🔄 **Built-in Cache** — Local file caching with TTL expiration to avoid duplicate requests
- ⏱️ **Rate Limiting** — Built-in request interval control to prevent IP bans
- 🔁 **Auto Retry** — Exponential backoff retry on HTTP failures
- 🎨 **Rich Terminal UI** — Beautiful colored tables and panels via Rich library
- 🔍 **Keyword Search** — Search across multiple sources simultaneously
- 🌍 **Cross-Platform** — Works on Windows, macOS, and Linux
- 📡 **URL Content Extraction** — Extract structured content from any URL
- 🤖 **RAG-Ready** — Output format directly compatible with RAG pipelines and LLM contexts

---

## 🚀 Quick Start

### 📋 Prerequisites

- **Python 3.9+** installed
- **pip** package manager

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/AgentSight-CLI.git
cd AgentSight-CLI

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### 🏃 Usage

```bash
# List all available data sources
agentsight sources

# Fetch GitHub Trending repos (default: top 10)
agentsight list github

# Fetch Reddit hot posts with JSON output
agentsight list reddit --format json

# Fetch Hacker News top stories with limit
agentsight list hackernews --limit 5

# Fetch Weibo hot search
agentsight list weibo

# Fetch Zhihu hot list
agentsight list zhihu

# Fetch Bilibili popular videos
agentsight list bilibili

# Search keyword across all sources
agentsight search "artificial intelligence"

# Search specific sources
agentsight search "Python" --sources github,reddit

# Extract content from a URL
agentsight fetch https://example.com/article

# Use proxy
agentsight list github --proxy http://127.0.0.1:7890

# Disable cache
agentsight list github --no-cache

# Disable SSL verification
agentsight list github --no-ssl-verify
```

---

## 📖 Detailed Usage Guide

### 🔧 CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `agentsight sources` | List all available data sources | `agentsight sources` |
| `agentsight list <source>` | Fetch trending content from a source | `agentsight list github --limit 5` |
| `agentsight search <keyword>` | Search keyword across sources | `agentsight search "AI"` |
| `agentsight fetch <url>` | Extract structured content from URL | `agentsight fetch https://...` |

### 📊 Output Formats

```bash
# JSON format (default)
agentsight list github --format json

# Markdown format (beautiful tables)
agentsight list github --format markdown

# CSV format (for spreadsheets)
agentsight list github --format csv

# RAG format (JSONL for embeddings)
agentsight list github --format rag
```

### 🎯 Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--format, -f` | Output format (json/markdown/csv/rag) | table |
| `--limit, -n` | Number of results | 10 |
| `--proxy` | HTTP proxy URL | None |
| `--no-cache` | Disable caching | False |
| `--no-ssl-verify` | Disable SSL verification | False |
| `--timeout` | Request timeout in seconds | 30 |
| `--version` | Show version | - |
| `--help` | Show help | - |

### 🧩 RAG Integration Example

```python
import json

# Run CLI and capture RAG output
import subprocess
result = subprocess.run(
    ["agentsight", "list", "github", "--format", "rag", "--limit", "20"],
    capture_output=True, text=True
)

# Parse JSONL for RAG pipeline
for line in result.stdout.strip().split("\n"):
    chunk = json.loads(line)
    # chunk["text"] → for embedding
    # chunk["metadata"] → for filtering
    print(f"Text: {chunk['text'][:100]}...")
    print(f"Source: {chunk['metadata']['source']}")
```

---

## 💡 Design Philosophy & Roadmap

### 🎯 Design Philosophy

1. **Simplicity First** — One command to get data, no complex configuration needed
2. **Agent-Centric** — Designed specifically for AI agent data access, not human browsing
3. **Cost Zero** — No API keys, no subscriptions, pure local scraping
4. **RAG-Native** — Output formats designed for direct RAG pipeline integration
5. **Extensible** — Plugin-based architecture makes adding new sources trivial

### 🗺️ Roadmap

- [ ] **v1.1** — Add Twitter/X, YouTube Trending sources
- [ ] **v1.2** — Add Docker support for containerized deployment
- [ ] **v1.3** — Add MCP Server mode for AI agent integration
- [ ] **v2.0** — Add full-text search and content summarization
- [ ] **v2.1** — Add WebSocket real-time streaming mode
- [ ] **v2.2** — Add custom source plugin system

---

## 📦 Installation & Deployment

### pip Install (Recommended)

```bash
pip install git+https://github.com/gitstq/AgentSight-CLI.git
```

### From Source

```bash
git clone https://github.com/gitstq/AgentSight-CLI.git
cd AgentSight-CLI
pip install -r requirements.txt
pip install -e .
```

### Docker (Coming Soon)

```bash
docker run -it ghcr.io/gitstq/agentsight-cli agentsight sources
```

### Requirements

| Dependency | Version | Purpose |
|-----------|---------|---------|
| Python | 3.9+ | Runtime |
| requests | 2.28+ | HTTP client |
| beautifulsoup4 | 4.12+ | HTML parsing |
| rich | 13.0+ | Terminal UI |
| click | 8.1+ | CLI framework |
| lxml | 4.9+ | Fast XML/HTML parser |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feat/amazing-feature`)
3. ✅ Write tests for your changes
4. 📝 Commit with conventional commits (`git commit -m 'feat: add amazing feature'`)
5. 🚀 Push to the branch (`git push origin feat/amazing-feature`)
6. 📋 Create a Pull Request

### Commit Convention

```
feat: new feature
fix: bug fix
docs: documentation update
refactor: code refactoring
test: test additions/updates
chore: build/tooling changes
```

### Issue Guidelines

- 🐛 **Bug Report** — Include OS, Python version, and reproduction steps
- 💡 **Feature Request** — Describe the use case and expected behavior
- ❓ **Question** — Use GitHub Discussions

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with 🦞 by <a href="https://github.com/gitstq">LobsterBot</a>
</p>

---

<a id="-项目介绍"></a>

## 🎉 项目介绍

**AgentSight-CLI** 是一款轻量级、零配置的终端CLI工具，赋予AI Agent从互联网读取和采集数据的能力。支持 **6大主流平台**（GitHub Trending、Reddit、Hacker News、微博热搜、知乎热榜、B站热门），自动提取结构化数据，并以多种格式输出，可直接用于RAG管道和LLM上下文。

### 💡 为什么需要 AgentSight-CLI？

在AI Agent时代，最大的瓶颈之一是**数据获取**。AI Agent能力强大，但往往被困在沙箱中，无法读取实时互联网数据。AgentSight-CLI 通过一个简单的CLI弥合了这一差距：

- 🔍 **采集** 多平台实时热门内容
- 🧠 **提取** 结构化数据（标题、内容、作者、日期、链接、互动数据）
- 📦 **输出** RAG管道可直接使用的格式（JSON、Markdown、CSV、JSONL）
- 💰 **零成本** — 无需API费用，纯本地爬取
- ⚡ **随处运行** — 跨平台，极简依赖

### ✨ 差异化亮点

| 特性 | AgentSight-CLI | 常见替代方案 |
|------|---------------|-------------|
| 中文平台支持 | ✅ 微博、知乎、B站 | ❌ 通常缺失 |
| API费用 | 免费（本地爬取） | $10-100+/月 |
| RAG输出 | 原生JSONL格式 | 需手动转换 |
| 依赖量 | 极简（4个包） | 重量级框架 |
| 离线缓存 | 内置TTL缓存 | 通常不支持 |

---

## ✨ 核心特性

- 🌐 **多源数据采集** — GitHub Trending、Reddit、Hacker News、微博热搜、知乎热榜、B站热门
- 🧠 **智能结构化提取** — 自动提取标题、内容、作者、日期、链接、互动指标
- 📊 **多格式输出** — JSON、Markdown、CSV、RAG优化JSONL
- 🔄 **内置缓存** — 本地文件缓存，支持TTL过期，避免重复请求
- ⏱️ **速率限制** — 内置请求间隔控制，防止IP封禁
- 🔁 **自动重试** — HTTP失败时指数退避重试
- 🎨 **Rich终端UI** — 通过Rich库提供美观的彩色表格和面板
- 🔍 **关键词搜索** — 跨多源同时搜索
- 🌍 **跨平台** — 支持Windows、macOS和Linux
- 📡 **URL内容提取** — 从任意URL提取结构化内容
- 🤖 **RAG就绪** — 输出格式直接兼容RAG管道和LLM上下文

---

## 🚀 快速开始

### 📋 环境要求

- **Python 3.9+**
- **pip** 包管理器

### 📦 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/AgentSight-CLI.git
cd AgentSight-CLI

# 安装依赖
pip install -r requirements.txt

# 或以开发模式安装
pip install -e .
```

### 🏃 使用方法

```bash
# 列出所有可用数据源
agentsight sources

# 获取GitHub Trending仓库（默认前10）
agentsight list github

# 获取Reddit热帖，JSON格式输出
agentsight list reddit --format json

# 获取Hacker News头条，限制数量
agentsight list hackernews --limit 5

# 获取微博热搜
agentsight list weibo

# 获取知乎热榜
agentsight list zhihu

# 获取B站热门视频
agentsight list bilibili

# 搜索关键词（跨所有数据源）
agentsight search "人工智能"

# 搜索指定数据源
agentsight search "Python" --sources github,reddit

# 提取URL内容
agentsight fetch https://example.com/article

# 使用代理
agentsight list github --proxy http://127.0.0.1:7890

# 禁用缓存
agentsight list github --no-cache

# 禁用SSL验证
agentsight list github --no-ssl-verify
```

---

## 📖 详细使用指南

### 🔧 CLI命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `agentsight sources` | 列出所有可用数据源 | `agentsight sources` |
| `agentsight list <source>` | 获取指定数据源的热门内容 | `agentsight list github --limit 5` |
| `agentsight search <keyword>` | 跨数据源搜索关键词 | `agentsight search "AI"` |
| `agentsight fetch <url>` | 从URL提取结构化内容 | `agentsight fetch https://...` |

### 📊 输出格式

```bash
# JSON格式（默认）
agentsight list github --format json

# Markdown格式（美观表格）
agentsight list github --format markdown

# CSV格式（电子表格）
agentsight list github --format csv

# RAG格式（JSONL，用于向量化）
agentsight list github --format rag
```

### 🎯 全局选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--format, -f` | 输出格式（json/markdown/csv/rag） | table |
| `--limit, -n` | 结果数量 | 10 |
| `--proxy` | HTTP代理URL | 无 |
| `--no-cache` | 禁用缓存 | False |
| `--no-ssl-verify` | 禁用SSL验证 | False |
| `--timeout` | 请求超时时间（秒） | 30 |
| `--version` | 显示版本 | - |
| `--help` | 显示帮助 | - |

### 🧩 RAG集成示例

```python
import json
import subprocess

# 运行CLI并捕获RAG输出
result = subprocess.run(
    ["agentsight", "list", "github", "--format", "rag", "--limit", "20"],
    capture_output=True, text=True
)

# 解析JSONL用于RAG管道
for line in result.stdout.strip().split("\n"):
    chunk = json.loads(line)
    # chunk["text"] → 用于向量化
    # chunk["metadata"] → 用于过滤
    print(f"文本: {chunk['text'][:100]}...")
    print(f"来源: {chunk['metadata']['source']}")
```

---

## 💡 设计思路与迭代规划

### 🎯 设计理念

1. **极简优先** — 一条命令获取数据，无需复杂配置
2. **Agent导向** — 专为AI Agent数据访问设计，非人类浏览
3. **零成本** — 无需API密钥，无订阅费用，纯本地爬取
4. **RAG原生** — 输出格式专为RAG管道直接集成设计
5. **可扩展** — 插件式架构，新增数据源极其简单

### 🗺️ 迭代规划

- [ ] **v1.1** — 新增Twitter/X、YouTube Trending数据源
- [ ] **v1.2** — 新增Docker容器化部署支持
- [ ] **v1.3** — 新增MCP Server模式，支持AI Agent直接集成
- [ ] **v2.0** — 新增全文搜索与内容摘要功能
- [ ] **v2.1** — 新增WebSocket实时流式推送模式
- [ ] **v2.2** — 新增自定义数据源插件系统

---

## 📦 安装与部署

### pip安装（推荐）

```bash
pip install git+https://github.com/gitstq/AgentSight-CLI.git
```

### 从源码安装

```bash
git clone https://github.com/gitstq/AgentSight-CLI.git
cd AgentSight-CLI
pip install -r requirements.txt
pip install -e .
```

### Docker（即将推出）

```bash
docker run -it ghcr.io/gitstq/agentsight-cli agentsight sources
```

### 依赖要求

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.9+ | 运行时 |
| requests | 2.28+ | HTTP客户端 |
| beautifulsoup4 | 4.12+ | HTML解析 |
| rich | 13.0+ | 终端UI |
| click | 8.1+ | CLI框架 |
| lxml | 4.9+ | 高速XML/HTML解析器 |

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. 🍴 Fork本仓库
2. 🌿 创建特性分支（`git checkout -b feat/amazing-feature`）
3. ✅ 为你的修改编写测试
4. 📝 使用Angular提交规范（`git commit -m 'feat: 新增特性'`）
5. 🚀 推送到分支（`git push origin feat/amazing-feature`）
6. 📋 创建Pull Request

### 提交规范

```
feat: 新增功能
fix: 修复问题
docs: 文档更新
refactor: 代码重构
test: 测试新增/更新
chore: 构建/工具变更
```

### Issue反馈规则

- 🐛 **Bug报告** — 包含操作系统、Python版本和复现步骤
- 💡 **功能建议** — 描述使用场景和期望行为
- ❓ **使用问题** — 使用GitHub Discussions

---

## 📄 开源协议

本项目基于 **MIT协议** 开源 — 详见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  🦞 由 <a href="https://github.com/gitstq">LobsterBot</a> 用心打造
</p>

---

<a id="-專案介紹"></a>

## 🎉 專案介紹

**AgentSight-CLI** 是一款輕量級、零配置的終端CLI工具，賦予AI Agent從網際網路讀取和採集資料的能力。支援 **6大主流平台**（GitHub Trending、Reddit、Hacker News、微博熱搜、知乎熱榜、B站熱門），自動提取結構化資料，並以多種格式輸出，可直接用於RAG管道和LLM上下文。

### 💡 為什麼需要 AgentSight-CLI？

在AI Agent時代，最大的瓶頸之一是**資料獲取**。AI Agent能力強大，但往往被困在沙箱中，無法讀取即時網際網路資料。AgentSight-CLI 透過一個簡單的CLI彌合了這一差距：

- 🔍 **採集** 多平台即時熱門內容
- 🧠 **提取** 結構化資料（標題、內容、作者、日期、連結、互動資料）
- 📦 **輸出** RAG管道可直接使用的格式（JSON、Markdown、CSV、JSONL）
- 💰 **零成本** — 無需API費用，純本地爬取
- ⚡ **隨處運行** — 跨平台，極簡依賴

### ✨ 差異化亮點

| 特性 | AgentSight-CLI | 常見替代方案 |
|------|---------------|-------------|
| 中文平台支援 | ✅ 微博、知乎、B站 | ❌ 通常缺失 |
| API費用 | 免費（本地爬取） | $10-100+/月 |
| RAG輸出 | 原生JSONL格式 | 需手動轉換 |
| 依賴量 | 極簡（4個套件） | 重量級框架 |
| 離線快取 | 內建TTL快取 | 通常不支援 |

---

## ✨ 核心特性

- 🌐 **多源資料採集** — GitHub Trending、Reddit、Hacker News、微博熱搜、知乎熱榜、B站熱門
- 🧠 **智慧結構化提取** — 自動提取標題、內容、作者、日期、連結、互動指標
- 📊 **多格式輸出** — JSON、Markdown、CSV、RAG最佳化JSONL
- 🔄 **內建快取** — 本地檔案快取，支援TTL過期，避免重複請求
- ⏱️ **速率限制** — 內建請求間隔控制，防止IP封禁
- 🔁 **自動重試** — HTTP失敗時指數退避重試
- 🎨 **Rich終端UI** — 透過Rich庫提供美觀的彩色表格和面板
- 🔍 **關鍵字搜尋** — 跨多源同時搜尋
- 🌍 **跨平台** — 支援Windows、macOS和Linux
- 📡 **URL內容提取** — 從任意URL提取結構化內容
- 🤖 **RAG就緒** — 輸出格式直接相容RAG管道和LLM上下文

---

## 🚀 快速開始

### 📋 環境要求

- **Python 3.9+**
- **pip** 套件管理器

### 📦 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/AgentSight-CLI.git
cd AgentSight-CLI

# 安裝依賴
pip install -r requirements.txt

# 或以開發模式安裝
pip install -e .
```

### 🏃 使用方法

```bash
# 列出所有可用資料源
agentsight sources

# 取得GitHub Trending倉庫（預設前10）
agentsight list github

# 取得Reddit熱帖，JSON格式輸出
agentsight list reddit --format json

# 取得Hacker News頭條，限制數量
agentsight list hackernews --limit 5

# 取得微博熱搜
agentsight list weibo

# 取得知乎熱榜
agentsight list zhihu

# 取得B站熱門影片
agentsight list bilibili

# 搜尋關鍵字（跨所有資料源）
agentsight search "人工智慧"

# 搜尋指定資料源
agentsight search "Python" --sources github,reddit

# 提取URL內容
agentsight fetch https://example.com/article

# 使用代理
agentsight list github --proxy http://127.0.0.1:7890

# 停用快取
agentsight list github --no-cache

# 停用SSL驗證
agentsight list github --no-ssl-verify
```

---

## 📖 詳細使用指南

### 🔧 CLI命令

| 命令 | 說明 | 範例 |
|------|------|------|
| `agentsight sources` | 列出所有可用資料源 | `agentsight sources` |
| `agentsight list <source>` | 取得指定資料源的熱門內容 | `agentsight list github --limit 5` |
| `agentsight search <keyword>` | 跨資料源搜尋關鍵字 | `agentsight search "AI"` |
| `agentsight fetch <url>` | 從URL提取結構化內容 | `agentsight fetch https://...` |

### 📊 輸出格式

```bash
# JSON格式（預設）
agentsight list github --format json

# Markdown格式（美觀表格）
agentsight list github --format markdown

# CSV格式（電子表格）
agentsight list github --format csv

# RAG格式（JSONL，用於向量化）
agentsight list github --format rag
```

### 🎯 全域選項

| 選項 | 說明 | 預設值 |
|------|------|--------|
| `--format, -f` | 輸出格式（json/markdown/csv/rag） | table |
| `--limit, -n` | 結果數量 | 10 |
| `--proxy` | HTTP代理URL | 無 |
| `--no-cache` | 停用快取 | False |
| `--no-ssl-verify` | 停用SSL驗證 | False |
| `--timeout` | 請求逾時時間（秒） | 30 |
| `--version` | 顯示版本 | - |
| `--help` | 顯示說明 | - |

### 🧩 RAG整合範例

```python
import json
import subprocess

# 執行CLI並擷取RAG輸出
result = subprocess.run(
    ["agentsight", "list", "github", "--format", "rag", "--limit", "20"],
    capture_output=True, text=True
)

# 解析JSONL用於RAG管道
for line in result.stdout.strip().split("\n"):
    chunk = json.loads(line)
    # chunk["text"] → 用於向量化
    # chunk["metadata"] → 用於過濾
    print(f"文本: {chunk['text'][:100]}...")
    print(f"來源: {chunk['metadata']['source']}")
```

---

## 💡 設計理念與迭代規劃

### 🎯 設計理念

1. **極簡優先** — 一條命令取得資料，無需複雜配置
2. **Agent導向** — 專為AI Agent資料存取設計，非人類瀏覽
3. **零成本** — 無需API金鑰，無訂閱費用，純本地爬取
4. **RAG原生** — 輸出格式專為RAG管道直接整合設計
5. **可擴展** — 外掛式架構，新增資料源極其簡單

### 🗺️ 迭代規劃

- [ ] **v1.1** — 新增Twitter/X、YouTube Trending資料源
- [ ] **v1.2** — 新增Docker容器化部署支援
- [ ] **v1.3** — 新增MCP Server模式，支援AI Agent直接整合
- [ ] **v2.0** — 新增全文搜尋與內容摘要功能
- [ ] **v2.1** — 新增WebSocket即時串流推送模式
- [ ] **v2.2** — 新增自訂資料源外掛系統

---

## 📦 安裝與部署

### pip安裝（推薦）

```bash
pip install git+https://github.com/gitstq/AgentSight-CLI.git
```

### 從原始碼安裝

```bash
git clone https://github.com/gitstq/AgentSight-CLI.git
cd AgentSight-CLI
pip install -r requirements.txt
pip install -e .
```

### Docker（即將推出）

```bash
docker run -it ghcr.io/gitstq/agentsight-cli agentsight sources
```

### 依賴要求

| 依賴 | 版本 | 用途 |
|------|------|------|
| Python | 3.9+ | 執行時期 |
| requests | 2.28+ | HTTP客戶端 |
| beautifulsoup4 | 4.12+ | HTML解析 |
| rich | 13.0+ | 終端UI |
| click | 8.1+ | CLI框架 |
| lxml | 4.9+ | 高速XML/HTML解析器 |

---

## 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. 🍴 Fork本倉庫
2. 🌿 建立特性分支（`git checkout -b feat/amazing-feature`）
3. ✅ 為你的修改撰寫測試
4. 📝 使用Angular提交規範（`git commit -m 'feat: 新增特性'`）
5. 🚀 推送到分支（`git push origin feat/amazing-feature`）
6. 📋 建立Pull Request

### 提交規範

```
feat: 新增功能
fix: 修復問題
docs: 文件更新
refactor: 程式碼重構
test: 測試新增/更新
chore: 建構/工具變更
```

### Issue回饋規則

- 🐛 **Bug報告** — 包含作業系統、Python版本和重現步驟
- 💡 **功能建議** — 描述使用場景和期望行為
- ❓ **使用問題** — 使用GitHub Discussions

---

## 📄 開源協議

本專案基於 **MIT協議** 開源 — 詳見 [LICENSE](LICENSE) 檔案。

---

<p align="center">
  🦞 由 <a href="https://github.com/gitstq">LobsterBot</a> 用心打造
</p>
