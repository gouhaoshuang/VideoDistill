# VideoDistill - AI 视频笔记生成器

使用 Gemini AI 自动分析视频并生成结构化笔记的智能工具。

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.0+-red)

## ✨ 功能特性

- 🎬 **智能视频分析**：自动分析视频内容，提取关键信息
- 📝 **结构化笔记生成**：生成层次清晰、内容详实的 Markdown 笔记
- 🔄 **断点续传**：支持缓存机制，可继续未完成的生成任务
- 📁 **智能文件管理**：基于 Hash 的文件编码，避免重复上传
- 🎯 **AI 自动分段**：根据内容智能划分笔记段落
- 🌐 **Web 界面**：基于 Streamlit 的友好用户界面
- 💾 **多格式输出**：支持分段保存和完整合并笔记

## 📋 系统要求

- Python 3.11+
- Miniconda/Anaconda
- 4GB+ 内存
- 稳定的网络连接

## 🚀 快速开始


### 2. 创建环境

```bash
# 创建 conda 环境
conda create -n videodistill python=3.11 -y

# 激活环境
conda activate videodistill
```

### 3. 安装依赖

```bash
cd VideoDistill
pip install -r requirements.txt
```

### 4. 配置 API Key

在项目根目录创建 `.env` 文件：

```bash
GOOGLE_API_KEY=your_api_key_here
```

获取 API Key：[Google AI Studio](https://aistudio.google.com)

### 5. 启动应用

**Windows：**
```bash
.\run.bat
```

**或使用 conda 命令：**
```bash
conda run -n videodistill streamlit run main.py
```

## 📖 使用说明

### Web 界面使用

1. 打开浏览器访问 `http://localhost:8501`
2. 在侧边栏配置 Google API Key
3. 选择 AI 模型（推荐 `gemini-2.0-flash`）
4. 上传视频文件（支持 MP4, MOV, AVI, MKV, WEBM）
5. 点击"开始生成"按钮
6. 等待 AI 分析完成
7. 预览或下载生成的笔记

### 命令行测试

```bash
# API 连接测试
conda run -n videodistill python tests/simple_test.py --test api

# 完整视频测试
conda run -n videodistill python tests/simple_test.py --test video
```

## 📁 项目结构

```
VideoDistill/
├── main.py                    # Streamlit 主程序
├── config.py                  # 配置文件
├── requirements.txt           # 依赖列表
├── run.bat                    # Windows 启动脚本
├── agents.md                  # AI Agent 提示词
├── .env                       # 环境变量（需自行创建）
│
├── src/                       # 源代码目录
│   ├── gemini_client.py      # Gemini API 客户端
│   ├── note_generator.py     # 笔记生成器（支持缓存）
│   ├── prompt_templates.py   # 提示词模板加载器
│   ├── file_utils.py         # 文件管理工具
│   └── prompts/              # 提示词目录
│       ├── outline_prompt.txt
│       ├── parse_segments_prompt.txt
│       ├── segment_note_prompt.txt
│       ├── merge_notes_prompt.txt
│       └── system_instruction.txt
│
├── tests/                     # 测试目录
│   └── simple_test.py        # 简单测试脚本
│
├── outputs/                   # 输出目录（自动生成）
│   └── YYYYMMDD_hash/        # 每个视频一个目录
│       ├── metadata.json     # 视频元数据
│       ├── outline.md        # 视频大纲
│       ├── segments.json     # 分段信息
│       ├── segment_01.md     # 各段笔记
│       ├── segment_02.md
│       ├── ...
│       └── final_notes.md    # 最终合并笔记
│
└── temp/                      # 临时文件目录
```

## ⚙️ 配置选项

编辑 `config.py` 自定义配置：

```python
# AI 模型选择
DEFAULT_MODEL = "gemini-2.0-flash"
AVAILABLE_MODELS = [
    "gemini-2.0-flash",  # 最新快速模型（推荐）
    "gemini-1.5-flash",  # 稳定快速模型
    "gemini-1.5-pro"     # 高质量模型
]

# 缓存开关
ENABLE_CACHE = True  # 启用后支持断点续传

# 文件大小限制
MAX_VIDEO_SIZE_MB = 2000
```

## 🔄 缓存机制

VideoDistill 支持智能缓存：

1. **视频文件缓存**：同一视频不会重复拷贝
2. **大纲缓存**：已生成的大纲会被保存
3. **分段笔记缓存**：每段笔记独立保存，支持断点续传
4. **最终笔记缓存**：完整的合并笔记也会缓存

输出目录结构：
- 每个视频有独立的子目录（`日期_Hash码`）
- 包含元数据、大纲、分段笔记和最终笔记
- 重新上传同一视频时会自动使用缓存

## 🔧 依赖包

```
google-genai      # Gemini AI SDK
streamlit         # Web 框架
python-dotenv     # 环境变量管理
```

## ⚠️ 注意事项

1. **API 限制**：
   - 视频文件最大 2GB
   - Gemini 文件存储保留 48 小时
   - API 按使用量计费

2. **网络要求**：
   - 需要稳定的网络连接
   - 首次上传大文件可能较慢

3. **编码问题**：
   - 视频文件名支持中文
   - 输出文件使用 UTF-8 编码

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Google Gemini AI](https://ai.google.dev) - AI 模型支持
- [Streamlit](https://streamlit.io) - Web 框架

---

Made with ❤️ by Claude Code
