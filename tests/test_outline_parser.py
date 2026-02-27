"""
大纲解析器单元测试

测试 OutlineParser 类的解析功能
"""

import sys
import pytest
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.outline_parser import OutlineParser


class TestOutlineParser:
    """大纲解析器测试"""

    def setup_method(self):
        """每个测试前创建解析器实例"""
        self.parser = OutlineParser()

    # ===== 基本解析测试 =====

    def test_parse_simple_outline_with_chinese_numbers(self):
        """测试解析简单的中文数字章节格式"""
        outline = """# 视频学习笔记

## 第一章：视频主题介绍
这是第一段的描述内容。

## 第二章：核心概念讲解
这是第二段的描述内容。
"""
        result = self.parser.parse(outline)

        assert result.title == "视频学习笔记"
        assert len(result.chapters) == 2
        assert result.chapters[0].number == 1
        assert result.chapters[0].title == "视频主题介绍"
        assert "第一段的描述" in result.chapters[0].description
        assert result.chapters[1].number == 2
        assert result.chapters[1].title == "核心概念讲解"

    def test_parse_outline_with_arabic_numbers(self):
        """测试解析阿拉伯数字章节格式"""
        outline = """# 课程大纲

## 第1章：基础语法
介绍基础语法知识。

## 第2章：高级特性
介绍高级特性。

## 第3章：实战案例
实战案例分析。
"""
        result = self.parser.parse(outline)

        assert result.title == "课程大纲"
        assert len(result.chapters) == 3
        assert result.chapters[0].number == 1
        assert result.chapters[1].number == 2
        assert result.chapters[2].number == 3

    def test_parse_outline_with_mixed_numbers(self):
        """测试解析混合数字格式"""
        outline = """# 混合格式测试

## 第一章：入门
入门内容。

## 第2章：进阶
进阶内容。

## 第三章：高级
高级内容。
"""
        result = self.parser.parse(outline)

        assert len(result.chapters) == 3
        assert result.chapters[0].number == 1
        assert result.chapters[1].number == 2
        assert result.chapters[2].number == 3

    # ===== 分隔符测试 =====

    def test_parse_with_dash_separators(self):
        """测试带 --- 分隔符的大纲"""
        outline = """# 带分隔符的大纲

## 第一章：第一部分
第一部分的描述。

---

## 第二章：第二部分
第二部分的描述。

---

## 第三章：第三部分
第三部分的描述。
"""
        result = self.parser.parse(outline)

        assert len(result.chapters) == 3
        # 确保分隔符不影响解析
        assert result.chapters[1].title == "第二部分"

    # ===== 章节标题格式测试 =====

    def test_parse_with_colon_separators(self):
        """测试不同类型的冒号分隔符"""
        outline = """# 标题

## 第一章：中文冒号
内容1

## 第2章:英文冒号
内容2
"""
        result = self.parser.parse(outline)

        assert len(result.chapters) == 2
        assert result.chapters[0].title == "中文冒号"
        assert result.chapters[1].title == "英文冒号"

    # ===== 描述提取测试 =====

    def test_extract_multiline_description(self):
        """测试提取多行描述"""
        outline = """# 测试大纲

## 第一章：多行描述
这是第一行描述。
这是第二行描述。
这是第三行描述。

## 第二章：下一段
下一段内容。
"""
        result = self.parser.parse(outline)

        assert len(result.chapters) == 2
        assert "第一行描述" in result.chapters[0].description
        assert "第二行描述" in result.chapters[0].description
        assert "第三行描述" in result.chapters[0].description

    # ===== 边界情况测试 =====

    def test_parse_empty_outline(self):
        """测试解析空大纲"""
        outline = ""
        result = self.parser.parse(outline)

        assert result.title == ""
        assert len(result.chapters) == 0

    def test_parse_outline_without_title(self):
        """测试没有标题的大纲"""
        outline = """## 第一章：直接开始
内容
"""
        result = self.parser.parse(outline)

        assert result.title == ""
        assert len(result.chapters) == 1

    def test_parse_outline_without_chapters(self):
        """测试没有章节的大纲"""
        outline = """# 只有标题

这里是一些前言内容。

## 第一章：正文
正文内容。
"""
        result = self.parser.parse(outline)

        assert result.title == "只有标题"
        assert len(result.chapters) == 1
        assert result.chapters[0].title == "正文"

    # ===== 中文数字转换测试 =====

    def test_chinese_number_conversion(self):
        """测试中文数字转换"""
        # 一到十
        for i, cn in enumerate(
            ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"], 1
        ):
            assert self.parser._parse_chapter_number(cn, "") == i

    def test_arabic_number_priority(self):
        """测试阿拉伯数字优先级"""
        # 当同时提供中文和阿拉伯数字时，优先使用阿拉伯数字
        assert self.parser._parse_chapter_number("十", "5") == 5

    # ===== to_segment_list 转换测试 =====

    def test_to_segment_list_conversion(self):
        """测试转换为分段列表格式"""
        outline = """# 测试

## 第一章：第一段
描述1

## 第二章：第二段
描述2
"""
        result = self.parser.parse(outline)
        segments = self.parser.to_segment_list(result)

        assert len(segments) == 2
        assert segments[0]["id"] == 1
        assert segments[0]["title"] == "第一段"
        assert segments[1]["id"] == 2
        assert segments[1]["title"] == "第二段"

    # ===== 文件解析测试 =====

    def test_parse_file(self, tmp_path):
        """测试从文件解析"""
        outline_file = tmp_path / "outline.md"
        outline_content = """# 文件测试

## 第一章：文件内容
这是从文件读取的内容。
"""
        outline_file.write_text(outline_content, encoding="utf-8")

        result = self.parser.parse_file(outline_file)

        assert result.title == "文件测试"
        assert len(result.chapters) == 1

    # ===== 复杂场景测试 =====

    def test_parse_complex_outline(self):
        """测试复杂真实场景的大纲"""
        outline = """# Claude Code 使用教程

## 第一章：产品概述
Claude Code 是 Anthropic 官方推出的 CLI 工具，专为软件工程任务设计。
本节介绍产品定位和核心功能。

## 第2章：安装配置
详细介绍如何安装 Claude Code，包括环境配置、API Key 设置等。

## 第三章：基础用法
学习基本的命令使用，包括 /help、/plan、/tdd 等常用命令。

## 第4章：高级功能
介绍多 Agent 协作、Hook 系统、内存管理等高级特性。

## 第5章：最佳实践
总结使用经验和技巧，帮助提高开发效率。
"""
        result = self.parser.parse(outline)

        assert result.title == "Claude Code 使用教程"
        assert len(result.chapters) == 5
        assert result.chapters[0].title == "产品概述"
        assert result.chapters[1].title == "安装配置"
        assert result.chapters[4].title == "最佳实践"

        # 验证描述内容
        assert "Anthropic" in result.chapters[0].description
        assert "API Key" in result.chapters[1].description


# Hook 测试：添加此注释以触发 Stop hook
# Stop hook 会在响应完成后自动运行 pyright 检查 src/ 目录
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
