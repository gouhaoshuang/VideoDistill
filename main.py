"""
VideoDistill - 视频笔记生成工具

使用 Gemini AI 自动分析视频并生成结构化笔记。
"""

import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from src.gemini_client import GeminiClient
from src.note_generator import NoteGenerator

# 页面配置
st.set_page_config(
    page_title="VideoDistill - 视频笔记生成",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
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
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-header">📹 VideoDistill - AI 视频笔记生成器</div>', unsafe_allow_html=True)
st.markdown("---")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")

    # API Key 设置
    api_key_input = st.text_input(
        "Google API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="在 [Google AI Studio](https://aistudio.google.com) 获取 API Key"
    )

    st.markdown("---")

    # 模型选择
    model_option = st.selectbox(
        "AI 模型",
        ["gemini-2.0-flash", "gemini-1.5-flash"],
        index=0,
        help="选择用于生成笔记的 AI 模型"
    )

    st.markdown("---")

    # 使用说明
    st.subheader("📖 使用说明")
    st.markdown("""
    1. 上传视频文件
    2. 点击"开始生成"
    3. 等待 AI 分析
    4. 预览或下载笔记

    **支持格式**: MP4, MOV, AVI, MKV

    **文件限制**: 最大 2GB
    """)

    st.markdown("---")

    # API 限制提示
    st.info("""
    ⚠️ **注意**
    - API 按使用量计费
    - 文件存储 48 小时
    - 建议先用短视频测试
    """)

# 初始化 session state
if "video_file" not in st.session_state:
    st.session_state.video_file = None
if "notes" not in st.session_state:
    st.session_state.notes = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# 主界面
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 上传视频")

    uploaded_file = st.file_uploader(
        "选择视频文件",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        help="支持 mp4, mov, avi, mkv, webm 格式，最大 2GB",
        label_visibility="visible"
    )

    if uploaded_file:
        st.video(uploaded_file)

        # 显示文件信息
        st.markdown(f"""
        <div class="info-message">
        <strong>文件信息</strong><br>
        文件名: {uploaded_file.name}<br>
        文件大小: {uploaded_file.size / 1024 / 1024:.2f} MB<br>
        文件类型: {uploaded_file.type}
        </div>
        """, unsafe_allow_html=True)

        # 保存到 session state
        st.session_state.uploaded_file_name = uploaded_file.name

with col2:
    st.subheader("📝 生成笔记")

    # 验证 API Key
    if not api_key_input:
        st.warning("⚠️ 请先在侧边栏配置 Google API Key")
    elif uploaded_file is None:
        st.info("👈 请先上传视频文件")
    else:
        if st.button("🚀 开始生成", type="primary", use_container_width=True):
            # 保存临时文件
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / f"temp_{uploaded_file.name}"

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                # 初始化客户端
                os.environ["GOOGLE_API_KEY"] = api_key_input
                client = GeminiClient(api_key=api_key_input)
                client.model = model_option
                generator = NoteGenerator(client)

                # 进度条容器
                progress_container = st.container()

                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    def progress_callback(current, total, message):
                        progress = current / total
                        progress_bar.progress(progress)
                        status_text.text(f"{message} ({current}/{total})")

                    # 显示进度
                    status_text.text("正在上传视频...")
                    progress_bar.progress(0.1)

                    video_file = client.upload_video(str(temp_path))

                    # 生成笔记
                    status_text.text("正在生成笔记...")
                    notes = generator.generate_all_notes(
                        video_file,
                        progress_callback=progress_callback
                    )

                    progress_bar.progress(1.0)
                    status_text.text("✅ 笔记生成完成！")

                # 保存到 session state
                st.session_state.notes = notes

                # 显示成功消息
                st.markdown("""
                <div class="success-message">
                ✅ <strong>笔记生成完成！</strong>
                </div>
                """, unsafe_allow_html=True)

                # 清理临时文件
                try:
                    client.delete_file(video_file.name)
                    os.remove(temp_path)
                except:
                    pass

            except Exception as e:
                st.error(f"""
                ❌ **生成失败**

                错误信息: {str(e)}

                请检查：
                1. API Key 是否正确
                2. 网络连接是否正常
                3. 视频文件是否损坏
                """)

# 显示生成的笔记
if st.session_state.notes:
    st.markdown("---")
    st.subheader("📄 生成的笔记")

    # 笔记预览
    with st.expander("📖 查看笔记预览", expanded=True):
        st.markdown(st.session_state.notes)

    # 下载按钮
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"notes_{timestamp}.md"

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📥 下载 Markdown 文件",
            data=st.session_state.notes,
            file_name=filename,
            mime="text/markdown",
            use_container_width=True
        )

    with col2:
        # 保存到 outputs 目录
        if st.button("💾 保存到本地", use_container_width=True):
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(st.session_state.notes)

            st.success(f"✅ 已保存到: {output_path}")

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
<p>Powered by <a href="https://ai.google.dev" target="_blank">Gemini AI</a> |
Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
