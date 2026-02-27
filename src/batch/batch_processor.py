"""
批量视频处理器

使用线程池并发处理多个视频，每个视频复用 NoteGenerator 流程。
支持中断恢复、进度回调和批量汇总报告。
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

from ..gemini_client import GeminiClient
from ..note_generator import NoteGenerator
from ..file_utils import VideoFileManager
from .task_queue import BatchTaskQueue, TaskStatus, VideoTask


class BatchProcessor:
    """批量视频笔记生成器

    支持多线程并发处理视频文件。
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        generation_mode: str = "direct",
        max_workers: int = 2,
        enable_cache: bool = True,
        output_dir: str = "outputs",
    ):
        self.api_key = api_key
        self.model = model
        self.generation_mode = generation_mode
        self.max_workers = max_workers
        self.enable_cache = enable_cache
        self.output_dir = Path(output_dir)

    def _make_batch_dir(self) -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir = self.output_dir / f"batch_{ts}"
        batch_dir.mkdir(parents=True, exist_ok=True)
        return batch_dir

    def process_files(
        self,
        video_items: List,
        progress_callback: Optional[Callable[[int, int, str, str], None]] = None,
        batch_dir: Optional[Path] = None,
    ) -> BatchTaskQueue:
        """
        批量处理视频文件列表。

        Args:
            video_items: 视频路径列表（str）或任务 dict 列表（含 path/original_name/mode）
            progress_callback: 回调函数 (done, total, video_name, message)
            batch_dir: 指定批量任务目录（恢复时传入）

        Returns:
            完成后的 BatchTaskQueue
        """
        if batch_dir is None:
            batch_dir = self._make_batch_dir()

        queue = BatchTaskQueue(batch_dir)
        queue.add_tasks(video_items)
        return self._run(queue, progress_callback)

    def resume(
        self,
        batch_dir: Path,
        progress_callback: Optional[Callable[[int, int, str, str], None]] = None,
    ) -> BatchTaskQueue:
        """恢复中断的批量任务"""
        queue = BatchTaskQueue.load(batch_dir)
        return self._run(queue, progress_callback)

    def _run(
        self,
        queue: BatchTaskQueue,
        progress_callback: Optional[Callable],
    ) -> BatchTaskQueue:
        pending = queue.pending_tasks()
        total = len(queue.tasks)
        done_count = total - len(pending)

        if not pending:
            return queue

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_single, task, queue): task
                for task in pending
            }

            for future in as_completed(futures):
                task = futures[future]
                done_count += 1
                video_name = Path(task.video_path).name

                try:
                    future.result()
                    msg = f"✅ 完成: {video_name}"
                except Exception as e:
                    msg = f"❌ 失败: {video_name} — {e}"

                if progress_callback:
                    progress_callback(done_count, total, video_name, msg)

        self._write_summary(queue)
        return queue

    def _process_single(self, task: VideoTask, queue: BatchTaskQueue):
        """处理单个视频任务（在线程中运行）"""
        video_path = Path(task.video_path)
        if not video_path.exists():
            queue.mark_failed(task, f"文件不存在: {task.video_path}")
            raise FileNotFoundError(task.video_path)

        queue.mark_running(task)

        # 优先使用 task 自身的 original_name，否则回退到文件名
        original_name = task.original_name or video_path.name
        # 优先使用 task 自身的 mode，否则回退到全局默认
        mode = task.mode or self.generation_mode

        try:
            client = GeminiClient(api_key=self.api_key)
            client.model = self.model

            file_manager = VideoFileManager(str(self.output_dir))

            # 检查是否已有最终笔记（跳过）
            if self.enable_cache:
                video_dir = file_manager.get_video_dir(str(video_path), original_name)
                if (video_dir / "final_notes.md").exists():
                    queue.mark_skipped(task, str(video_dir))
                    return

            generator = NoteGenerator(
                client,
                file_manager=file_manager,
                enable_cache=self.enable_cache,
            )

            video_file = client.upload_video(str(video_path))

            try:
                video_dir = file_manager.get_video_dir(str(video_path), original_name)
                generator.current_video_dir = video_dir

                generator.generate_all_notes(
                    video_file,
                    video_path=str(video_path),
                    original_name=original_name,
                    mode=mode,
                )
            finally:
                try:
                    if video_file.name is not None:
                        client.delete_file(video_file.name)
                except Exception:
                    pass

            queue.mark_done(task, str(video_dir))

        except Exception as e:
            queue.mark_failed(task, str(e))
            raise

    def _write_summary(self, queue: BatchTaskQueue):
        """生成 batch_summary.md 汇总报告"""
        lines = [
            f"# 批量处理汇总 — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "| 视频文件 | 状态 | 笔记 |",
            "|---------|------|------|",
        ]

        for task in queue.tasks:
            name = Path(task.video_path).name
            if task.status == TaskStatus.DONE:
                rel = Path(task.output_dir).name if task.output_dir else "-"
                lines.append(f"| {name} | ✅ 完成 | [{rel}](./{rel}/final_notes.md) |")
            elif task.status == TaskStatus.SKIPPED:
                rel = Path(task.output_dir).name if task.output_dir else "-"
                lines.append(
                    f"| {name} | ⏭️ 跳过（已缓存） | [{rel}](./{rel}/final_notes.md) |"
                )
            elif task.status == TaskStatus.FAILED:
                lines.append(f"| {name} | ❌ 失败 | {task.error or ''} |")
            else:
                lines.append(f"| {name} | ⏳ 未完成 | - |")

        s = queue.summary
        lines += [
            "",
            f"**合计**: 共 {s['total']} 个，完成 {s['done']}，跳过 {s['skipped']}，失败 {s['failed']}",
        ]

        summary_path = queue.batch_dir / "batch_summary.md"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
