# 🤖 Git Changelog AI

[![PyPI version](https://badge.fury.io/py/git-changelog-ai.svg)](https://pypi.org/project/git-changelog-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[English](README.md) | [中文](README_CN.md)

AI-powered changelog generator that analyzes git commits and generates beautiful, structured release notes.

## 🎯 Why Git Changelog AI?

Most changelog tools only reorganize commit messages. **Git Changelog AI is different** - it analyzes actual code changes (`git diff`) to understand what really changed, not just what developers wrote in their commit messages.

| | Traditional Tools | Git Changelog AI |
|---|---|---|
| Input | Commit messages only | Commit messages + **Code Diff** |
| Analysis | Text formatting/classification | **Semantic understanding** |
| Output | Reorganized commit messages | **Intelligent summary** based on actual changes |

## ✨ Features

- 🧠 **True AI Analysis** - Analyzes actual code diff, not just commit messages
- 🔍 **Intelligent Classification** - Automatically categorizes changes (features, fixes, refactoring, etc.)
- 🤖 **Smart Summarization** - AI understands code changes and generates human-friendly descriptions
- 📝 **Clean Markdown Output** - Generates well-formatted, professional changelogs
- 🚀 **Zero Dependencies** - Uses only Python standard library (no pip install required for basic mode)
- 🔌 **Multiple AI Providers** - Supports Gemini, OpenAI, and DeepSeek
- 📤 **WeChat Work Integration** - Push changelog to group chat via webhook

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install git-changelog-ai
```

### From Source

```bash
git clone https://github.com/yourusername/git-changelog-ai.git
cd git-changelog-ai
pip install -e .
```

## 🚀 Quick Start

### 1. Set up your API key

```bash
# For Gemini (default)
export GOOGLE_API_KEY="your-api-key"

# Or for other providers
export OPENAI_API_KEY="your-api-key"
export DEEPSEEK_API_KEY="your-api-key"
```

### 2. Generate changelog

```bash
# List available tags
git-changelog-ai --list

# Compare recent 2 tags with AI analysis
git-changelog-ai --recent 2 --ai

# Compare specific tags
git-changelog-ai v1.0.0 v1.1.0 --ai

# Output to file
git-changelog-ai --recent 2 --ai --output CHANGELOG.md

# Send to WeChat Work group
git-changelog-ai --recent 2 --ai --webhook
```

## 📖 Usage

### Basic Commands

```bash
# List all tags
git-changelog-ai --list

# Filter tags by date
git-changelog-ai --list --date 2025-01

# Basic mode (keyword-based classification, no AI)
git-changelog-ai --recent 2

# AI-powered mode (recommended)
git-changelog-ai --recent 2 --ai

# Use specific AI provider
git-changelog-ai --recent 2 --ai --provider openai

# Debug mode (see what would be sent to AI)
git-changelog-ai --recent 2 --dry-run

# Verbose output (includes commit hashes)
git-changelog-ai --recent 2 --verbose

# Send changelog to WeChat Work group
git-changelog-ai --recent 2 --ai --webhook

# Send with custom webhook URL
git-changelog-ai --recent 2 --ai --webhook --webhook-url "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"

# Send existing changelog to webhook (without re-analyzing)
git-changelog-ai --notify --input CHANGELOG.md
git-changelog-ai --notify --input CHANGELOG.md --webhook-url "https://..."
cat CHANGELOG.md | git-changelog-ai --notify
```

### Command Options

| Option | Description |
|--------|-------------|
| `from_ref` | Starting version (tag/commit hash/branch) |
| `to_ref` | Target version (tag/commit hash/branch) |
| `--list`, `-l` | List available tags |
| `--date`, `-d` | Filter tags by date |
| `--limit` | Limit number of tags to display (default: 20) |
| `--recent`, `-r` | Compare recent N tags |
| `--ai` | Enable AI-powered analysis |
| `--provider` | AI provider (gemini/openai/deepseek) |
| `--output`, `-o` | Output file path |
| `--verbose`, `-v` | Show detailed information |
| `--dry-run` | Debug mode without calling AI |
| `--webhook` | Send changelog to WeChat Work group |
| `--webhook-url` | Custom webhook URL (overrides env var) |
| `--notify` | Send existing changelog to webhook (without generating new one) |
| `--input`, `-i` | Input file path for --notify mode (reads from stdin if not specified) |
| `--version` | Show version |
| `--help`, `-h` | Show help message |

## 🔧 Configuration

### Environment Variables

| Variable | Provider | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Gemini | Google AI API key |
| `OPENAI_API_KEY` | OpenAI | OpenAI API key |
| `DEEPSEEK_API_KEY` | DeepSeek | DeepSeek API key |
| `WECOM_WEBHOOK_URL` | WeChat Work | Webhook URL for group robot |

### Supported AI Providers

| Provider | Model | Description |
|----------|-------|-------------|
| Gemini | gemini-3-flash-preview | Google AI, default option, generous free tier |
| OpenAI | gpt-4o | OpenAI GPT series, excellent quality |
| DeepSeek | deepseek-chat | Cost-effective |

### Ignored Files

The following files are automatically ignored when generating changelogs:

- `CHANGELOG.md`, `CHANGELOG*.md`
- `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`

### Ignored Authors

Commits from the following authors are automatically ignored (e.g., CI bots):

- `vfe_athena`

You can modify `IGNORE_AUTHORS` in `constants.py` to customize.

## 📋 Example Output

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

## 🏗️ Project Structure

```
git-changelog-ai/
├── src/
│   └── git_changelog_ai/
│       ├── __init__.py      # Package init
│       ├── __main__.py      # Module entry point
│       ├── cli.py           # Command-line interface
│       ├── core.py          # Core logic
│       ├── git.py           # Git operations
│       ├── config.py        # Configuration
│       ├── constants.py     # Constants
│       ├── types.py         # Type definitions
│       ├── notify.py        # Notification (WeChat Work)
│       └── ai/
│           ├── __init__.py
│           ├── base.py      # AI API calls
│           └── prompts.py   # AI prompts
├── pyproject.toml           # Project config
├── README.md                # English docs
├── README_CN.md             # Chinese docs
└── LICENSE                  # MIT License
```

## 💡 Tips

1. **First time use**: Run `--dry-run` mode first to see data that would be sent to AI
2. **Large projects**: For versions with many changes, AI will automatically merge similar content
3. **Custom output**: You can redirect output to a file and adjust manually

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to Google Gemini, OpenAI, and other AI providers for their powerful APIs
- Inspired by conventional commits and semantic versioning
