"""
AI API integration for changelog generation.
"""

import json
import urllib.request
import urllib.error
from typing import List, Optional

from ..types import CommitInfo
from ..config import get_ai_config
from ..constants import (
    DEFAULT_AI_PROVIDER,
    DEFAULT_AI_TEMPERATURE,
    DEFAULT_AI_MAX_OUTPUT_TOKENS,
    DEFAULT_MAX_DIFF_CHARS,
)
from .prompts import AI_SYSTEM_PROMPT


def call_ai_api(prompt: str, provider: str = DEFAULT_AI_PROVIDER) -> Optional[str]:
    """
    Call AI API for analysis.
    
    Args:
        prompt: User prompt
        provider: AI service provider name
        
    Returns:
        AI response content, None on failure
    """
    config = get_ai_config(provider)
    if not config:
        print(f"❌ Unsupported AI provider: {provider}")
        return None
    
    api_key = config.api_key
    if not api_key:
        print(f"❌ API key not configured for {provider}")
        print(f"   Please set the {config.api_key_env} environment variable")
        return None
    
    # Build request
    if provider == 'gemini':
        url = config.base_url.format(model=config.model) + f"?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            'contents': [{'parts': [{'text': AI_SYSTEM_PROMPT + "\n\n" + prompt}]}],
            'generationConfig': {
                'temperature': DEFAULT_AI_TEMPERATURE,
                'maxOutputTokens': DEFAULT_AI_MAX_OUTPUT_TOKENS
            }
        }
    else:
        url = config.base_url
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        data = {
            'model': config.model,
            'messages': [
                {'role': 'system', 'content': AI_SYSTEM_PROMPT},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': DEFAULT_AI_TEMPERATURE,
            'max_tokens': DEFAULT_AI_MAX_OUTPUT_TOKENS
        }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if provider == 'gemini':
                return result['candidates'][0]['content']['parts'][0]['text']
            return result['choices'][0]['message']['content']
            
    except urllib.error.HTTPError as e:
        print(f"❌ AI API request failed: HTTP {e.code}")
        try:
            print(f"   Error details: {e.read().decode('utf-8')[:200]}")
        except:
            pass
        return None
    except urllib.error.URLError as e:
        print(f"❌ Network error: {e.reason}")
        return None
    except Exception as e:
        print(f"❌ AI call exception: {str(e)}")
        return None


def build_ai_prompt(from_ref: str, to_ref: str, commits: List[CommitInfo],
                    diff: str, diff_stat: str) -> str:
    """
    Build the prompt to send to AI.
    
    Args:
        from_ref: Starting reference
        to_ref: Target reference
        commits: List of commit records
        diff: Git diff content
        diff_stat: Git diff statistics
        
    Returns:
        Constructed prompt string
    """
    commit_text = "\n".join(
        f"- [{c['hash'][:7]}] {c['message']} (by {c['author']}, {c['date']})"
        for c in commits
    )
    
    diff_content = diff[:DEFAULT_MAX_DIFF_CHARS] if len(diff) > DEFAULT_MAX_DIFF_CHARS else diff
    
    return f"""请分析以下代码变更，生成版本更新摘要：

## 版本信息
从: {from_ref}
到: {to_ref}

## 提交记录 ({len(commits)}个提交)
{commit_text}

## 文件变更统计
{diff_stat}

## 代码差异 (Git Diff)
```diff
{diff_content}
```

请根据以上信息，生成结构清晰的版本更新摘要。重点关注：
1. 实际的功能变化（不要简单复述commit message）
2. 用户可感知的改进
3. 修复的问题
4. 技术层面的优化

注意合并相关的变更，使输出简洁有序。"""
