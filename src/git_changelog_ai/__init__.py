"""
Git Changelog AI - AI-powered changelog generator

A tool that analyzes git commits and generates beautiful release notes using AI.
"""

__version__ = "0.2.0"
__author__ = "Your Name"
__email__ = "your@email.com"

from .core import generate_changelog
from .git import get_all_tags, get_git_commits

__all__ = [
    "__version__",
    "generate_changelog",
    "get_all_tags",
    "get_git_commits",
]
