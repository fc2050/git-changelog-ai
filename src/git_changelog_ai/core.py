"""
Core changelog generation logic.
"""

from typing import Dict, List, Optional

from .types import CommitInfo
from .constants import (
    COMMIT_KEYWORDS,
    CATEGORY_DISPLAY,
    SKIP_COMMIT_KEYWORDS,
    COMMIT_PREFIXES,
    DEFAULT_AI_PROVIDER,
    IGNORE_PATTERNS,
)
from .git import (
    get_git_commits,
    get_git_diff_files,
    get_git_diff,
    get_git_diff_stat,
    should_ignore_file,
)
from .ai import call_ai_api, build_ai_prompt, AI_SYSTEM_PROMPT


def classify_commits(commits: List[CommitInfo]) -> Dict[str, List[CommitInfo]]:
    """
    Classify commits by their message content.
    
    Args:
        commits: List of commit records
        
    Returns:
        Dict with category names as keys and lists of commits as values
    """
    categories = {key: [] for key, _ in CATEGORY_DISPLAY}
    
    for commit in commits:
        message = commit['message'].lower()
        
        # Skip certain commit types
        if any(skip in message for skip in SKIP_COMMIT_KEYWORDS):
            continue
        
        # Classify by keywords
        classified = False
        for category, keywords in COMMIT_KEYWORDS.items():
            if any(keyword in message for keyword in keywords):
                categories[category].append(commit)
                classified = True
                break
        
        if not classified:
            categories['others'].append(commit)
    
    return categories


def format_commit_message(message: str) -> str:
    """
    Format commit message by removing common prefixes and capitalizing.
    
    Args:
        message: Original commit message
        
    Returns:
        Formatted message
    """
    formatted = message
    for prefix in COMMIT_PREFIXES:
        if formatted.lower().startswith(prefix):
            formatted = formatted[len(prefix):].strip()
            break
    
    return formatted[0].upper() + formatted[1:] if formatted else formatted


def print_dry_run_info(commits: List[CommitInfo], diff: str, diff_stat: str, prompt: str) -> None:
    """
    Print debug mode detailed information.
    
    Args:
        commits: List of commit records
        diff: Git diff content
        diff_stat: Git diff statistics
        prompt: AI prompt
    """
    separator = "=" * 80
    sub_separator = "-" * 40
    
    print(f"\n{separator}")
    print("🔍 [DRY-RUN Debug Mode] - AI API will not be called")
    print(separator)
    
    print(f"\n{sub_separator}")
    print("🚫 Ignored file patterns:")
    print(sub_separator)
    for pattern in IGNORE_PATTERNS:
        print(f"  - {pattern}")
    
    print(f"\n{sub_separator}")
    print("📋 Raw Git commits:")
    print(sub_separator)
    for c in commits:
        print(f"  [{c['hash'][:7]}] {c['date']} | {c['author']}")
        print(f"           {c['message']}")
    
    print(f"\n{sub_separator}")
    print("📊 Git Diff statistics:")
    print(sub_separator)
    print(diff_stat)
    
    print(f"\n{sub_separator}")
    print("📝 Git Diff content (first 100 lines):")
    print(sub_separator)
    diff_lines = diff.split('\n')
    for line in diff_lines[:100]:
        print(line)
    if len(diff_lines) > 100:
        print(f"\n... (total {len(diff_lines)} lines, showing first 100) ...")
    
    print(f"\n{separator}")
    print("🤖 Full prompt to be sent to AI:")
    print(separator)
    print(f"\n[System Prompt]:\n{sub_separator}")
    print(AI_SYSTEM_PROMPT)
    print(f"\n[User Prompt]:\n{sub_separator}")
    print(prompt)
    print(f"\n{separator}")
    print(f"📏 Prompt stats: System={len(AI_SYSTEM_PROMPT)} chars, User={len(prompt)} chars, Total={len(AI_SYSTEM_PROMPT) + len(prompt)} chars")
    print(f"{separator}\n")


def generate_basic_changelog(commits: List[CommitInfo], changed_files: List[str],
                             diff_stat: str, verbose: bool = False) -> str:
    """
    Generate basic changelog without AI.
    
    Args:
        commits: List of commit records
        changed_files: List of changed files
        diff_stat: Git diff statistics
        verbose: Whether to show detailed info
        
    Returns:
        Generated changelog content
    """
    if not commits:
        return "⚠️ No changes found\n"
    
    categories = classify_commits(commits)
    total_categorized = sum(len(v) for v in categories.values())
    
    # Generate content for each category
    changelog_parts = []
    for key, title in CATEGORY_DISPLAY:
        items = categories[key]
        if items:
            lines = [f"## {title}\n"]
            for item in items:
                msg = format_commit_message(item['message'])
                suffix = f" ({item['hash'][:7]})" if verbose else ""
                lines.append(f"- {msg}{suffix}")
            changelog_parts.append('\n'.join(lines))
    
    changelog = '\n\n'.join(changelog_parts)
    
    # Add statistics
    changelog += f"\n\n---\n\n**变更统计**: {total_categorized} 项变更，涉及 {len(changed_files)} 个文件\n"
    
    if diff_stat:
        changelog += f"\n<details>\n<summary>📈 文件变更详情</summary>\n\n```\n{diff_stat}\n```\n</details>\n"
    
    return changelog


