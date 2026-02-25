"""
批量任务队列与状态管理

负责维护每个视频任务的状态，并持久化到 batch_status.json，支持中断恢复。
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional


class TaskStatus(str, Enum):
    PENDING = "pending"    # 等待处理
    RUNNING = "running"    # 处理中
    DONE = "done"          # 完成
    FAILED = "failed"      # 失败（可重试）
    SKIPPED = "skipped"    # 跳过（已有缓存）


@dataclass
class VideoTask:
    video_path: str
    original_name: Optional[str] = None   # 原始中文文件名
    mode: str = "direct"                   # 生成模式: direct | segmented
    status: TaskStatus = TaskStatus.PENDING
    output_dir: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "VideoTask":
        d = d.copy()
        d["status"] = TaskStatus(d["status"])
        return cls(**d)


class BatchTaskQueue:
    """批量任务队列，负责状态持久化和恢复"""

    STATUS_FILE = "batch_status.json"

    def __init__(self, batch_dir: Path):
        self.batch_dir = batch_dir
        self.batch_dir.mkdir(parents=True, exist_ok=True)
        self.tasks: List[VideoTask] = []
        self._status_path = batch_dir / self.STATUS_FILE

    def add_tasks(self, video_items: List):
        """添加视频任务列表，支持 str 或 dict(path, original_name, mode)"""
        for item in video_items:
            if isinstance(item, dict):
                self.tasks.append(VideoTask(
                    video_path=item["path"],
                    original_name=item.get("original_name"),
                    mode=item.get("mode", "direct"),
                ))
            else:
                self.tasks.append(VideoTask(video_path=item))
        self.save()

    def save(self):
        """持久化任务状态到 JSON"""
        data = {
            "batch_dir": str(self.batch_dir),
            "created_at": datetime.now().isoformat(),
            "total": len(self.tasks),
            "done": sum(1 for t in self.tasks if t.status == TaskStatus.DONE),
            "failed": sum(1 for t in self.tasks if t.status == TaskStatus.FAILED),
            "tasks": [t.to_dict() for t in self.tasks],
        }
        with open(self._status_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, batch_dir: Path) -> "BatchTaskQueue":
        """从已有 batch_status.json 恢复队列"""
        queue = cls(batch_dir)
        status_path = batch_dir / cls.STATUS_FILE
        if not status_path.exists():
            raise FileNotFoundError(f"找不到状态文件: {status_path}")
        with open(status_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        queue.tasks = [VideoTask.from_dict(t) for t in data["tasks"]]
        # 将上次中断时 RUNNING 的任务重置为 PENDING
        for task in queue.tasks:
            if task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.PENDING
                task.started_at = None
        return queue

    def pending_tasks(self) -> List[VideoTask]:
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]

    def mark_running(self, task: VideoTask):
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        self.save()

    def mark_done(self, task: VideoTask, output_dir: str):
        task.status = TaskStatus.DONE
        task.output_dir = output_dir
        task.finished_at = datetime.now().isoformat()
        self.save()

    def mark_failed(self, task: VideoTask, error: str):
        task.status = TaskStatus.FAILED
        task.error = error
        task.finished_at = datetime.now().isoformat()
        self.save()

    def mark_skipped(self, task: VideoTask, output_dir: str):
        task.status = TaskStatus.SKIPPED
        task.output_dir = output_dir
        task.finished_at = datetime.now().isoformat()
        self.save()

    @property
    def summary(self) -> dict:
        return {
            "total": len(self.tasks),
            "done": sum(1 for t in self.tasks if t.status == TaskStatus.DONE),
            "skipped": sum(1 for t in self.tasks if t.status == TaskStatus.SKIPPED),
            "failed": sum(1 for t in self.tasks if t.status == TaskStatus.FAILED),
            "pending": sum(1 for t in self.tasks if t.status == TaskStatus.PENDING),
        }
