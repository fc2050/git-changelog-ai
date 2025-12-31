"""
AI module initialization.
"""

from .base import call_ai_api, build_ai_prompt
from .prompts import AI_SYSTEM_PROMPT

__all__ = [
    "call_ai_api",
    "build_ai_prompt", 
    "AI_SYSTEM_PROMPT",
]
