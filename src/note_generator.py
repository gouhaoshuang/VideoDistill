"""
笔记生成器

负责视频大纲生成、分段解析、笔记生成和合并的核心逻辑。
"""

import json
import re
from typing import List, Dict, Optional
from .gemini_client import GeminiClient
from .prompt_templates import (
    OUTLINE_PROMPT,
    PARSE_SEGMENTS_PROMPT,
    SEGMENT_NOTE_PROMPT,
    MERGE_NOTES_PROMPT,
    SYSTEM_INSTRUCTION
)


class NoteGenerator:
    """视频笔记生成器"""

    def __init__(self, gemini_client: GeminiClient):
        """
        初始化笔记生成器

        Args:
            gemini_client: Gemini API 客户端
        """
        self.client = gemini_client

    def generate_outline(self, video_file) -> str:
        """
        生成视频大纲

        Args:
            video_file: 上传的视频文件对象

        Returns:
            视频大纲文本
        """
        print("正在生成视频大纲...")
        outline = self.client.generate_content(
            OUTLINE_PROMPT,
            file=video_file,
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.5
        )
        print("大纲生成完成")
        return outline

    def parse_segments(self, outline: str) -> List[Dict]:
        """
        解析大纲为结构化分段列表

        Args:
            outline: 视频大纲文本

        Returns:
            分段列表，每个分段包含 id, title, description 等字段
        """
        print("正在解析分段...")

        prompt = PARSE_SEGMENTS_PROMPT.format(outline=outline)
        response = self.client.generate_content(
            prompt,
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3
        )

        # 尝试解析 JSON
        try:
            # 提取 JSON 部分（处理可能的前后文字）
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                segments = json.loads(json_match.group())
            else:
                segments = json.loads(response)
            print(f"解析出 {len(segments)} 个分段")
            return segments
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            print(f"原始响应: {response}")
            # 如果解析失败，返回单个分段
            return [{
                "id": 1,
                "title": "视频内容",
                "description": outline,
                "time_range": None
            }]

    def generate_segment_note(
        self,
        outline: str,
        segment: Dict
    ) -> str:
        """
        为单个段落生成笔记

        Args:
            outline: 完整的视频大纲
            segment: 分段信息字典

        Returns:
            该段落的笔记文本
        """
        print(f"正在生成段落 {segment['id']} 的笔记: {segment['title']}")

        prompt = SEGMENT_NOTE_PROMPT.format(
            outline=outline,
            segment_id=segment['id'],
            segment_title=segment['title'],
            segment_description=segment.get('description', '')
        )

        note = self.client.generate_content(
            prompt,
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.6
        )

        return note

    def merge_notes(self, segment_notes: List[str]) -> str:
        """
        合并所有分段笔记

        Args:
            segment_notes: 分段笔记列表

        Returns:
            合并后的完整笔记
        """
        print("正在合并笔记...")

        notes_text = "\n\n---\n\n".join(segment_notes)
        prompt = MERGE_NOTES_PROMPT.format(segments_notes=notes_text)

        merged = self.client.generate_content(
            prompt,
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.5
        )

        print("笔记合并完成")
        return merged

    def generate_all_notes(
        self,
        video_file,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        生成完整笔记的主流程

        Args:
            video_file: 上传的视频文件对象
            progress_callback: 进度回调函数，接收 (current, total, message)

        Returns:
            完整的 Markdown 笔记
        """
        # 1. 生成大纲
        if progress_callback:
            progress_callback(1, 5, "正在分析视频生成大纲...")
        outline = self.generate_outline(video_file)

        # 2. 解析分段
        if progress_callback:
            progress_callback(2, 5, "正在解析分段...")
        segments = self.parse_segments(outline)

        # 3. 为每段生成笔记
        segment_notes = []
        total_segments = len(segments)

        for i, segment in enumerate(segments):
            if progress_callback:
                progress_callback(
                    3 + i,
                    3 + total_segments,
                    f"正在生成第 {i+1}/{total_segments} 段笔记: {segment['title']}"
                )

            note = self.generate_segment_note(outline, segment)
            segment_notes.append(note)

        # 4. 合并笔记
        if progress_callback:
            progress_callback(
                3 + total_segments,
                3 + total_segments + 1,
                "正在合并所有笔记..."
            )

        merged_notes = self.merge_notes(segment_notes)

        if progress_callback:
            progress_callback(
                3 + total_segments + 1,
                3 + total_segments + 1,
                "笔记生成完成！"
            )

        return merged_notes
