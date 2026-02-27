# VideoDistill - 视频笔记生成工具

## 项目概述

VideoDistill 是一个 AI 驱动的视频笔记生成工具，用户上传本地视频后，工具自动调用 Gemini AI API 分析视频内容，生成结构化的 Markdown 笔记。

## 核心功能

1. **视频上传**: 通过 Web UI 上传本地视频文件
2. **AI 分析**: 使用 Gemini AI API 分析视频内容
3. **自动分段**: AI 自动决定分段方式
4. **笔记生成**: 针对每段生成详细笔记
5. **自动合并**: 将所有分段笔记合并成完整文档
6. **Markdown 导出**: 支持下载 Markdown 格式文件

## 技术栈

- **编程语言**: Python
- **AI SDK**: google-genai (官方 Gemini API SDK)
- **UI 框架**: Streamlit
- **AI 模型**: gemini-2.0-flash

## 工作流程

```
用户上传视频
    ↓
上传到 Gemini Files API
    ↓
生成视频大纲
    ↓
AI 自动决定分段
    ↓
逐段生成详细笔记
    ↓
合并所有笔记
    ↓
输出 Markdown 文件
```

## API 配置

- **API Key**: 已配置
- **Base URL**: https://generativelanguage.googleapis.com
- **文件限制**: 单文件最大 2GB，项目总存储 20GB
- **文件有效期**: 48 小时

## 支持的视频格式

- MP4
- MOV
- AVI
- MKV

## 项目结构

```
VideoDistill/
├── main.py                 # Streamlit 应用入口
├── requirements.txt        # 项目依赖
├── .env                    # API Key 配置
├── doc/                    # 文档目录
│   └── requirements.md     # 需求文档
├── src/
│   ├── __init__.py
│   ├── gemini_client.py    # Gemini API 客户端封装
│   ├── prompt_templates.py # 提示词模板
│   └── note_generator.py   # 笔记生成器
└── outputs/                # 生成的笔记输出目录
```

## 使用说明

1. 安装依赖: `pip install -r requirements.txt`
2. 运行应用: `streamlit run main.py`
3. 在浏览器中打开应用
4. 上传视频文件
5. 点击"开始生成"按钮
6. 等待笔记生成完成
7. 预览或下载 Markdown 文件

## 提示词策略

### 大纲生成提示词
- 分析视频内容
- 生成结构化大纲
- 按时间或逻辑顺序分段
- 包含段落标题和时间范围

### 分段笔记生成提示词
- 基于大纲段落生成详细笔记
- 包含关键概念
- 包含重要细节
- 包含示例或案例
- 使用 Markdown 格式

### 笔记合并提示词
- 合并所有分段笔记
- 添加过渡语句
- 确保整体连贯性
- 添加总体摘要和总结

## 注意事项

- Gemini API 按使用量计费，请注意控制成本
- 建议先用短视频测试
- 大视频可能需要较长的处理时间
- 生成的笔记质量取决于视频内容的清晰度
