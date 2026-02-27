# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 项目概述

VideoDistill 是一个基于 Python 的 AI 视频笔记生成工具，使用 Google Gemini AI。它通过 Streamlit Web 界面分析视频内容并生成结构化的 Markdown 笔记。

## 开发命令

### 运行应用

```bash
# Windows
.\run.bat

# 使用 conda（跨平台）
conda run -n videodistill streamlit run main.py

# 或显式指定 Python
conda activate videodistill
streamlit run main.py
```

### 测试

```bash
# 运行所有测试
pytest

# 运行指定测试文件
pytest tests/test_outline_parser.py

# 详细输出模式
pytest -v

# 运行覆盖率测试
pytest --cov-report=html:tests/.temp/htmlcov --cov-report=term-missing
```

### 代码质量

```bash
# 格式化代码
black .
isort .

# 代码检查
ruff check .
```

### 类型检查

```bash
# 安装 pyright（首次使用）
conda run -n videodistill pip install pyright

# 检查单个文件
conda run -n videodistill pyright <文件路径>

# 检查整个项目
conda run -n videodistill pyright src/
```

> **说明**: Pyright 是 Pylance 的底层引擎，运行类型检查可发现与 VSCode 中 Pylance 相同的错误。

### 环境配置

```bash
# 创建 conda 环境
conda create -n videodistill python=3.11 -y
conda activate videodistill

# 安装依赖
pip install -r requirements.txt
```

**API Key**: 设置 `GOOGLE_API_KEY` 环境变量（不使用 `.env` 文件 — 仅使用系统环境变量）。

## 架构设计

### 核心组件

```
main.py                    # Streamlit Web UI
├── GeminiClient          # API 封装，带重试逻辑
├── NoteGenerator         # 笔记生成编排
│   ├── generate_outline()       # 步骤 1: 创建视频大纲
│   ├── parse_outline_to_segments()  # 步骤 2: 解析大纲为章节
│   ├── generate_segment_note()  # 步骤 3: 按章节生成笔记
│   └── merge_notes()            # 步骤 4: 合并最终输出
├── VideoFileManager      # 基于哈希的缓存/恢复系统
└── OutlineParser         # Markdown 章节提取
```

### 生成模式

**分段模式**（默认，用于长视频）：
1. 上传视频 → 生成大纲
2. 解析大纲为章节（支持"第一章"、"第1章"、"Chapter 1"）
3. 按章节生成笔记（可恢复）
4. 合并为最终笔记

**直接模式**（用于短视频）：
1. 上传视频 → 一次性生成完整笔记

### 缓存系统

视频通过哈希识别：`MD5(filename + filesize)[:12]`

输出目录结构：
```
outputs/
└── YYYYMMDD_hash/           # 每个唯一视频一个目录
    ├── metadata.json        # 视频元数据
    ├── outline.md           # 生成的大纲
    ├── segment_01.md        # 分章笔记
    ├── segment_02.md
    ├── ...
    ├── direct_note.md       # 直接模式输出
    └── final_notes.md       # 合并的最终笔记
```

缓存支持：
- 重新上传时跳过重复处理
- 恢复中断的分段生成
- 复用缓存的大纲/分段

### 关键文件

| 文件 | 用途 |
|------|---------|
| [config.py](config.py) | 模型、模式、路径常量配置 |
| [src/gemini_client.py](src/gemini_client.py) | Gemini API 封装，含 429 重试（指数退避） |
| [src/note_generator.py](src/note_generator.py) | 核心编排，模式选择 |
| [src/file_utils.py](src/file_utils.py) | VideoFileManager 缓存管理 |
| [src/outline_parser.py](src/outline_parser.py) | 基于正则的章节提取 |
| [src/prompt_templates.py](src/prompt_templates.py) | 从 `src/prompts/*.txt` 加载提示词 |

### 提示词模板

编辑 `src/prompts/` 中的提示词：
- `outline_prompt.txt` - 视频分析大纲生成
- `segment_prompt.txt` - 分章笔记生成
- `direct_prompt.txt` - 一次性笔记生成
- `system_instruction.txt` - 系统级 AI 指令

## 配置

模型配置位于 [config.py](config.py:5-10)：
```python
DEFAULT_MODEL = "gemini-2.0-flash"
AVAILABLE_MODELS = ["gemini-3-pro-preview", "gemini-3-flash-preview"]
```

发布新 Gemini 模型时更新这些配置。

## 测试模式

测试使用 pytest 和 fixtures。参考 [tests/test_outline_parser.py](tests/test_outline_parser.py) 了解模式：
- `setup_method()` 用于每个测试的初始化
- `tmp_path` pytest fixture 用于文件 I/O 测试
- 全面的边界情况覆盖（空输入、混合格式等）

测试输出目录为 `tests/.temp/`（在 [pytest.ini](pytest.ini) 中配置）。

## 重要说明

- **无 .env 文件**: API Key 仅通过 `GOOGLE_API_KEY` 环境变量设置
- **文件保留**: Gemini 文件 48 小时后过期
- **速率限制**: 内置 429 错误重试（最多 5 次，指数退避）
- **视频限制**: 最大文件大小 2GB
- **编码**: 所有文件使用 UTF-8，支持中文文件名

