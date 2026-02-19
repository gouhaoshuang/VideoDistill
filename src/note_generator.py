"""
笔记生成器

负责视频大纲生成、分段解析、笔记生成和合并的核心逻辑。
支持缓存和断点续传功能。
"""

import json
import re
from typing import List, Dict, Optional, Callable
from pathlib import Path
from .gemini_client import GeminiClient
from .prompt_templates import (
    OUTLINE_PROMPT,
    PARSE_SEGMENTS_PROMPT,
    SEGMENT_NOTE_PROMPT,
    MERGE_NOTES_PROMPT,
    SYSTEM_INSTRUCTION
)
from .file_utils import VideoFileManager


class NoteGenerator:
    """视频笔记生成器，支持缓存和断点续传"""

    def __init__(
        self,
        gemini_client: GeminiClient,
        file_manager: Optional[VideoFileManager] = None,
        output_dir: str = "outputs",
        enable_cache: bool = True
    ):
        """
        初始化笔记生成器

        Args:
            gemini_client: Gemini API 客户端
            file_manager: 文件管理器（可选）
            output_dir: 输出目录
            enable_cache: 是否启用缓存
        """
        self.client = gemini_client
        self.file_manager = file_manager or VideoFileManager(output_dir)
        self.enable_cache = enable_cache
        self.current_video_dir = None
        self.current_outline = None
        self.current_segments = None

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
        video_path: str,
        original_name: str,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        生成完整笔记的主流程，支持缓存和断点续传

        Args:
            video_file: 上传的视频文件对象
            video_path: 视频文件路径
            original_name: 原始文件名
            progress_callback: 进度回调函数，接收 (current, total, message)

        Returns:
            完整的 Markdown 笔记
        """
        # 获取视频输出目录
        self.current_video_dir = self.file_manager.get_video_dir(video_path, original_name)

        def report_progress(current: int, total: int, message: str):
            if progress_callback:
                progress_callback(current, total, message)

        # 1. 检查并加载/生成大纲
        if self.enable_cache:
            cached_outline = self.file_manager.load_outline(self.current_video_dir)
            if cached_outline:
                self.current_outline = cached_outline
                report_progress(1, 5, "✅ 从缓存加载大纲...")
            else:
                report_progress(1, 5, "正在分析视频生成大纲...")
                outline = self.generate_outline(video_file)
                self.current_outline = outline
                self.file_manager.save_outline(self.current_video_dir, outline)
        else:
            report_progress(1, 5, "正在分析视频生成大纲...")
            outline = self.generate_outline(video_file)
            self.current_outline = outline
            self.file_manager.save_outline(self.current_video_dir, outline)

        # 2. 检查并加载/解析分段
        if self.enable_cache:
            cached_segments = self.file_manager.load_segments(self.current_video_dir)
            if cached_segments:
                self.current_segments = cached_segments
                report_progress(2, 5, f"✅ 从缓存加载分段（共{len(cached_segments)}段）...")
            else:
                report_progress(2, 5, "正在解析分段...")
                segments = self.parse_segments(self.current_outline)
                self.current_segments = segments
                self.file_manager.save_segments(self.current_video_dir, segments)
        else:
            report_progress(2, 5, "正在解析分段...")
            segments = self.parse_segments(self.current_outline)
            self.current_segments = segments
            self.file_manager.save_segments(self.current_video_dir, segments)

        # 3. 检查并生成每段笔记（支持断点续传）
        segment_notes = []
        total_segments = len(self.current_segments)
        cached_segment_ids = self.file_manager.get_cached_segments(self.current_video_dir)

        for i, segment in enumerate(self.current_segments):
            segment_id = segment['id']

            # 检查是否有缓存
            if self.enable_cache and segment_id in cached_segment_ids:
                cached_note = self.file_manager.load_segment_note(self.current_video_dir, segment_id)
                if cached_note:
                    segment_notes.append(cached_note)
                    report_progress(
                        3 + i,
                        3 + total_segments,
                        f"✅ 从缓存加载第 {i+1}/{total_segments} 段: {segment['title']}"
                    )
                    continue

            # 生成新笔记
            report_progress(
                3 + i,
                3 + total_segments,
                f"正在生成第 {i+1}/{total_segments} 段笔记: {segment['title']}"
            )

            note = self.generate_segment_note(self.current_outline, segment)
            segment_notes.append(note)

            # 保存到缓存
            self.file_manager.save_segment_note(self.current_video_dir, segment_id, note)

        # 4. 检查并合并笔记
        if self.enable_cache:
            cached_final = self.file_manager.load_final_notes(self.current_video_dir)
            if cached_final:
                report_progress(100, 100, "✅ 从缓存加载最终笔记...")
                return cached_final

        report_progress(
            3 + total_segments,
            3 + total_segments + 1,
            "正在合并所有笔记..."
        )

        merged_notes = self.merge_notes(segment_notes)
        self.file_manager.save_final_notes(self.current_video_dir, merged_notes)

        report_progress(
            100,
            100,
            f"✅ 笔记生成完成！已保存到: {self.current_video_dir}"
        )

        return merged_notes
