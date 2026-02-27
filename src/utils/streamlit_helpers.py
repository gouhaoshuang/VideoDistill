"""
Streamlit 辅助工具

页面配置、自定义样式、session state 管理
"""

import streamlit as st
from typing import Tuple


def init_page_config() -> None:
    """初始化 Streamlit 页面配置"""
    st.set_page_config(
        page_title="VideoDistill - 视频笔记生成",
        page_icon="📹",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def init_custom_css() -> None:
    """注入自定义 CSS 样式"""
    st.markdown(
        """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""",
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    """初始化 Streamlit session state 变量"""
    defaults = {
        "video_file": None,
        "notes": None,
        "uploaded_file_name": None,
        "batch_log": [],
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def render_header() -> None:
    """渲染页面标题"""
    st.markdown(
        '<div class="main-header">📹 VideoDistill - AI 视频笔记生成器</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")


def render_progress_container() -> Tuple[st.progress, st.empty]:
    """
    创建进度条和状态文本容器

    Returns:
        (progress_bar, status_text) 元组
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    return progress_bar, status_text
