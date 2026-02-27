"""
文件处理工具

上传文件保存、API key 设置、资源清理
"""

import os
from pathlib import Path
from typing import Optional

from src.file_utils import VideoFileManager


class UploadedFileHandler:
    """处理 Streamlit 上传文件的保存和管理"""

    def __init__(self, temp_dir: str = "temp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self.file_manager = VideoFileManager()

    def save_uploaded_file(
        self, uploaded_file, original_name: Optional[str] = None
    ) -> Path:
        """
        保存上传的文件到临时目录（使用 hash 避免重复）

        Args:
            uploaded_file: Streamlit UploadedFile 对象
            original_name: 原始文件名（可选）

        Returns:
            保存后的文件路径
        """
        name = original_name or uploaded_file.name
        temp_path = self.file_manager.get_temp_video_path(
            name, temp_dir=str(self.temp_dir)
        )

        if not temp_path.exists():
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        return temp_path

    def get_temp_path(self, file_name: str) -> Path:
        """获取文件的临时路径（不保存）"""
        return self.file_manager.get_temp_video_path(
            file_name, temp_dir=str(self.temp_dir)
        )

    @staticmethod
    def prepare_api_key(api_key: str) -> None:
        """设置 API key 到环境变量"""
        os.environ["GOOGLE_API_KEY"] = api_key

    @staticmethod
    def cleanup_resources(
        client, video_file: Optional[object], temp_path: Path
    ) -> None:
        """
        清理 Gemini 上的文件和本地临时文件

        Args:
            client: GeminiClient 实例
            video_file: Gemini 上的文件对象
            temp_path: 本地临时文件路径
        """
        try:
            if video_file and hasattr(video_file, "name"):
                client.delete_file(video_file.name)
        except Exception:
            pass

        try:
            if temp_path and temp_path.exists():
                os.remove(temp_path)
        except Exception:
            pass
