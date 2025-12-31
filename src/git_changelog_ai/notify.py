"""
WeChat Work (企业微信) webhook notification module.

Supports sending changelog to WeChat Work group chat via webhook robot.
Reference: https://developer.work.weixin.qq.com/document/path/91770
"""

import json
import urllib.request
import urllib.error
from typing import Optional


def send_wecom_message(webhook_url: str, content: str) -> tuple[bool, str]:
    """
    Send markdown message to WeChat Work group via webhook.
    
    Args:
        webhook_url: WeChat Work webhook URL
        content: Markdown content (max 4096 bytes)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not webhook_url:
        return False, "Webhook URL is not configured"
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={
                'Content-Type': 'application/json'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('errcode') == 0:
                return True, "Message sent successfully"
            else:
                return False, f"API Error: {result.get('errmsg', 'Unknown error')}"
                
    except urllib.error.HTTPError as e:
        return False, f"HTTP Error: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return False, f"URL Error: {e.reason}"
    except json.JSONDecodeError as e:
        return False, f"JSON Parse Error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected Error: {str(e)}"


def truncate_content_for_wecom(content: str, max_bytes: int = 4096) -> str:
    """
    Truncate content to fit WeChat Work markdown message limit.
    
    WeChat Work markdown message has a 4096 byte limit.
    
    Args:
        content: Original content
        max_bytes: Maximum bytes allowed (default: 4096)
        
    Returns:
        Truncated content if needed
    """
    if len(content.encode('utf-8')) <= max_bytes:
        return content
    
    # Leave some buffer for truncation notice
    target_bytes = max_bytes - 100
    
    # Truncate by removing characters from the end
    truncated = content
    while len(truncated.encode('utf-8')) > target_bytes:
        truncated = truncated[:len(truncated) - 100]
    
    # Try to truncate at a newline for cleaner output
    last_newline = truncated.rfind('\n')
    if last_newline > len(truncated) // 2:
        truncated = truncated[:last_newline]
    
    return truncated + "\n\n⚠️ 内容过长已截断，完整内容请查看控制台或文件输出"


def send_changelog_to_wecom(webhook_url: str, changelog: str) -> tuple[bool, str]:
    """
    Send changelog to WeChat Work group.
    
    Keep the content consistent with console/file output.
    
    Args:
        webhook_url: WeChat Work webhook URL
        changelog: Changelog content (same as console/file output)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Truncate if content exceeds limit, keep original content otherwise
    content = truncate_content_for_wecom(changelog)
    return send_wecom_message(webhook_url, content)
