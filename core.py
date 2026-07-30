"""Core TodoList implementation.

Provides a TodoList class for managing tasks persisted to a JSON file.
No external dependencies; uses the standard library only.
"""

from __future__ import annotations

import json
import tempfile
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Union


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string (UTC, no microseconds)."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class TodoList:
    """A simple to-do list manager persisted to a JSON file.

    The JSON structure:
    {
        "next_id": <int>,
        "tasks": [ {task}, ... ]
    }

    Each task:
    {
        "id": int,
        "text": str,
        "created_at": str (ISO 8601),
        "completed": bool,
        "completed_at": Optional[str]
    }
    """

    def __init__(self, storage_path: Union[str, Path] = "data/todos.json") -> None:
        self.path = Path(storage_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._data: Dict[str, Any] = {"next_id": 1, "tasks": []}
            self._save()
        else:
            self._load()

    def _load(self) -> None:
        with self.path.open("r", encoding="utf-8") as fh:
            self._data = json.load(fh)
        # Basic validation and defaults
        if "next_id" not in self._data:
            self._data["next_id"] = 1
        if "tasks" not in self._data:
            self._data["tasks"] = []

    def _save(self) -> None:
        """Atomically write the current data to the storage file."""
        dirpath = self.path.parent
        fd, tmp_path = tempfile.mkstemp(dir=dirpath)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2, ensure_ascii=False)
            # Atomic replace
            os.replace(tmp_path, str(self.path))
        except Exception:
            # Ensure temp file cleaned up on failure
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            raise

    def add_task(self, text: str) -> Dict[str, Any]:
        """Add a new task with the provided text. Returns the task dict."""
        if not text or not text.strip():
            raise ValueError("Task text must be a non-empty string.")
        task_id = int(self._data["next_id"])
        task = {
            "id": task_id,
            "text": text.strip(),
            "created_at": _now_iso(),
            "completed": False,
            "completed_at": None,
        }
        self._data["tasks"].append(task)
        self._data["next_id"] = task_id + 1
        self._save()
        return task

    def list_tasks(self, show_completed: bool = False) -> List[Dict[str, Any]]:
        """Return tasks, optionally including completed tasks."""
        if show_completed:
            return list(self._data["tasks"])
        return [t for t in self._data["tasks"] if not t.get("completed", False)]

    def _find_index(self, task_id: int) -> int:
        for idx, t in enumerate(self._data["tasks"]):
            if int(t.get("id")) == int(task_id):
                return idx
        raise KeyError(f"Task with id {task_id} not found.")

    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """Mark a task completed and return the updated task."""
        idx = self._find_index(task_id)
        task = self._data["tasks"][idx]
        if task.get("completed"):
            # Already completed; just return it
            return task
        task["completed"] = True
        task["completed_at"] = _now_iso()
        self._save()
        return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task by id. Raises KeyError if not found."""
        idx = self._find_index(task_id)
        del self._data["tasks"][idx]
        self._save()

    def clear_tasks(self) -> None:
        """Remove all tasks. next_id is preserved to keep IDs stable."""
        self._data["tasks"] = []
        self._save()

    def find_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Find tasks whose text contains the query (case-insensitive)."""
        q = (query or "").strip().lower()
        if not q:
            return []
        return [t for t in self._data["tasks"] if q in t.get("text", "").lower()]

    def export_json(self, export_path: Union[str, Path]) -> None:
        """Export current tasks to the supplied file path (JSON)."""
        export_p = Path(export_path)
        export_p.parent.mkdir(parents=True, exist_ok=True)
        with export_p.open("w", encoding="utf-8") as fh:
            json.dump({"tasks": self._data["tasks"]}, fh, indent=2, ensure_ascii=False)

    def import_json(self, import_path: Union[str, Path]) -> None:
        """Import tasks from a JSON file. Replaces current tasks with the imported list.

        Imported file is expected to contain an object with "tasks": [ ... ].
        After import, next_id is adjusted to max(id)+1 to preserve incremental IDs.
        """
        import_p = Path(import_path)
        with import_p.open("r", encoding="utf-8") as fh:
            obj = json.load(fh)
        tasks = obj.get("tasks")
        if not isinstance(tasks, list):
            raise ValueError("Import file must contain a top-level 'tasks' array.")
        # Basic normalization/validation
        normalized = []
        max_id = 0
        for t in tasks:
            tid = int(t.get("id", 0))
            if tid <= 0:
                continue
            max_id = max(max_id, tid)
            normalized.append(
                {
                    "id": tid,
                    "text": str(t.get("text", "")).strip(),
                    "created_at": str(t.get("created_at") or _now_iso()),
                    "completed": bool(t.get("completed", False)),
                    "completed_at": t.get("completed_at"),
                }
            )
        self._data["tasks"] = normalized
        self._data["next_id"] = max(self._data.get("next_id", 1), max_id + 1)
        self._save()
