"""核心业务模块"""

from .note_generator import NoteGenerator
from .outline_parser import OutlineParser, Chapter, ParseResult

__all__ = ["NoteGenerator", "OutlineParser", "Chapter", "ParseResult"]
