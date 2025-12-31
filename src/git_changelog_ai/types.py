"""
Type definitions for git-changelog-ai.
"""

from typing import TypedDict


class CommitInfo(TypedDict):
    """Git commit information"""
    hash: str
    author: str
    email: str
    date: str
    message: str


class TagInfo(TypedDict):
    """Git tag information"""
    name: str
    date: str
