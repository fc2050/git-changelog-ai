# 🤖 Git Changelog AI

[![PyPI version](https://badge.fury.io/py/git-changelog-ai.svg)](https://pypi.org/project/git-changelog-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[English](README.md) | [中文](README_CN.md)

AI 驱动的版本更新日志生成器，智能分析 Git 提交记录，生成清晰、专业的版本更新说明。

## 🎯 为什么选择 Git Changelog AI？

市面上大多数 changelog 工具只是**重新整理 commit message**。**Git Changelog AI 不一样** —— 它分析实际的代码变更（`git diff`），真正理解代码做了什么，而不仅仅依赖开发者写的提交信息。

| | 传统工具 | Git Changelog AI |
|---|---|---|
| 输入 | 仅 commit message | Commit message + **代码 Diff** |
| 分析方式 | 文本格式化/分类 | **语义理解** |
| 输出 | 整理后的 commit 列表 | 基于实际变更的**智能总结** |

## ✨ 特性

- 🧠 **真正的 AI 分析** - 分析实际代码 diff，而非仅依赖 commit message
- 🔍 **智能分类** - 自动将变更分类（新功能、修复、重构等）
- 🤖 **智能总结** - AI 理解代码变更，生成用户友好的描述
- 📝 **Markdown 输出** - 生成格式规范、专业的更新日志
- 🚀 **零依赖** - 仅使用 Python 标准库（基础模式无需安装任何依赖）
- 🔌 **多 AI 支持** - 支持 Gemini、OpenAI、DeepSeek
- 📤 **企微集成** - 支持通过 webhook 推送到企业微信群聊

## 📦 安装

### 从 PyPI 安装（推荐）

```bash
pip install git-changelog-ai
```

### 从源码安装

```bash
git clone https://github.com/yourusername/git-changelog-ai.git
cd git-changelog-ai
pip install -e .
```

## 🚀 快速开始

### 1. 配置 API Key

```bash
# Gemini（默认）
export GOOGLE_API_KEY="你的-api-key"

# 或其他提供商
export OPENAI_API_KEY="你的-api-key"
export DEEPSEEK_API_KEY="你的-api-key"
```

### 2. 生成更新日志

```bash
# 列出可用的 tags
git-changelog-ai --list

# 比较最近 2 个 tags 并使用 AI 分析
git-changelog-ai --recent 2 --ai

# 比较指定的 tags
git-changelog-ai v1.0.0 v1.1.0 --ai

# 输出到文件
git-changelog-ai --recent 2 --ai --output CHANGELOG.md

# 推送到企业微信群
git-changelog-ai --recent 2 --ai --webhook
```

## 📖 使用说明

### 基本命令

```bash
# 列出所有 tags
git-changelog-ai --list

# 按日期筛选 tags
git-changelog-ai --list --date 2025-01

# 基础模式（关键词分类，不使用 AI）
git-changelog-ai --recent 2

# AI 模式（推荐）
git-changelog-ai --recent 2 --ai

# 使用指定的 AI 提供商
git-changelog-ai --recent 2 --ai --provider openai

# 调试模式（查看将发送给 AI 的数据）
git-changelog-ai --recent 2 --dry-run

# 详细输出（包含 commit hash）
git-changelog-ai --recent 2 --verbose

# 推送到企业微信群
git-changelog-ai --recent 2 --ai --webhook

# 使用自定义 webhook URL
git-changelog-ai --recent 2 --ai --webhook --webhook-url "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
```

### 命令选项

| 选项 | 说明 |
|------|------|
| `from_ref` | 起始版本（tag/commit hash/分支名） |
| `to_ref` | 目标版本（tag/commit hash/分支名） |
| `--list`, `-l` | 列出可用的 tags |
| `--date`, `-d` | 按日期筛选 tags |
| `--limit` | 限制显示的 tags 数量（默认：20） |
| `--recent`, `-r` | 比较最近 N 个 tags |
| `--ai` | 启用 AI 智能分析 |
| `--provider` | AI 提供商（gemini/openai/deepseek） |
| `--output`, `-o` | 输出文件路径 |
| `--verbose`, `-v` | 显示详细信息 |
| `--dry-run` | 调试模式，不调用 AI |
| `--webhook` | 推送更新日志到企业微信群 |
| `--webhook-url` | 自定义 webhook URL（覆盖环境变量） |
| `--version` | 显示版本号 |
| `--help`, `-h` | 显示帮助信息 |

## 🔧 配置

### 环境变量

| 变量名 | 提供商 | 说明 |
|--------|--------|------|
| `GOOGLE_API_KEY` | Gemini | Google AI API 密钥 |
| `OPENAI_API_KEY` | OpenAI | OpenAI API 密钥 |
| `DEEPSEEK_API_KEY` | DeepSeek | DeepSeek API 密钥 |
| `WECOM_WEBHOOK_URL` | 企业微信 | 群机器人 Webhook URL |

### 自动忽略的文件

生成更新日志时会自动忽略以下文件：

- `CHANGELOG.md`, `CHANGELOG*.md`
- `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`

### 自动忽略的提交者

以下提交者的 commit 会被自动忽略（如 CI 机器人）：

- `vfe_athena`

可在 `constants.py` 中修改 `IGNORE_AUTHORS` 自定义配置。

## 📋 输出示例

```markdown
# 更新日志

**v1.0.0 → v1.1.0**

📅 发布日期: 2025-01-15

## ✨ 新功能
- 支持多种 AI 提供商（Gemini、OpenAI、DeepSeek）
- 新增 --dry-run 调试模式

## 🐛 问题修复
- 修复了大文件 diff 导致的内存问题
- 修复了日期解析在某些格式下的错误

## ⚡ 性能优化
- 优化了 Git 命令执行效率

---

**变更统计**: 15 次提交，涉及 8 个文件
```

## 🏗️ 项目结构

```
git-changelog-ai/
├── src/
│   └── git_changelog_ai/
│       ├── __init__.py      # 包初始化
│       ├── __main__.py      # 模块入口
│       ├── cli.py           # 命令行接口
│       ├── core.py          # 核心逻辑
│       ├── git.py           # Git 操作
│       ├── config.py        # 配置管理
│       ├── constants.py     # 常量定义
│       ├── types.py         # 类型定义
│       ├── notify.py        # 消息推送（企微）
│       └── ai/
│           ├── __init__.py
│           ├── base.py      # AI API 调用
│           └── prompts.py   # AI 提示词
├── pyproject.toml           # 项目配置
├── README.md                # 英文文档
├── README_CN.md             # 中文文档
└── LICENSE                  # MIT 许可证
```

## 🔌 支持的 AI 提供商

| 提供商 | 模型 | 说明 |
|--------|------|------|
| Gemini | gemini-3-flash-preview | Google AI，默认选项，免费额度充足 |
| OpenAI | gpt-4o | OpenAI GPT 系列，效果优秀 |
| DeepSeek | deepseek-chat | 性价比高 |

## 💡 使用技巧

1. **首次使用**：建议先运行 `--dry-run` 模式查看将发送给 AI 的数据
2. **API 选择**：国内用户推荐使用 DeepSeek
3. **大型项目**：对于变更很多的版本，AI 会自动合并相似内容
4. **自定义输出**：可以将输出重定向到文件后手动调整

## 🤝 参与贡献

欢迎提交 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 发起 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢 Google Gemini、OpenAI 等 AI 提供商提供的强大 API
- 灵感来源于 conventional commits 和语义化版本
