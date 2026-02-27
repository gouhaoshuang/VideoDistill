"""
UI 模块

提供可复用的 Streamlit UI 组件和事件处理器
"""

from .components import (
    render_sidebar_config,
    render_file_uploader,
    render_file_info,
    render_notes_preview,
    render_download_buttons,
    render_batch_file_editor,
    render_footer,
)
from .handlers import (
    handle_single_video_generation,
    handle_batch_processing,
)

__all__ = [
    "render_sidebar_config",
    "render_file_uploader",
    "render_file_info",
    "render_notes_preview",
    "render_download_buttons",
    "render_batch_file_editor",
    "render_footer",
    "handle_single_video_generation",
    "handle_batch_processing",
]
