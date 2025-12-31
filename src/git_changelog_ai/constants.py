"""
Constants and configuration values for git-changelog-ai.
"""

from typing import Dict, List, Tuple

# Default parameters
DEFAULT_MAX_DIFF_LINES = 3000
DEFAULT_MAX_DIFF_CHARS = 50000  # Maximum characters for diff content
DEFAULT_TAGS_LIMIT = 20
DEFAULT_AI_PROVIDER = 'gemini'
DEFAULT_AI_TEMPERATURE = 0.3
DEFAULT_AI_MAX_OUTPUT_TOKENS = 4000  # Maximum output tokens for AI

# Files to ignore (similar to .gitignore)
IGNORE_PATTERNS: List[str] = [
    "CHANGELOG.md",
    "CHANGELOG*.md",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
]

# Authors to ignore (e.g., CI bots)
IGNORE_AUTHORS: List[str] = [
    "vfe_athena",
]

# Commit classification keywords mapping
COMMIT_KEYWORDS: Dict[str, List[str]] = {
    'new_features': ['新增', '添加', 'add', 'feat', 'feature', '功能', 'new', 'implement', '支持'],
    'bug_fixes': ['修复', '修正', 'fix', 'bug', '问题', 'issue', '错误', 'resolve', 'hotfix'],
    'performance': ['优化', '性能', 'perf', 'performance', '提升', '改进', 'improve', 'optimize', '加速'],
    'refactoring': ['重构', 'refactor', '调整', '重写', 'rewrite', 'restructure', '改造'],
    'documentation': ['文档', 'doc', 'documentation', '注释', 'comment', 'readme', 'changelog'],
    'styling': ['样式', 'style', 'css', 'ui', '界面', '美化', 'format', '布局'],
    'configuration': ['配置', 'config', 'configuration', '设置', 'setting', 'build', 'ci', 'chore', 'deps']
}

# Category display configuration
CATEGORY_DISPLAY: List[Tuple[str, str]] = [
    ('new_features', '✨ 新功能'),
    ('bug_fixes', '🐛 问题修复'),
    ('performance', '⚡ 性能优化'),
    ('refactoring', '🔨 代码重构'),
    ('styling', '🎨 样式调整'),
    ('configuration', '🔧 配置变更'),
    ('documentation', '📝 文档更新'),
    ('others', '📦 其他变更')
]

# Keywords for commits to skip
SKIP_COMMIT_KEYWORDS: List[str] = ['merge', 'version', '版本', 'release']

# Common commit message prefixes
COMMIT_PREFIXES: List[str] = ['feat:', 'fix:', 'chore:', 'docs:', 'style:', 'refactor:', 'perf:', 'test:']