def generate_ai_changelog(from_ref: str, to_ref: str, commits: List[CommitInfo],
                          all_files: List[str], diff: str, diff_stat: str,
                          provider: str = DEFAULT_AI_PROVIDER, 
                          dry_run: bool = False) -> Optional[str]:
    """
    Generate intelligent changelog using AI.
    
    Args:
        from_ref: Starting reference
        to_ref: Target reference
        commits: List of commit records
        all_files: All changed files (to show ignored ones)
        diff: Git diff content
        diff_stat: Git diff statistics
        provider: AI service provider
        dry_run: Whether in debug mode
        
    Returns:
        Generated changelog content, None on failure
    """
    if not commits:
        return None
    
    prompt = build_ai_prompt(from_ref, to_ref, commits, diff, diff_stat)
    
    # Dry-run mode
    if dry_run:
        # Show ignored files
        ignored_files = [f for f in all_files if should_ignore_file(f)]
        print_dry_run_info(commits, diff, diff_stat, prompt)
        
        if ignored_files:
            print(f"\n  Excluded {len(ignored_files)} files:")
            for f in ignored_files:
                print(f"    × {f}")
        
        return "[DRY-RUN Mode - AI not called]"
    
    print(f"🤖 Using AI ({provider}) to analyze code changes...")
    return call_ai_api(prompt, provider)


def generate_changelog(from_ref: str, to_ref: str, use_ai: bool = False,
                       ai_provider: str = DEFAULT_AI_PROVIDER, 
                       verbose: bool = False, dry_run: bool = False) -> str:
    """
    Main function to generate changelog.
    
    Args:
        from_ref: Starting reference
        to_ref: Target reference
        use_ai: Whether to use AI mode
        ai_provider: AI service provider
        verbose: Whether to show detailed info
        dry_run: Whether in debug mode
        
    Returns:
        Complete changelog content
    """
    print(f"📊 Analyzing version changes: {from_ref} → {to_ref}")
    
    # Collect Git data
    commits = get_git_commits(from_ref, to_ref)
    if not commits:
        return f"# 更新日志\n\n**{from_ref} → {to_ref}**\n\n⚠️ 未发现任何变更\n"
    
    print(f"✅ Found {len(commits)} commits")
    
    # Get file list
    all_files = get_git_diff_files(from_ref, to_ref, include_ignored=True)
    changed_files = [f for f in all_files if not should_ignore_file(f)]
    ignored_count = len(all_files) - len(changed_files)
    
    if ignored_count > 0:
        print(f"📁 {len(changed_files)} file changes ({ignored_count} files ignored)")
    else:
        print(f"📁 {len(changed_files)} file changes")
    
    # Get diff info
    diff = get_git_diff(from_ref, to_ref, changed_files)
    diff_stat = get_git_diff_stat(from_ref, to_ref, changed_files)
    
    # Generate header
    header = f"# 更新日志\n\n**{from_ref} → {to_ref}**\n\n"
    if commits:
        first_date, last_date = commits[-1]['date'], commits[0]['date']
        date_info = f"📅 发布日期: {last_date}" if first_date == last_date else f"📅 变更周期: {first_date} ~ {last_date}"
        header += f"{date_info}\n\n"
    
    # Generate content based on mode
    if use_ai or dry_run:
        ai_content = generate_ai_changelog(
            from_ref, to_ref, commits, all_files, diff, diff_stat, ai_provider, dry_run
        )
        
        if dry_run:
            return header + "\n[DRY-RUN Mode - Debug output above, no content generated]\n"
        
        if ai_content:
            content = ai_content
            # Add statistics for AI mode
            if diff_stat:
                content += f"\n\n---\n\n**变更统计**: {len(commits)} 次提交，涉及 {len(changed_files)} 个文件\n"
                content += f"\n<details>\n<summary>📈 文件变更详情</summary>\n\n```\n{diff_stat}\n```\n</details>\n"
        else:
            print("⚠️ AI analysis failed, falling back to basic mode")
            content = generate_basic_changelog(commits, changed_files, diff_stat, verbose)
    else:
        print("🔍 Classifying commits...")
        content = generate_basic_changelog(commits, changed_files, diff_stat, verbose)
    
    return header + content
