"""
UI 事件处理器

处理用户交互的核心业务逻辑
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, Optional

from src.gemini_client import GeminiClient
from src.note_generator import NoteGenerator
from src.file_utils import VideoFileManager
from src.batch import BatchProcessor
from src.utils.file_handler import UploadedFileHandler
from config import GENERATION_MODES


def handle_single_video_generation(config: Dict[str, any]) -> None:
    """
    处理单视频笔记生成

    Args:
        config: 配置字典，来自 render_sidebar_config()
    """
    api_key = config["api_key"]
    model = config["model"]
    generation_mode = config["generation_mode"]
    enable_cache = config["enable_cache"]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 上传视频")

        from src.ui.components import render_file_uploader, render_file_info

        uploaded_file = render_file_uploader()

        if uploaded_file:
            render_file_info(uploaded_file)
            st.session_state.uploaded_file_name = uploaded_file.name

    with col2:
        st.subheader("📝 生成笔记")

        if not api_key:
            st.warning("⚠️ 请先在侧边栏配置 Google API Key")
        elif uploaded_file is None:
            st.info("👈 请先上传视频文件")
        elif st.button("🚀 开始生成", type="primary", use_container_width=True):
            _execute_single_generation(
                uploaded_file, api_key, model, generation_mode, enable_cache
            )

    # 笔记展示
    if st.session_state.notes:
        from src.ui.components import render_notes_preview, render_download_buttons

        render_notes_preview(st.session_state.notes)
        render_download_buttons(st.session_state.notes)


def _execute_single_generation(
    uploaded_file, api_key: str, model: str, generation_mode: str, enable_cache: bool
) -> None:
    """执行单视频生成的核心逻辑"""
    try:
        UploadedFileHandler.prepare_api_key(api_key)
        client = GeminiClient(api_key=api_key)
        client.model = model

        file_handler = UploadedFileHandler()
        temp_path = file_handler.save_uploaded_file(uploaded_file)
        file_manager = VideoFileManager()

        generator = NoteGenerator(
            client, file_manager=file_manager, enable_cache=enable_cache
        )

        progress_container = st.container()
        with progress_container:
            from src.utils.streamlit_helpers import render_progress_container

            progress_bar, status_text = render_progress_container()

            def progress_callback(current, total, message):
                progress_bar.progress(current / total)
                status_text.text(f"{message} ({current}/{total})")

            status_text.text("正在上传视频...")
            progress_bar.progress(0.1)

            video_file = client.upload_video(str(temp_path))

            status_text.text("正在生成笔记...")
            notes = generator.generate_all_notes(
                video_file,
                video_path=str(temp_path),
                original_name=uploaded_file.name,
                mode=generation_mode,
                progress_callback=progress_callback,
            )

            progress_bar.progress(1.0)
            status_text.text("✅ 笔记生成完成！")

        st.session_state.notes = notes

        st.markdown(
            """
        <div class="success-message">
        ✅ <strong>笔记生成完成！</strong>
        </div>
        """,
            unsafe_allow_html=True,
        )

        file_handler.cleanup_resources(client, video_file, temp_path)

    except Exception as e:
        st.error(
            f"""
        ❌ **生成失败**

        错误信息: {str(e)}

        请检查：
        1. API Key 是否正确
        2. 网络连接是否正常
        3. 视频文件是否损坏
        """
        )


def handle_batch_processing(config: Dict[str, any]) -> None:
    """
    处理批量视频处理

    Args:
        config: 配置字典，来自 render_sidebar_config()
    """
    api_key = config["api_key"]
    model = config["model"]
    generation_mode = config["generation_mode"]
    enable_cache = config["enable_cache"]

    st.subheader("📦 批量视频处理")

    if not api_key:
        st.warning("⚠️ 请先在侧边栏配置 Google API Key")
        return

    batch_col1, batch_col2 = st.columns([1, 1])

    with batch_col1:
        st.markdown("**上传多个视频文件**")
        batch_files = st.file_uploader(
            "选择多个视频文件",
            type=["mp4", "mov", "avi", "mkv", "webm"],
            accept_multiple_files=True,
            help="可同时选择多个视频文件",
            label_visibility="visible",
            key="batch_uploader",
        )

        edited_df = None
        if batch_files:
            from src.ui.components import render_batch_file_editor

            edited_df = render_batch_file_editor(batch_files, generation_mode)

        max_workers = st.slider(
            "并发处理数",
            min_value=1,
            max_value=4,
            value=2,
            help="同时处理的视频数量，建议不超过 2 以避免 API 限流",
        )

    with batch_col2:
        st.markdown("**处理进度**")

        if not batch_files:
            st.info("👈 请先上传视频文件")
        elif st.button("🚀 开始批量生成", type="primary", use_container_width=True):
            _execute_batch_processing(
                batch_files,
                edited_df,
                api_key,
                model,
                generation_mode,
                enable_cache,
                max_workers,
            )


def _execute_batch_processing(
    batch_files,
    edited_df: Optional[pd.DataFrame],
    api_key: str,
    model: str,
    generation_mode: str,
    enable_cache: bool,
    max_workers: int,
) -> None:
    """执行批量处理的核心逻辑"""
    st.session_state.batch_log = []

    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    file_handler = UploadedFileHandler()

    # 从 data_editor 读取每行选择的模式
    mode_labels = list(GENERATION_MODES.values())
    mode_keys = list(GENERATION_MODES.keys())
    row_modes = edited_df["生成模式"].tolist() if edited_df is not None else []

    video_items = []
    for idx, uploaded_file in enumerate(batch_files):
        temp_path = file_handler.save_uploaded_file(uploaded_file)

        label = (
            row_modes[idx]
            if idx < len(row_modes)
            else GENERATION_MODES[generation_mode]
        )
        task_mode = (
            mode_keys[mode_labels.index(label)]
            if label in mode_labels
            else generation_mode
        )

        video_items.append(
            {
                "path": str(temp_path),
                "original_name": uploaded_file.name,
                "mode": task_mode,
            }
        )

    progress_bar = st.progress(0)
    log_area = st.empty()

    def batch_progress(done, total, name, msg):
        progress_bar.progress(done / total)
        st.session_state.batch_log.append(msg)
        log_area.markdown("\n".join(f"- {line}" for line in st.session_state.batch_log))

    processor = BatchProcessor(
        api_key=api_key,
        model=model,
        generation_mode=generation_mode,
        max_workers=max_workers,
        enable_cache=enable_cache,
        output_dir="outputs",
    )

    try:
        queue = processor.process_files(
            video_items,
            progress_callback=batch_progress,
        )
        summary = queue.summary
        progress_bar.progress(1.0)
        st.success(
            f"✅ 批量完成：共 {summary['total']} 个，"
            f"完成 {summary['done']}，跳过 {summary['skipped']}，失败 {summary['failed']}"
        )
        st.markdown(f"📄 汇总报告：`{queue.batch_dir / 'batch_summary.md'}`")
    except Exception as e:
        st.error(f"❌ 批量处理出错: {e}")
