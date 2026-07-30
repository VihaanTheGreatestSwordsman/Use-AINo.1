# todo — simple Python CLI to-do list

A small, dependency-free Python 3.8+ command-line application to manage a simple to-do list persisted to JSON.

Features
- Add, list, complete, delete, clear, find tasks
- Persisted to `data/todos.json`
- Atomic writes to avoid simple race problems
- Tests with pytest
- GitHub Actions workflow included

Installation
- No installation required. Uses only the Python standard library (3.8+).

Usage examples
- Add a task:
  python main.py add "Buy milk"

- List tasks:
  python main.py list

- Mark a task complete:
  python main.py complete 1

- Add another:
  python main.py add "Write report"

- Delete a task:
  python main.py delete 1

- Clear all tasks:
  python main.py clear

- Find tasks:
  python main.py find "report"

- Export tasks:
  python main.py export backup.json

- Import tasks:
  python main.py import backup.json

Storage format
- By default tasks are stored in `data/todos.json` with this structure:
  {
    "next_id": <int>,
    "tasks": [ { id, text, created_at, completed, completed_at }, ... ]
  }

Running tests locally
- Ensure pytest is installed (pip install pytest)
- From repository root run:
  python -m pytest

GitHub Actions
- Tests run automatically on push and pull requests using Python 3.8–3.11 (see `.github/workflows/python-app.yml`).

Acceptance tests you can run manually
1. python main.py add "Buy milk"
   - python main.py list
     - Expected: "1. [ ] Buy milk"

2. python main.py complete 1
   - python main.py list
     - Expected: "1. [x] Buy milk"

3. python main.py add "Write report"
   - python main.py list
     - Expected: both items with stable IDs

4. python main.py delete 1
   - python main.py list
     - Expected: only task 2 remains

5. python main.py clear
   - python main.py list
     - Expected: "No tasks."

Notes
- No third-party packages are used.
- CLI returns non-zero exit codes on error (2: not found, 3: invalid input, 4: file error, 99: unexpected).
- The storage file is created automatically if missing.
