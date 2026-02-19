"""
提示词模板

从文件加载用于视频分析、大纲生成、笔记生成的提示词模板。
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
    def segment_prompt(self) -> str:
        return self.load_prompt("segment_prompt")

    @property
    def direct_prompt(self) -> str:
        return self.load_prompt("direct_prompt")

    @property
    def system_instruction(self) -> str:
        return self.load_prompt("system_instruction")


# 全局加载器实例
_loader = PromptLoader()

# 保持向后兼容的导出
def get_outline_prompt() -> str:
    return _loader.outline_prompt

def get_segment_prompt() -> str:
    return _loader.segment_prompt

def get_direct_prompt() -> str:
    return _loader.direct_prompt

def get_system_instruction() -> str:
    return _loader.system_instruction

# 向后兼容：旧代码可以直接使用的常量
OUTLINE_PROMPT = get_outline_prompt()
SEGMENT_PROMPT = get_segment_prompt()
DIRECT_PROMPT = get_direct_prompt()
SYSTEM_INSTRUCTION = get_system_instruction()
