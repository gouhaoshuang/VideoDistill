# VideoDistill src package
"""
向后兼容层：保持旧的导入路径可用

新代码应使用子模块导入：
- from src.api.gemini_client import GeminiClient
- from src.core.note_generator import NoteGenerator
- from src.storage.file_utils import VideoFileManager
- from src.config.prompt_templates import ...
"""

# API 层
from .api.gemini_client import GeminiClient

# 核心业务层
from .core.note_generator import NoteGenerator
from .core.outline_parser import OutlineParser, Chapter, ParseResult

# 存储层
from .storage.file_utils import VideoFileManager

# 配置层
from .config.prompt_templates import (
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
    # API
    "GeminiClient",
    # Core
    "NoteGenerator",
    "OutlineParser",
    "Chapter",
    "ParseResult",
    # Storage
    "VideoFileManager",
    # Config
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
