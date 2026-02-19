"""
提示词模板

从文件加载用于视频分析、大纲生成、笔记生成和合并的提示词模板。
"""

from pathlib import Path


class PromptLoader:
    """从文件加载提示词"""

    def __init__(self, prompts_dir: str = "src/prompts"):
        self.prompts_dir = Path(prompts_dir)

    def load_prompt(self, prompt_name: str) -> str:
        """加载指定的提示词文件"""
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            raise FileNotFoundError(f"提示词文件不存在: {prompt_file}")

    @property
    def outline_prompt(self) -> str:
        return self.load_prompt("outline_prompt")

    @property
    def parse_segments_prompt(self) -> str:
        return self.load_prompt("parse_segments_prompt")

    @property
    def segment_note_prompt(self) -> str:
        return self.load_prompt("segment_note_prompt")

    @property
    def merge_notes_prompt(self) -> str:
        return self.load_prompt("merge_notes_prompt")

    @property
    def system_instruction(self) -> str:
        return self.load_prompt("system_instruction")


# 全局加载器实例
_loader = PromptLoader()

# 保持向后兼容的导出
def get_outline_prompt() -> str:
    return _loader.outline_prompt

def get_parse_segments_prompt() -> str:
    return _loader.parse_segments_prompt

def get_segment_note_prompt() -> str:
    return _loader.segment_note_prompt

def get_merge_notes_prompt() -> str:
    return _loader.merge_notes_prompt

def get_system_instruction() -> str:
    return _loader.system_instruction

# 向后兼容：旧代码可以直接使用的常量
OUTLINE_PROMPT = get_outline_prompt()
PARSE_SEGMENTS_PROMPT = get_parse_segments_prompt()
SEGMENT_NOTE_PROMPT = get_segment_note_prompt()
MERGE_NOTES_PROMPT = get_merge_notes_prompt()
SYSTEM_INSTRUCTION = get_system_instruction()
