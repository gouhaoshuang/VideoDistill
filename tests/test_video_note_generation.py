"""
VideoDistill 测试脚本

测试视频笔记生成功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gemini_client import GeminiClient
from src.note_generator import NoteGenerator


def test_video_note_generation():
    """测试视频笔记生成功能"""

    # 测试视频路径
    video_path = r"C:\Users\tianyi\Downloads\Claude_Code+Tmux,并行跑Agent军团.mp4"

    print("=" * 60)
    print("VideoDistill - 视频笔记生成测试")
    print("=" * 60)

    # 检查视频文件是否存在
    if not os.path.exists(video_path):
        print("\n❌ 错误: 视频文件不存在")
        print(f"   路径: {video_path}")
        return False

    print(f"\n📹 视频文件: {os.path.basename(video_path)}")
    print(f"   文件大小: {os.path.getsize(video_path) / 1024 / 1024:.2f} MB")

    # API Key - 从环境变量获取，不再使用硬编码
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n❌ 错误: 未设置 GOOGLE_API_KEY 环境变量")
        print("   请设置: set GOOGLE_API_KEY=your_api_key_here")
        return False
    print(f"\n🔑 API Key: {api_key[:15]}...{api_key[-6:]}")

    try:
        # 初始化客户端
        print("\n" + "=" * 60)
        print("步骤 1/4: 初始化 Gemini 客户端")
        print("=" * 60)

        client = GeminiClient(api_key=api_key)
        print("✅ 客户端初始化成功")

        # 上传视频
        print("\n" + "=" * 60)
        print("步骤 2/4: 上传视频到 Gemini Files API")
        print("=" * 60)

        video_file = client.upload_video(video_path)
        print("✅ 视频上传成功")
        print(f"   文件名: {video_file.name}")
        print(f"   URI: {video_file.uri}")

        # 创建笔记生成器
        print("\n" + "=" * 60)
        print("步骤 3/4: 生成笔记")
        print("=" * 60)

        generator = NoteGenerator(client)

        # 进度回调
        def progress_callback(current, total, message):
            progress = current / total * 100
            bar_length = 40
            filled = int(bar_length * current / total)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"\r  [{bar}] {progress:.1f}% - {message}", end="", flush=True)

        notes = generator.generate_all_notes(
            video_file, progress_callback=progress_callback
        )

        print("\n✅ 笔记生成成功！")

        # 保存笔记
        print("\n" + "=" * 60)
        print("步骤 4/4: 保存笔记")
        print("=" * 60)

        output_dir = Path(__file__).parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / "test_notes.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(notes)

        print(f"✅ 笔记已保存到: {output_path}")

        # 显示笔记预览
        print("\n" + "=" * 60)
        print("笔记预览 (前 500 字符)")
        print("=" * 60)
        print(notes[:500] + "..." if len(notes) > 500 else notes)

        # 清理
        print("\n" + "=" * 60)
        print("清理资源")
        print("=" * 60)

        client.delete_file(video_file.name)
        print("✅ 已删除上传的视频文件")

        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_simple_api_call():
    """测试简单的 API 调用"""

    print("=" * 60)
    print("VideoDistill - API 连接测试")
    print("=" * 60)

    # API Key - 从环境变量获取，不再使用硬编码
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n❌ 错误: 未设置 GOOGLE_API_KEY 环境变量")
        print("   请设置: set GOOGLE_API_KEY=your_api_key_here")
        return False

    try:
        client = GeminiClient(api_key=api_key)
        print("✅ 客户端初始化成功")

        # 测试简单的文本生成
        print("\n正在测试文本生成...")
        response = client.generate_content("请用一句话介绍 Gemini AI", temperature=0.7)
        print(f"✅ API 响应: {response[:100]}...")

        return True

    except Exception as e:
        print(f"❌ API 测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="VideoDistill 测试脚本")
    parser.add_argument(
        "--test",
        choices=["api", "video"],
        default="api",
        help="测试类型: api (API连接测试) 或 video (视频笔记生成测试)",
    )

    args = parser.parse_args()

    if args.test == "api":
        success = test_simple_api_call()
    else:
        success = test_video_note_generation()

    sys.exit(0 if success else 1)
