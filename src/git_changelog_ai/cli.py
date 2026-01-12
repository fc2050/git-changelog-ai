"""
Command-line interface for git-changelog-ai.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

from .constants import DEFAULT_TAGS_LIMIT, DEFAULT_AI_PROVIDER
from .config import get_available_providers
from .git import get_all_tags, is_git_repository, ref_exists
from .core import generate_changelog
from .notify import send_changelog_to_wecom


def list_tags(date_filter: Optional[str] = None, limit: int = DEFAULT_TAGS_LIMIT) -> None:
    """
    List available tags.
    
    Args:
        date_filter: Date filter condition
        limit: Number limit for display
    """
    tags = get_all_tags()
    
    if not tags:
        print("❌ No tags found")
        return
    
    if date_filter:
        tags = [t for t in tags if date_filter in t['date']]
        if not tags:
            print(f"❌ No tags found with date containing '{date_filter}'")
            return
    
    display_count = min(limit, len(tags))
    print(f"\n📋 Available Tags (total {len(tags)}, showing latest {display_count}):\n")
    print(f"{'No.':<6}{'Tag Name':<50}{'Date':<20}")
    print("-" * 76)
    
    for i, tag in enumerate(tags[:limit], 1):
        print(f"{i:<6}{tag['name']:<50}{tag['date']:<20}")
    
    print("\n💡 Usage:")
    print("   git-changelog-ai <tag1> <tag2>")
    print("   git-changelog-ai --recent 2        # Basic mode")
    print("   git-changelog-ai --recent 2 --ai   # AI-powered mode")


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description='AI-powered Git changelog generator - Analyze Git changes and generate release notes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available tags
  git-changelog-ai --list
  git-changelog-ai --list --date 2025-12-30
  
  # Basic mode (keyword-based classification)
  git-changelog-ai --recent 2
  
  # AI-powered mode (recommended)
  git-changelog-ai --recent 2 --ai
  git-changelog-ai --recent 2 --ai --provider openai
  
  # Debug mode (view data sent to AI)
  git-changelog-ai --recent 2 --dry-run
  
  # Compare specific tags
  git-changelog-ai tag1 tag2 --ai
  
  # Output to file
  git-changelog-ai --recent 2 --ai --output CHANGELOG.md
  
  # Send to WeChat Work group
  git-changelog-ai --recent 2 --ai --webhook

  # Send existing changelog to webhook (without re-analyzing)
  git-changelog-ai --notify --input CHANGELOG.md
  git-changelog-ai --notify --input CHANGELOG.md --webhook-url https://...
  cat CHANGELOG.md | git-changelog-ai --notify

API Key Configuration:
  Set environment variables:
  - GOOGLE_API_KEY (Gemini, default)
  - OPENAI_API_KEY (OpenAI)
  - DEEPSEEK_API_KEY (DeepSeek)
  - WECOM_WEBHOOK_URL (WeChat Work webhook for message push)
        """
    )
    
    parser.add_argument('from_ref', nargs='?', help='Starting version (tag/commit hash/branch)')
    parser.add_argument('to_ref', nargs='?', help='Target version (tag/commit hash/branch)')
    
    parser.add_argument('-l', '--list', action='store_true', help='List available tags')
    parser.add_argument('-d', '--date', help='Filter tags by date (format: YYYY-MM-DD or partial)')
    parser.add_argument('--limit', type=int, default=DEFAULT_TAGS_LIMIT, 
                        help=f'Limit number of tags to list (default: {DEFAULT_TAGS_LIMIT})')
    parser.add_argument('-r', '--recent', type=int, 
                        help='Compare recent N tags (e.g., --recent 2)')
    parser.add_argument('-o', '--output', help='Output file path (default: stdout)')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Show detailed info (include commit hash)')
    
    parser.add_argument('--ai', action='store_true', help='Enable AI-powered analysis mode')
    parser.add_argument('--provider', default=DEFAULT_AI_PROVIDER,
                        choices=get_available_providers(),
                        help=f'AI service provider (default: {DEFAULT_AI_PROVIDER})')
    parser.add_argument('--dry-run', action='store_true',
                        help='Debug mode: output raw git data and AI prompt without calling AI API')
    
    parser.add_argument('--webhook', action='store_true',
                        help='Send changelog to WeChat Work group via webhook')
    parser.add_argument('--webhook-url', 
                        help='WeChat Work webhook URL (overrides WECOM_WEBHOOK_URL env var)')
    
    # Notify mode: send existing changelog to webhook without re-analyzing
    parser.add_argument('--notify', action='store_true',
                        help='Send existing changelog to webhook (without generating new one)')
    parser.add_argument('-i', '--input', 
                        help='Input file path for --notify mode (reads from stdin if not specified)')
    
    parser.add_argument('--version', action='store_true', help='Show version information')
    
    return parser


