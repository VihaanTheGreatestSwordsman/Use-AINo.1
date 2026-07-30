"""Command-line interface for the todo app using argparse."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional
from .core import TodoList


def _print_task(t: dict) -> None:
    status = "x" if t.get("completed") else " "
    print(f"{t.get('id')}. [{status}] {t.get('text')}")


def create_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="todo", description="Simple todo list CLI")
    p.add_argument("--data", "-d", default="data/todos.json", help="Path to JSON storage file")

    sub = p.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Add a new task")
    add.add_argument("text", help="Task text")

    lst = sub.add_parser("list", help="List tasks")
    lst.add_argument("--show-completed", action="store_true", help="Show completed tasks as well")

    comp = sub.add_parser("complete", help="Mark a task complete")
    comp.add_argument("id", type=int, help="ID of task to complete")

    delete = sub.add_parser("delete", help="Delete a task")
    delete.add_argument("id", type=int, help="ID of task to delete")

    clear = sub.add_parser("clear", help="Clear all tasks")

    find = sub.add_parser("find", help="Find tasks containing a query")
    find.add_argument("query", help="Search query")

    export = sub.add_parser("export", help="Export tasks to a JSON file")
    export.add_argument("path", help="Destination file path")

    imp = sub.add_parser("import", help="Import tasks from a JSON file")
    imp.add_argument("path", help="Source file path")

    return p


def main(argv: Optional[List[str]] = None) -> int:
    """Parse argv and run the requested command. Returns exit code (0 success)."""
    parser = create_parser()
    args = parser.parse_args(argv)
    todo = TodoList(storage_path=Path(args.data))

    try:
        if args.command == "add":
            task = todo.add_task(args.text)
            print("Added task:")
            _print_task(task)
            return 0

        if args.command == "list":
            tasks = todo.list_tasks(show_completed=args.show_completed)
            if not tasks:
                print("No tasks.")
                return 0
            for t in tasks:
                _print_task(t)
            return 0

        if args.command == "complete":
            updated = todo.complete_task(args.id)
            print("Marked complete:")
            _print_task(updated)
            return 0

        if args.command == "delete":
            todo.delete_task(args.id)
            print(f"Deleted task {args.id}.")
            return 0

        if args.command == "clear":
            todo.clear_tasks()
            print("All tasks cleared.")
            return 0

        if args.command == "find":
            results = todo.find_tasks(args.query)
            if not results:
                print("No matching tasks.")
                return 0
            for t in results:
                _print_task(t)
            return 0

        if args.command == "export":
            todo.export_json(args.path)
            print(f"Exported tasks to {args.path}")
            return 0

        if args.command == "import":
            todo.import_json(args.path)
            print(f"Imported tasks from {args.path}")
            return 0

        parser.print_help()
        return 1
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"Invalid input: {e}", file=sys.stderr)
        return 3
    except FileNotFoundError as e:
        print(f"File error: {e}", file=sys.stderr)
        return 4
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 99
