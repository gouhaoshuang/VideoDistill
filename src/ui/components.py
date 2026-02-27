"""
UI 组件模块

可复用的 Streamlit UI 组件
"""

import os
import pandas as pd
import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from config import (
    AVAILABLE_MODELS,
    ENABLE_CACHE,
    GENERATION_MODES,
    DEFAULT_GENERATION_MODE,
)


def render_sidebar_config() -> Dict[str, any]:
    """
    渲染侧边栏配置区域

    Returns:
        配置字典，包含 api_key, model, generation_mode, enable_cache
    """
    with st.sidebar:
        st.header("⚙️ 配置")

        api_key_input = st.text_input(
            "Google API Key",
            type="password",
            value=os.getenv("GOOGLE_API_KEY", ""),
            help="在 [Google AI Studio](https://aistudio.google.com) 获取 API Key",
        )

        st.markdown("---")

        model_option = st.selectbox(
            "AI 模型", AVAILABLE_MODELS, index=0, help="选择用于生成笔记的 AI 模型"
        )

        st.markdown("---")

        generation_mode = st.selectbox(
            "生成模式",
            options=list(GENERATION_MODES.keys()),
            format_func=lambda x: GENERATION_MODES[x],
            index=list(GENERATION_MODES.keys()).index(DEFAULT_GENERATION_MODE),
            help="选择笔记生成方式：分段生成适合长视频，直接生成适合短视频",
        )

        if generation_mode == "segmented":
            st.info(
                """
            📚 **分段生成模式**
            - 先生成大纲，再逐段生成笔记
            - 适合长视频、结构化内容
            - 支持断点续传
            """
            )
        else:
            st.info(
                """
            ⚡ **直接生成模式**
            - 一次性生成完整笔记
            - 适合短视频、快速笔记
            - 速度更快
            """
            )

        st.markdown("---")

        enable_cache = st.checkbox(
            "启用缓存",
            value=ENABLE_CACHE,
            help="启用后，已生成的笔记会被缓存，支持断点续传",
        )

        st.markdown("---")

        _render_usage_instructions()

        st.markdown("---")

        st.info(
            """
        ⚠️ **注意**
        - API 按使用量计费
        - 文件存储 48 小时
        - 建议先用短视频测试
        """
        )

    return {
        "api_key": api_key_input,
        "model": model_option,
        "generation_mode": generation_mode,
        "enable_cache": enable_cache,
    }


def _render_usage_instructions() -> None:
    """渲染使用说明"""
    st.subheader("📖 使用说明")
    st.markdown(
        """
    1. 选择生成模式（分段/直接）
    2. 上传视频文件
    3. 点击"开始生成"
    4. 等待 AI 分析
    5. 预览或下载笔记

    **支持格式**: MP4, MOV, AVI, MKV, WEBM

    **文件限制**: 最大 2GB

    **模式建议**:
    - 长视频（>10分钟）→ 分段生成
    - 短视频（<10分钟）→ 直接生成
    """
    )


def render_file_uploader() -> Optional[object]:
    """
    渲染单视频上传器

    Returns:
        Streamlit UploadedFile 对象，未上传时返回 None
    """
    uploaded_file = st.file_uploader(
        "选择视频文件",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        help="支持 mp4, mov, avi, mkv, webm 格式，最大 2GB",
        label_visibility="visible",
    )

    if uploaded_file:
        st.video(uploaded_file)

    return uploaded_file


def render_file_info(uploaded_file, cached: bool = False) -> None:
    """
    渲染文件信息卡片

    Args:
        uploaded_file: Streamlit UploadedFile 对象
        cached: 是否为缓存文件
    """
    if cached:
        st.info("✅ 使用已缓存的视频文件")
    else:
        st.info("📁 视频已缓存")

    st.markdown(
        f"""
    <div class="info-message">
    <strong>文件信息</strong><br>
    文件名: {uploaded_file.name}<br>
    文件大小: {uploaded_file.size / 1024 / 1024:.2f} MB<br>
    文件类型: {uploaded_file.type}
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_notes_preview(notes: str) -> None:
    """
    渲染笔记预览区域

    Args:
        notes: 笔记内容
    """
    st.markdown("---")
    st.subheader("📄 生成的笔记")

    with st.expander("📖 查看笔记预览", expanded=True):
        st.markdown(notes)


def render_download_buttons(notes: str) -> None:
    """
    渲染下载和保存按钮

    Args:
        notes: 笔记内容
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"notes_{timestamp}.md"

    dl_col, save_col = st.columns(2)

    with dl_col:
        st.download_button(
            label="📥 下载 Markdown 文件",
            data=notes,
            file_name=filename,
            mime="text/markdown",
            use_container_width=True,
        )

    with save_col:
        if st.button("💾 保存到本地", use_container_width=True):
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / filename
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(notes)
            st.success(f"✅ 已保存到: {output_path}")


def render_batch_file_editor(batch_files, default_mode: str) -> Optional[pd.DataFrame]:
    """
    渲染批量文件模式编辑器

    Args:
        batch_files: Streamlit 上传的文件列表
        default_mode: 默认生成模式

    Returns:
        编辑后的 DataFrame，未上传文件时返回 None
    """
    if not batch_files:
        return None

    st.markdown(
        f"已选择 **{len(batch_files)}** 个文件，可在下方调整每个视频的生成模式："
    )

    mode_labels = list(GENERATION_MODES.values())
    default_label = GENERATION_MODES[default_mode]

    df_init = pd.DataFrame(
        [
            {
                "文件名": uf.name,
                "大小(MB)": round(uf.size / 1024 / 1024, 1),
                "生成模式": default_label,
            }
            for uf in batch_files
        ]
    )

    edited_df = st.data_editor(
        df_init,
        column_config={
            "文件名": st.column_config.TextColumn(disabled=True),
            "大小(MB)": st.column_config.NumberColumn(disabled=True),
            "生成模式": st.column_config.SelectboxColumn(
                options=mode_labels,
                required=True,
            ),
        },
        hide_index=True,
        use_container_width=True,
        key="batch_mode_editor",
    )

    return edited_df


def render_footer() -> None:
    """渲染页脚"""
    st.markdown("---")
    st.markdown(
        """
<div style="text-align: center; color: #666; font-size: 0.9rem;">
<p>Powered by <a href="https://ai.google.dev" target="_blank">Gemini AI</a> |
Made with ❤️ using Streamlit</p>
</div>
""",
        unsafe_allow_html=True,
    )
