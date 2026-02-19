"""
笔记生成器

负责视频大纲生成、大纲解析、笔记生成和合并的核心逻辑。
支持缓存和断点续传功能。
支持分段生成和直接生成两种模式。
"""

from typing import List, Dict, Optional, Callable
from pathlib import Path
from .gemini_client import GeminiClient
from .prompt_templates import (
    OUTLINE_PROMPT,
    SEGMENT_PROMPT,
    DIRECT_PROMPT,
    SYSTEM_INSTRUCTION
)
from .file_utils import VideoFileManager
from .outline_parser import OutlineParser


class NoteGenerator:
    """视频笔记生成器，支持缓存和断点续传"""

    # 生成模式枚举
    MODE_SEGMENTED = "segmented"  # 分段生成（适合长视频）
    MODE_DIRECT = "direct"        # 直接生成（适合短视频）

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
        self.outline_parser = OutlineParser()
        self.current_video_dir = None
        self.current_outline = None
        self.current_segments = None

    def generate_outline(self, video_file) -> str:
        """
        生成视频大纲

        Args:
            video_file: 上传的视频文件对象

        Returns:
            视频大纲文本（Markdown格式）
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

    def parse_outline_to_segments(self, outline: str) -> List[Dict]:
        """
        解析大纲为结构化分段列表

        Args:
            outline: 视频大纲文本（Markdown格式）

        Returns:
            分段列表，每个分段包含 id, title, description 字段
        """
        print("正在解析分段...")

        # 使用 OutlineParser 解析大纲
        result = self.outline_parser.parse(outline)
        segments = self.outline_parser.to_segment_list(result)

        print(f"解析出 {len(segments)} 个分段")
        return segments

    def generate_segment_note(
        self,
        outline: str,
        segment: Dict
    ) -> str:
        """
        为单个段落生成笔记

        Args:
            outline: 完整的视频大纲
            segment: 分段信息字典，包含 id, title, description

        Returns:
            该段落的笔记文本
        """
        print(f"正在生成段落 {segment['id']} 的笔记: {segment['title']}")

        prompt = SEGMENT_PROMPT.format(
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

    def generate_direct_note(self, video_file) -> str:
        """
        直接生成完整笔记（不分段）

        Args:
            video_file: 上传的视频文件对象

        Returns:
            完整的笔记文本
        """
        print("正在直接生成笔记...")
        note = self.client.generate_content(
            DIRECT_PROMPT,
            file=video_file,
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.6
        )
        print("笔记生成完成")
        return note

    def merge_notes(self, segment_notes: List[str], segments: List[Dict]) -> str:
        """
        合并所有分段笔记（直接拼接，添加章节标题）

        Args:
            segment_notes: 分段笔记列表
            segments: 分段信息列表

        Returns:
            合并后的完整笔记
        """
        print("正在合并笔记...")

        # 直接拼接，添加章节标题
        merged_parts = []
        for note, segment in zip(segment_notes, segments):
            # 添加章节标题
            chapter_title = f"\n\n## 第{segment['id']}章 {segment['title']}\n\n"
            merged_parts.append(chapter_title)
            merged_parts.append(note)

        merged = "".join(merged_parts)
        print("笔记合并完成")
        return merged

    def generate_all_notes(
        self,
        video_file,
        video_path: str,
        original_name: str,
        mode: str = MODE_SEGMENTED,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        生成完整笔记的主流程，支持缓存和断点续传

        Args:
            video_file: 上传的视频文件对象
            video_path: 视频文件路径
            original_name: 原始文件名
            mode: 生成模式 ("segmented" 或 "direct")
            progress_callback: 进度回调函数，接收 (current, total, message)

        Returns:
            完整的 Markdown 笔记
        """
        # 获取视频输出目录
        self.current_video_dir = self.file_manager.get_video_dir(video_path, original_name)

        def report_progress(current: int, total: int, message: str):
            if progress_callback:
                progress_callback(current, total, message)

        # 根据模式选择不同的生成流程
        if mode == self.MODE_DIRECT:
            return self._generate_direct_mode(video_file, progress_callback)
        else:
            return self._generate_segmented_mode(video_file, video_path, original_name, progress_callback)

    def _generate_direct_mode(
        self,
        video_file,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        直接生成模式

        Args:
            video_file: 上传的视频文件对象
            progress_callback: 进度回调函数

        Returns:
            完整的 Markdown 笔记
        """
        def report_progress(current: int, total: int, message: str):
            if progress_callback:
                progress_callback(current, total, message)

        # 1. 检查并加载/生成笔记
        if self.enable_cache:
            cached_note = self.file_manager.load_direct_note(self.current_video_dir)
            if cached_note:
                report_progress(100, 100, "✅ 从缓存加载笔记...")
                return cached_note

        # 2. 生成笔记
        report_progress(1, 3, "正在分析视频生成笔记...")
        note = self.generate_direct_note(video_file)

        # 3. 保存笔记
        report_progress(2, 3, "正在保存笔记...")
        self.file_manager.save_direct_note(self.current_video_dir, note)
        self.file_manager.save_final_notes(self.current_video_dir, note)

        report_progress(100, 100, "✅ 笔记生成完成！")

        return note

    def _generate_segmented_mode(
        self,
        video_file,
        video_path: str,
        original_name: str,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        分段生成模式

        Args:
            video_file: 上传的视频文件对象
            video_path: 视频文件路径
            original_name: 原始文件名
            progress_callback: 进度回调函数

        Returns:
            完整的 Markdown 笔记
        """
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

        # 2. 解析大纲为分段（直接解析，不缓存JSON）
        report_progress(2, 5, "正在解析分段...")
        segments = self.parse_outline_to_segments(self.current_outline)
        self.current_segments = segments

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

        merged_notes = self.merge_notes(segment_notes, self.current_segments)
        self.file_manager.save_final_notes(self.current_video_dir, merged_notes)

        report_progress(
            100,
            100,
            f"✅ 笔记生成完成！已保存到: {self.current_video_dir}"
        )

        return merged_notes
