"""
批量处理 CLI 入口

用法:
  python -m src.batch.batch_main --input videos/ --mode direct
  python -m src.batch.batch_main --input a.mp4 b.mp4 c.mp4
  python -m src.batch.batch_main --resume outputs/batch_20260225_120000
"""

import argparse
import os
import sys
from pathlib import Path

# 确保项目根目录在 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.batch.batch_processor import BatchProcessor
from config import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    DEFAULT_GENERATION_MODE,
    GENERATION_MODES,
    SUPPORTED_VIDEO_FORMATS,
)


def collect_videos(inputs: list[str]) -> list[str]:
    """从路径列表收集视频文件（支持目录和单文件）"""
    videos = []
    for inp in inputs:
        p = Path(inp)
        if p.is_dir():
            for fmt in SUPPORTED_VIDEO_FORMATS:
                videos.extend(str(f) for f in sorted(p.glob(f"*.{fmt}")))
        elif p.is_file():
            videos.append(str(p))
        else:
            print(f"⚠️  跳过不存在的路径: {inp}")
    return videos


def main():
    parser = argparse.ArgumentParser(
        description="VideoDistill 批量视频笔记生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理目录下所有视频
  python -m src.batch.batch_main --input videos/

  # 处理指定文件
  python -m src.batch.batch_main --input a.mp4 b.mp4

  # 恢复中断的批量任务
  python -m src.batch.batch_main --resume outputs/batch_20260225_120000
        """,
    )

    parser.add_argument(
        "--input",
        "-i",
        nargs="+",
        metavar="PATH",
        help="视频文件或目录（可多个）",
    )
    parser.add_argument(
        "--resume",
        metavar="BATCH_DIR",
        help="恢复中断的批量任务目录",
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=list(GENERATION_MODES.keys()),
        default=DEFAULT_GENERATION_MODE,
        help=f"生成模式（默认: {DEFAULT_GENERATION_MODE}）",
    )
    parser.add_argument(
        "--model",
        choices=AVAILABLE_MODELS,
        default=DEFAULT_MODEL,
        help=f"AI 模型（默认: {DEFAULT_MODEL}）",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=2,
        help="并发线程数（默认: 2）",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="outputs",
        help="输出根目录（默认: outputs）",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="禁用缓存，强制重新生成",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("GOOGLE_API_KEY", ""),
        help="Google API Key（默认读取环境变量 GOOGLE_API_KEY）",
    )

    args = parser.parse_args()

    # 验证参数
    if not args.input and not args.resume:
        parser.error("请指定 --input 或 --resume")

    if not args.api_key:
        parser.error("请设置 GOOGLE_API_KEY 环境变量或通过 --api-key 传入")

    processor = BatchProcessor(
        api_key=args.api_key,
        model=args.model,
        generation_mode=args.mode,
        max_workers=args.workers,
        enable_cache=not args.no_cache,
        output_dir=args.output,
    )

    def on_progress(done: int, total: int, name: str, msg: str):
        print(f"[{done}/{total}] {msg}")

    if args.resume:
        batch_dir = Path(args.resume)
        print(f"▶ 恢复批量任务: {batch_dir}")
        queue = processor.resume(batch_dir, progress_callback=on_progress)
    else:
        videos = collect_videos(args.input)
        if not videos:
            print("❌ 未找到任何视频文件")
            sys.exit(1)

        print(
            f"▶ 开始批量处理 {len(videos)} 个视频（模式: {GENERATION_MODES[args.mode]}，并发: {args.workers}）"
        )
        for v in videos:
            print(f"   • {v}")
        print()

        queue = processor.process_files(videos, progress_callback=on_progress)

    s = queue.summary
    print(f"\n{'='*50}")
    print(f"批量处理完成: 共 {s['total']} 个")
    print(f"  ✅ 完成: {s['done']}  ⏭️ 跳过: {s['skipped']}  ❌ 失败: {s['failed']}")
    print(f"  汇总报告: {queue.batch_dir / 'batch_summary.md'}")

    if s["failed"] > 0:
        print("\n失败任务:")
        for t in queue.tasks:
            from src.batch.task_queue import TaskStatus

            if t.status == TaskStatus.FAILED:
                print(f"  ❌ {Path(t.video_path).name}: {t.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
