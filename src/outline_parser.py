"""
大纲解析器

解析包含章节标记的大纲Markdown文件，提取结构化的分段信息。
支持 "第一章" 和 "第1章" 两种章节格式。
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import re


@dataclass
class Chapter:
    """章节数据类"""
    number: int
    title: str
    description: str
    raw_content: str


@dataclass
class ParseResult:
    """解析结果"""
    title: str
    chapters: List[Chapter]


class OutlineParser:
    """大纲解析器"""

    # 支持的章节格式：第一章、第1章、Chapter 1
    CHAPTER_PATTERN = re.compile(
        r'^##+\s*(第([一二三四五六七八九十百千0-9]+)章|Chapter\s+(\d+))[:：]\s*(.+)$',
        re.MULTILINE
    )

    # 中文数字转换（支持一到一百）
    CN_NUMBERS = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
        '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
        '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
        '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
        '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34, '三十五': 35,
        '三十六': 36, '三十七': 37, '三十八': 38, '三十九': 39, '四十': 40,
        '四十一': 41, '四十二': 42, '四十三': 43, '四十四': 44, '四十五': 45,
        '四十六': 46, '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50,
        '五十一': 51, '五十二': 52, '五十三': 53, '五十四': 54, '五十五': 55,
        '五十六': 56, '五十七': 57, '五十八': 58, '五十九': 59, '六十': 60,
        '六十一': 61, '六十二': 62, '六十三': 63, '六十四': 64, '六十五': 65,
        '六十六': 66, '六十七': 67, '六十八': 68, '六十九': 69, '七十': 70,
        '七十一': 71, '七十二': 72, '七十三': 73, '七十四': 74, '七十五': 75,
        '七十六': 76, '七十七': 77, '七十八': 78, '七十九': 79, '八十': 80,
        '八十一': 81, '八十二': 82, '八十三': 83, '八十四': 84, '八十五': 85,
        '八十六': 86, '八十七': 87, '八十八': 88, '八十九': 89, '九十': 90,
        '九十一': 91, '九十二': 92, '九十三': 93, '九十四': 94, '九十五': 95,
        '九十六': 96, '九十七': 97, '九十八': 98, '九十九': 99, '一百': 100,
    }

    def parse(self, outline_content: str) -> ParseResult:
        """
        解析大纲内容

        Args:
            outline_content: 大纲的Markdown文本内容

        Returns:
            ParseResult 包含标题和章节列表
        """
        title = self._extract_title(outline_content)
        chapters = self._extract_chapters(outline_content)
        return ParseResult(title=title, chapters=chapters)

    def parse_file(self, outline_path: Path) -> ParseResult:
        """
        解析大纲文件

        Args:
            outline_path: 大纲文件路径

        Returns:
            ParseResult 包含标题和章节列表
        """
        content = outline_path.read_text(encoding='utf-8')
        return self.parse(content)

    def _extract_title(self, content: str) -> str:
        """提取文档标题（第一个 # 标题）"""
        # 匹配第一个 # 开头的标题
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else ""

    def _extract_chapters(self, content: str) -> List[Chapter]:
        """提取所有章节"""
        chapters = []

        # 找到所有章节标记
        for match in self.CHAPTER_PATTERN.finditer(content):
            full_match = match.group(0)
            cn_number = match.group(2)  # 中文数字
            arabic_number = match.group(3)  # 阿拉伯数字
            title = match.group(4).strip()  # 章节标题

            # 解析章节编号
            chapter_number = self._parse_chapter_number(cn_number, arabic_number)

            # 提取该章节的描述内容（从章节标记到下一个章节或文档结尾）
            start_pos = match.end()
            next_match = self.CHAPTER_PATTERN.search(content, start_pos)

            if next_match:
                description = content[start_pos:next_match.start()].strip()
            else:
                description = content[start_pos:].strip()

            # 清理描述中的分隔符
            description = re.sub(r'^---+\s*$', '', description, flags=re.MULTILINE).strip()

            chapters.append(Chapter(
                number=chapter_number,
                title=title,
                description=description,
                raw_content=description
            ))

        return chapters

    def _parse_chapter_number(self, cn_num: str, arabic_num: str) -> int:
        """
        解析章节编号（支持中文和阿拉伯数字）

        Args:
            cn_num: 中文数字（如"一"、"十二"）
            arabic_num: 阿拉伯数字（如"1"、"12"）

        Returns:
            章节编号的整数值
        """
        # 优先使用阿拉伯数字
        if arabic_num:
            return int(arabic_num)

        # 使用中文数字转换
        if cn_num and cn_num in self.CN_NUMBERS:
            return self.CN_NUMBERS[cn_num]

        # 尝试直接转换（处理纯数字字符串）
        if cn_num and cn_num.isdigit():
            return int(cn_num)

        return 1  # 默认返回1

    def to_segment_list(self, result: ParseResult) -> List[Dict]:
        """
        将解析结果转换为分段列表（用于兼容旧代码）

        Args:
            result: 解析结果

        Returns:
            分段字典列表，每个包含 id, title, description
        """
        return [
            {
                'id': chapter.number,
                'title': chapter.title,
                'description': chapter.description,
            }
            for chapter in result.chapters
        ]
