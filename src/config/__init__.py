"""配置/模板模块"""

from .prompt_templates import (
    PromptLoader,
    get_outline_prompt,
    get_segment_prompt,
    get_direct_prompt,
    get_system_instruction,
    OUTLINE_PROMPT,
    SEGMENT_PROMPT,
    DIRECT_PROMPT,
    SYSTEM_INSTRUCTION,
)

__all__ = [
    "PromptLoader",
    "get_outline_prompt",
    "get_segment_prompt",
    "get_direct_prompt",
    "get_system_instruction",
    "OUTLINE_PROMPT",
    "SEGMENT_PROMPT",
    "DIRECT_PROMPT",
    "SYSTEM_INSTRUCTION",
]
