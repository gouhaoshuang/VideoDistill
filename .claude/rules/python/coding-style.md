---
paths:
  - "**/*.py"
  - "**/*.pyi"
---
# Python 编码风格

> 本文件扩展了 [common/coding-style.md](../common/coding-style.md)，包含 Python 特定内容。



## 格式化

**提交代码前必须运行格式化**，确保代码风格一致：

```bash
# 检查格式（不修改文件）
conda run -n videodistill black --check <文件或目录>

# 格式化（修改文件）
conda run -n videodistill black <文件或目录>

# 显示差异（不修改）
conda run -n videodistill black --diff <文件或目录>
```


## 类型检查

**提交代码前必须运行类型检查**，确保无类型错误：

```bash
# 首次使用：安装 pyright
conda run -n videodistill pip install pyright

# 检查单个文件
conda run -n videodistill pyright <文件路径>

# 检查整个项目
conda run -n videodistill pyright src/
```


### 环境说明

- **环境**: `videodistill` conda 环境
- **工具**: pyright（Pylance 底层引擎，结果与 VSCode 一致）
- **目标**: 0 errors, 0 warnings