def load_env_file() -> None:
    """
    Load environment variables from .env file.
    
    Searches for .env file in git-changelog-ai package directory.
    """
    # Get the package installation directory (where this cli.py is located)
    package_dir = Path(__file__).parent.parent.parent  # src/git_changelog_ai -> src -> project root
    env_file = package_dir / '.env'
    
    if not env_file.exists():
        return
    
    # Parse and load .env file
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE format
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip()
                    # Remove surrounding quotes
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    # Only set if not already in environment
                    if key and key not in os.environ:
                        os.environ[key] = value
    except Exception:
        pass  # Silently ignore .env parsing errors


def send_existing_changelog(args) -> None:
    """
    Send existing changelog content to webhook without re-analyzing.
    
    Args:
        args: Parsed command line arguments
    """
    # Determine webhook URL
    webhook_url = args.webhook_url or os.environ.get('WECOM_WEBHOOK_URL', '')
    if not webhook_url:
        print("❌ Error: Webhook URL not configured", file=sys.stderr)
        print("   Set WECOM_WEBHOOK_URL environment variable or use --webhook-url option", 
              file=sys.stderr)
        sys.exit(1)
    
    # Read changelog content
    if args.input:
        # Read from file
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        try:
            changelog = input_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        if sys.stdin.isatty():
            print("❌ Error: No input provided", file=sys.stderr)
            print("   Use --input to specify a file, or pipe content via stdin", file=sys.stderr)
            print("   Example: cat CHANGELOG.md | git-changelog-ai --notify", file=sys.stderr)
            sys.exit(1)
        changelog = sys.stdin.read()
    
    if not changelog.strip():
        print("❌ Error: Empty changelog content", file=sys.stderr)
        sys.exit(1)
    
    # Send to webhook
    print(f"📤 Sending changelog to WeChat Work...")
    if args.verbose:
        print(f"   Webhook URL: {webhook_url[:50]}...")
        print(f"   Content length: {len(changelog)} characters")
    
    success, msg = send_changelog_to_wecom(webhook_url, changelog)
    if success:
        print(f"✅ {msg}")
    else:
        print(f"❌ Failed to send: {msg}", file=sys.stderr)
        sys.exit(1)


def main():
    """Program entry point."""
    # Load .env file first
    load_env_file()
    
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Show version
    if args.version:
        from . import __version__
        print(f"git-changelog-ai version {__version__}")
        return
    
    # Notify mode: send existing changelog to webhook
    if args.notify:
        send_existing_changelog(args)
        return
    
    # Check if in Git repository
    if not is_git_repository():
        print("❌ Error: Current directory is not a Git repository", file=sys.stderr)
        sys.exit(1)
    
    # List tags
    if args.list:
        list_tags(date_filter=args.date, limit=args.limit)
        return
    
    # Determine references to compare
    if args.recent:
        tags = get_all_tags()
        if len(tags) < args.recent:
            print(f"❌ Error: Only {len(tags)} tags available, cannot compare recent {args.recent}", 
                  file=sys.stderr)
            sys.exit(1)
        from_ref, to_ref = tags[args.recent - 1]['name'], tags[0]['name']
        print(f"📌 Selected Tags: {from_ref} → {to_ref}")
    elif args.from_ref and args.to_ref:
        from_ref, to_ref = args.from_ref, args.to_ref
    else:
        parser.print_help()
        print("\n💡 Quick Start:")
        print("   git-changelog-ai --list")
        print("   git-changelog-ai --recent 2 --ai")
        return
    
    # Validate references exist
    for ref in [from_ref, to_ref]:
        if not ref_exists(ref):
            print(f"❌ Error: Reference '{ref}' not found", file=sys.stderr)
            print(f"   Use --list to see available tags", file=sys.stderr)
            sys.exit(1)
    
    # Generate changelog
    try:
        changelog = generate_changelog(
            from_ref, to_ref,
            use_ai=args.ai,
            ai_provider=args.provider,
            verbose=args.verbose,
            dry_run=args.dry_run,
        )
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(changelog)
            print(f"\n✅ Changelog saved to: {args.output}")
        else:
            print("\n" + "=" * 80)
            print(changelog)
            print("=" * 80)
        
        # Send to WeChat Work if webhook is enabled
        if args.webhook:
            webhook_url = args.webhook_url or os.environ.get('WECOM_WEBHOOK_URL', '')
            if not webhook_url:
                print("\n⚠️ Webhook URL not configured")
                print("   Set WECOM_WEBHOOK_URL environment variable or use --webhook-url option")
            else:
                print("\n📤 Sending changelog to WeChat Work...")
                
                success, msg = send_changelog_to_wecom(webhook_url, changelog)
                if success:
                    print(f"✅ {msg}")
                else:
                    print(f"❌ Failed to send: {msg}")
        
        print("\n🎉 Generation complete!")
        
    except Exception as e:
        print(f"\n❌ Generation failed: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
