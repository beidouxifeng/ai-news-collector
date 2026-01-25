# 📰 AI资讯哨兵 (AI News Sentinel)

> 基于GitHub Actions的全网资讯热点自动捕捉与分析系统

[![GitHub Actions](https://github.com/caosheng03/ai-news-sentinel/actions/workflows/daily-news.yml/badge.svg)](https://github.com/caosheng03/ai-news-sentinel/actions/workflows/daily-news.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-327873?logo=github&logoColor=white)](https://caosheng03.github.io/ai-news-sentinel/)

## ✨ 特性

- 🚀 **全自动运行**：GitHub Actions定时触发，无需人工干预
- 🤖 **AI智能分析**：使用DeepSeek API进行内容分类、摘要生成和热度评分
- 📊 **美观报告**：自动生成精美的HTML报告，支持响应式设计
- 📚 **历史存档**：自动归档历史报告，方便回溯查看
- 💰 **零成本**：完全免费（GitHub Actions + GitHub Pages）
- 🌐 **多源聚合**：支持从多个RSS源抓取科技资讯

## 🚀 快速开始

### 1. 配置API密钥

在GitHub仓库中添加DeepSeek API密钥：

1. 进入仓库 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. Name: `DEEPSEEK_API_KEY`
4. Value: 您的DeepSeek API密钥
5. 点击 **Add secret**

### 2. 配置RSS源

编辑 `config/rss_sources.json` 文件，添加您想要的RSS源。

### 3. 启用GitHub Pages

1. 进入仓库 **Settings** → **Pages**
2. Source 选择 **Deploy from a branch**
3. Branch 选择 **gh-pages** 和 **/(root)**
4. 点击 **Save**

## 📊 使用流程

```
每天北京时间9点
    ↓
GitHub Actions自动触发
    ↓
抓取RSS源数据
    ↓
AI分析（分类/摘要/评分）
    ↓
生成HTML报告
    ↓
部署到GitHub Pages
    ↓
访问网页查看报告
```

## 🌐 访问报告

部署完成后，通过以下地址访问：

**最新报告**: `https://caosheng03.github.io/ai-news-sentinel/`

**历史存档**: `https://caosheng03.github.io/ai-news-sentinel/archive/`

## 💡 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DEEPSEEK_API_KEY=your_api_key_here

# 运行程序
python scripts/main.py
```

## 📮 联系方式

- **作者**: caosheng03
- **GitHub**: [caosheng03](https://github.com/caosheng03)
- **项目主页**: https://github.com/caosheng03/ai-news-sentinel

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！