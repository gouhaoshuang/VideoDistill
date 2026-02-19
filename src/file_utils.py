"""
文件工具类

处理视频文件名的hash编码、缓存管理和输出目录结构
"""

import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class VideoFileManager:
    """管理视频文件的hash编码、缓存和输出目录"""

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def get_video_hash(self, file_path: str) -> str:
        """
        根据视频文件路径生成唯一hash标识

        使用文件名和文件大小生成hash，确保同一视频生成相同hash
        """
        path = Path(file_path)
        file_size = path.stat().st_size if path.exists() else 0

        # 使用文件名和大小生成hash
        hash_input = f"{path.name}_{file_size}"
        return hashlib.md5(hash_input.encode('utf-8')).hexdigest()[:12]

    def get_video_dir(self, file_path: str, original_name: Optional[str] = None) -> Path:
        """
        获取视频对应的输出目录

        目录命名格式: YYYYMMDD_HashCode
        """
        video_hash = self.get_video_hash(file_path)
        date_str = datetime.now().strftime("%Y%m%d")
        dir_name = f"{date_str}_{video_hash}"
        video_dir = self.output_dir / dir_name
        video_dir.mkdir(parents=True, exist_ok=True)

        # 保存元数据
        self._save_metadata(video_dir, file_path, original_name)

        return video_dir

    def _save_metadata(self, video_dir: Path, file_path: str, original_name: Optional[str] = None):
        """保存视频元数据"""
        metadata_file = video_dir / "metadata.json"

        metadata = {
            "video_hash": self.get_video_hash(file_path),
            "original_name": original_name or Path(file_path).name,
            "created_at": datetime.now().isoformat(),
            "source_path": file_path
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def get_temp_video_path(self, file_path: str, temp_dir: str = "temp") -> Path:
        """
        获取临时视频文件路径

        使用hash避免重复拷贝同一视频
        """
        temp_path = Path(temp_dir)
        temp_path.mkdir(exist_ok=True)

        video_hash = self.get_video_hash(file_path)
        temp_filename = f"video_{video_hash}.mp4"
        return temp_path / temp_filename

    def save_outline(self, video_dir: Path, outline: str):
        """保存大纲到文件"""
        outline_file = video_dir / "outline.md"
        with open(outline_file, 'w', encoding='utf-8') as f:
            f.write(outline)

    def load_outline(self, video_dir: Path) -> Optional[str]:
        """从缓存加载大纲"""
        outline_file = video_dir / "outline.md"
        if outline_file.exists():
            with open(outline_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def save_segments(self, video_dir: Path, segments: List[Dict]):
        """保存分段信息到文件"""
        segments_file = video_dir / "segments.json"
        with open(segments_file, 'w', encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

    def load_segments(self, video_dir: Path) -> Optional[List[Dict]]:
        """从缓存加载分段信息"""
        segments_file = video_dir / "segments.json"
        if segments_file.exists():
            with open(segments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_segment_note(self, video_dir: Path, segment_id: int, note: str):
        """保存单个分段的笔记"""
        segment_file = video_dir / f"segment_{segment_id:02d}.md"
        with open(segment_file, 'w', encoding='utf-8') as f:
            f.write(note)

    def load_segment_note(self, video_dir: Path, segment_id: int) -> Optional[str]:
        """从缓存加载单个分段笔记"""
        segment_file = video_dir / f"segment_{segment_id:02d}.md"
        if segment_file.exists():
            with open(segment_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def get_cached_segments(self, video_dir: Path) -> List[int]:
        """获取已缓存的分段ID列表"""
        cached = []
        for f in video_dir.glob("segment_*.md"):
            # 从文件名提取段号
            try:
                segment_id = int(f.stem.split("_")[1])
                cached.append(segment_id)
            except (IndexError, ValueError):
                continue
        return sorted(cached)

    def save_final_notes(self, video_dir: Path, notes: str):
        """保存最终合并的笔记"""
        notes_file = video_dir / "final_notes.md"
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write(notes)

    def load_final_notes(self, video_dir: Path) -> Optional[str]:
        """从缓存加载最终笔记"""
        notes_file = video_dir / "final_notes.md"
        if notes_file.exists():
            with open(notes_file, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def get_video_info(self, video_dir: Path) -> Optional[Dict]:
        """获取视频的元数据信息"""
        metadata_file = video_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def list_all_videos(self) -> List[Dict]:
        """列出所有已处理的视频"""
        videos = []
        for video_dir in self.output_dir.iterdir():
            if video_dir.is_dir():
                info = self.get_video_info(video_dir)
                if info:
                    # 检查处理进度
                    cached_segments = self.get_cached_segments(video_dir)
                    has_outline = (video_dir / "outline.md").exists()
                    has_final = (video_dir / "final_notes.md").exists()

                    videos.append({
                        "dir_name": video_dir.name,
                        "path": str(video_dir),
                        "original_name": info.get("original_name"),
                        "created_at": info.get("created_at"),
                        "has_outline": has_outline,
                        "has_final": has_final,
                        "cached_segments": cached_segments,
                        "total_segments": len(cached_segments)
                    })

        # 按创建时间倒序排列
        videos.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return videos
