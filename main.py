"""
VideoDistill - 视频笔记生成工具

使用 Gemini AI 自动分析视频并生成结构化笔记。
"""

import streamlit as st

# 初始化
from src.utils.streamlit_helpers import (
    init_page_config,
    init_custom_css,
    init_session_state,
    render_header,
)
from src.ui.components import (
    render_sidebar_config,
    render_footer,
)
from src.ui.handlers import (
    handle_single_video_generation,
    handle_batch_processing,
)

# ── 页面初始化 ─────────────────────────────────────────────────────────────
init_page_config()
init_custom_css()
init_session_state()

# ── 标题 ───────────────────────────────────────────────────────────────────
render_header()

# ── 侧边栏配置 ─────────────────────────────────────────────────────────────
config = render_sidebar_config()

# ── 主界面 ─────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🎬 单视频", "📦 批量处理"])

# ── Tab 1: 单视频 ───────────────────────────────────────────────────────────
with tab1:
    handle_single_video_generation(config)

# ── Tab 2: 批量处理 ─────────────────────────────────────────────────────────
with tab2:
    handle_batch_processing(config)

# ── 页脚 ─────────────────────────────────────────────────────────────────────
render_footer()
