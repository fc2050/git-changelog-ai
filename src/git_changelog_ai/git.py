"""
Git operations for git-changelog-ai.
"""

import subprocess
import os
import re
import fnmatch
from typing import List, Tuple
from datetime import datetime

from .types import CommitInfo, TagInfo
from .constants import IGNORE_PATTERNS, DEFAULT_MAX_DIFF_LINES


def run_git_command(cmd: str) -> Tuple[bool, str]:
    """
    Execute a Git command and return the result.
    
    Args:
        cmd: Git command string to execute
        
    Returns:
        Tuple of (success, output or error message)
    """
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return (result.returncode == 0, result.stdout if result.returncode == 0 else result.stderr)
    except Exception as e:
        return False, str(e)


def get_all_tags() -> List[TagInfo]:
    """
    Get all tags sorted by date in descending order.
    
    Returns:
        List of tag info dicts containing name and date
    """
    success, output = run_git_command(
        "git tag -l --sort=-creatordate --format='%(refname:short)|%(creatordate:short)'"
    )
    
    if not success or not output.strip():
        return []
    
    tags = []
    for line in output.strip().split('\n'):
        if not line or '|' not in line:
            continue
            
        parts = line.split('|')
        tag_name = parts[0]
        tag_date = parts[1] if len(parts) > 1 else ""
        
        # Try to extract timestamp from tag name (format: ...rc_ci_YYYYMMDDHHmm)
        timestamp_match = re.search(r'rc_ci_(\d{12})', tag_name)
        if timestamp_match:
            try:
                parsed_date = datetime.strptime(timestamp_match.group(1), '%Y%m%d%H%M')
                tag_date = parsed_date.strftime('%Y-%m-%d %H:%M')
            except ValueError:
                pass
        
        tags.append({'name': tag_name, 'date': tag_date})
    
    return tags


def get_git_commits(from_ref: str, to_ref: str) -> List[CommitInfo]:
    """
    Get commit information between two references.
    
    Args:
        from_ref: Starting reference (tag/commit/branch)
        to_ref: Target reference
        
    Returns:
        List of commit info dicts
    """
    success, output = run_git_command(
        f"git log {from_ref}..{to_ref} --pretty=format:'%H|%an|%ae|%ad|%s' --date=short"
    )
    
    if not success or not output.strip():
        return []
    
    commits = []
    for line in output.strip().split('\n'):
        if not line:
            continue
        parts = line.split('|')
        if len(parts) >= 5:
            commits.append({
                'hash': parts[0],
                'author': parts[1],
                'email': parts[2],
                'date': parts[3],
                'message': '|'.join(parts[4:])
            })
    
    return commits


def should_ignore_file(filepath: str) -> bool:
    """
    Check if a file should be ignored based on patterns.
    
    Args:
        filepath: File path to check
        
    Returns:
        True if file should be ignored
    """
    basename = os.path.basename(filepath)
    return any(
        fnmatch.fnmatch(filepath, pattern) or fnmatch.fnmatch(basename, pattern)
        for pattern in IGNORE_PATTERNS
    )


def get_git_diff_files(from_ref: str, to_ref: str, include_ignored: bool = False) -> List[str]:
    """
    Get list of changed files between references.
    
    Args:
        from_ref: Starting reference
        to_ref: Target reference
        include_ignored: Whether to include ignored files
        
    Returns:
        List of file paths
    """
    success, output = run_git_command(f"git diff {from_ref}..{to_ref} --name-only")
    if not success or not output.strip():
        return []
    
    files = output.strip().split('\n')
    if include_ignored:
        return files
    return [f for f in files if not should_ignore_file(f)]


def get_git_diff(from_ref: str, to_ref: str, files: List[str], 
                 max_lines: int = DEFAULT_MAX_DIFF_LINES) -> str:
    """
    Get code diff (limited by line count to avoid being too long).
    
    Args:
        from_ref: Starting reference
        to_ref: Target reference
        files: List of files to diff
        max_lines: Maximum line limit
        
    Returns:
        Git diff content
    """
    if not files:
        return ""
    
    files_arg = ' '.join(f'"{f}"' for f in files)
    success, output = run_git_command(f"git diff {from_ref}..{to_ref} -- {files_arg}")
    
    if not success:
        success, output = run_git_command(f"git diff {from_ref}..{to_ref}")
        if not success:
            return ""
    
    lines = output.split('\n')
    if len(lines) > max_lines:
        return '\n'.join(lines[:max_lines]) + f"\n\n... (diff too long, truncated, total {len(lines)} lines) ..."
    return output


def get_git_diff_stat(from_ref: str, to_ref: str, files: List[str]) -> str:
    """
    Get simplified diff statistics.
    
    Args:
        from_ref: Starting reference
        to_ref: Target reference
        files: List of files to stat
        
    Returns:
        Git diff stat output
    """
    if not files:
        return ""
    
    files_arg = ' '.join(f'"{f}"' for f in files)
    success, output = run_git_command(f"git diff {from_ref}..{to_ref} --stat -- {files_arg}")
    
    if not success:
        success, output = run_git_command(f"git diff {from_ref}..{to_ref} --stat")
    
    return output if success else ""


def is_git_repository() -> bool:
    """
    Check if current directory is a git repository.
    
    Returns:
        True if in a git repository
    """
    success, _ = run_git_command('git rev-parse --git-dir')
    return success


def ref_exists(ref: str) -> bool:
    """
    Check if a git reference exists.
    
    Args:
        ref: Git reference (tag/commit/branch)
        
    Returns:
        True if reference exists
    """
    success, _ = run_git_command(f"git rev-parse {ref}")
    return success
