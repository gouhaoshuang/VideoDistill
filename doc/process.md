# VideoDistill 项目功能说明

VideoDistill 是一个基于 Gemini AI 的智能视频笔记生成工具。用户通过 Web 界面上传视频文件后，系统会自动将视频上传至 Gemini API 进行分析，首先生成视频的整体大纲，然后 AI 根据内容智能划分段落，为每个段落生成详细的笔记，最后合并成完整的 Markdown 文档。系统支持智能缓存机制：视频文件通过 Hash 编码避免重复拷贝，已生成的大纲、分段笔记和最终笔记都会持久化存储，实现断点续传功能。输出目录按视频分类（outputs/日期_Hash/），包含元数据、大纲、分段笔记（segment_01.md, segment_02.md...）和最终合并笔记（final_notes.md）。支持多种 AI 模型选择（gemini-2.0-flash、gemini-1.5-flash、gemini-1.5-pro），并提供友好的进度跟踪和错误处理。
