# Phase 1: In-Memory Python Console Todo App

A robust, type-safe Python CLI application built with Typer and Rich, implementing a full-featured task management system with **no persistent storage** - all data lives in memory during runtime.

---

![App Screenshot](assets/App%20screenshot.png)

---

## Implementation Status

**Phase 1** progresses through 3 complexity levels:

- ✅ **Level 1 - Basic**: Core CRUD operations (Add, View, Update, Delete, Toggle)
- ✅ **Level 2 - Intermediate**: Priorities, Tags, Filtering, Search, Sorting
- ⏳ **Level 3 - Advanced**: Recurring tasks, Due dates automation, Reminders (Coming Soon)

---

## Features

### Level 1 - Essential Operations (✅ Completed)

- **Add Tasks**: Create tasks with titles (1-100 chars) and descriptions (0-500 chars)
- **View All Tasks**: Display tasks in Rich-formatted tables with status indicators
- **Update Tasks**: Modify task titles and descriptions
- **Delete Tasks**: Permanently remove tasks (with confirmation)
- **Toggle Status**: Mark tasks as complete (✓) or incomplete (○)
- **Interactive Menu**: Numbered menu system for easy navigation

### Level 2 - Organization & Usability (✅ Completed)

- **Priority Levels**: HIGH (Red), MEDIUM (Yellow), LOW (Green), NONE with color-coding
- **Multi-Tag Support**: Categorize tasks with comma-separated tags (max 20 chars each)
- **Advanced Filtering**: Filter by status (todo/done), priority, or tags with ANY-match logic
- **Keyword Search**: Case-insensitive search across task titles and descriptions
- **Multi-Criteria Sorting**: Sort by Priority, Created Date, Title, or Due Date
  - Smart secondary sorting (e.g., Priority → Due Date → Title)
- **Due Date Management**: Assign future due dates with validation (YYYY-MM-DD format)
- **Enhanced Menu**: 10 options (0-9) including dedicated Filter, Sort, Search, and Help
- **Shorthand Inputs**: Quick commands (h/m/l/n for priority, cd/p/t/dd for sort)

---

## Installation

### Prerequisites

- Python 3.13+ ([Download](https://www.python.org/downloads/))
- Git ([Download](https://git-scm.com/downloads))
- UV Package Manager ([Install UV](https://github.com/astral-sh/uv)) - Recommended

### Setup Instructions

**1. Clone the Repository**

```bash
git clone https://github.com/OsamabinAdnan/Hackathon-2-Todo-List.git
cd Hackathon-2-Todo-List/Phase01_InMemoryPythonConsoleApp
```

**2. Install Dependencies**

Using UV (recommended):
```bash
uv sync
```

Alternative using pip:
```bash
pip install typer rich pytest pytest-cov mypy ruff
```

**3. Launch the App**

```bash
# Interactive menu (default)
uv run main.py

# Or with Python directly
python main.py
```

---

## Usage

### Interactive Menu

The menu provides guided workflows for all operations:

```bash
uv run main.py
```

**Available Options:**
```
1. Add Task - Create with priority & tags
2. List Tasks - Show all tasks (no filters)
3. Filter Tasks - Filter by status, priority, or tags
4. Sort Tasks - Reorder by date, priority, or title
5. Search Tasks - Find by keyword in title/description
6. Update Task - Edit details & attributes
7. Delete Task - Remove task permanently
8. Toggle Status - Mark complete/incomplete
9. Quit - Exit application
0. Help - View all available commands
```

**Shorthand Tips:**
- **Priorities**: Type `h`, `m`, `l`, or `n` (case-insensitive)
- **Status Filters**: Type `a`, `t`, or `d`
- **Sort Keys**: Type `cd`, `p`, `t`, or `dd`

### Direct CLI Commands

For automation and scripting:

```bash
# Add a high-priority task with tags and due date
uv run main.py add "Deploy to production" \
  --priority high \
  --tags "work,devops" \
  --due 2026-01-20 \
  --description "Deploy v2.0 release"

# List incomplete high-priority tasks sorted by due date
uv run main.py list --status todo --priority high --sort due_date

# Search for tasks containing "meeting"
uv run main.py search "meeting" --priority high

# Update task attributes
uv run main.py update 3 --title "Updated title" --priority medium

# Toggle task completion
uv run main.py toggle 1

# Delete a task
uv run main.py delete 2

# View all available commands
uv run main.py --help
```

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.13+** | Modern Python with enhanced type system |
| **Typer** | CLI framework with automatic help generation |
| **Rich** | Terminal output styling, tables, and colors |
| **UV** | Fast Python package and project manager |
| **Pytest** | Testing framework with coverage reporting |
| **Mypy** | Static type checking (strict mode) |
| **Ruff** | Fast linting and code formatting |

---

## Project Structure

```text
.
├── .claude/                # AI agents and skills
├── .specify/               # SDD framework
│   ├── memory/             # Project constitution
│   ├── templates/          # Spec templates
│   └── scripts/            # Automation scripts
├── history/prompts/        # Prompt History Records (PHRs)
│   ├── basic-crud/         # Level 1 development logs
│   ├── intermediate-features/ # Level 2 development logs
│   └── constitution/       # Project principles logs
├── specs/                  # Design artifacts
│   ├── basic-crud/
│   │   ├── spec.md         # Requirements & user stories
│   │   ├── plan.md         # Architecture decisions
│   │   └── tasks.md        # Implementation roadmap
│   └── intermediate-features/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       └── checklists/     # Quality validation
├── src/todo/               # Application code
│   ├── cli/views/          # Console UI (formatters, menu)
│   ├── models/             # Data models (Task, Priority)
│   ├── services/           # Business logic (TaskService)
│   └── storage/            # In-memory storage (TaskStore)
├── tests/
│   ├── unit/               # Unit tests
│   └── cli/                # CLI integration tests
├── main.py                 # Entry point
├── pyproject.toml          # Project config
└── README.md               # This file
```

---

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=html

# Run specific test suite
uv run pytest tests/unit/
uv run pytest tests/cli/
```

### Code Quality

```bash
# Linting
uv run ruff check src/

# Auto-fix linting issues
uv run ruff check --fix src/

# Type checking
uv run mypy src/todo/

# Format code
uv run ruff format src/
```

### Quality Gate (All must pass)

```bash
uv run ruff check src/ && \
uv run mypy src/todo/ && \
uv run pytest --cov=src
```

---

## Spec-Driven Development (SDD)

This project demonstrates **Spec-Driven Development**, where all features are:
1. Specified in `spec.md` (requirements & user stories)
2. Planned in `plan.md` (architecture & decisions)
3. Broken down in `tasks.md` (implementation steps)
4. Implemented by AI agents (Claude Code)
5. Documented in PHRs (`history/prompts/`)

**SDD Workflow:**
```
/sp.specify → /sp.clarify → /sp.plan → /sp.tasks → /sp.analyze → /sp.implement
```

All artifacts live in `specs/{feature}/` directories.

---

## What's Next?

**Level 3 - Advanced Features** (Upcoming)
- ⏳ Recurring tasks (daily, weekly, monthly patterns)
- ⏳ Smart due date handling and overdue detection
- ⏳ Reminder notifications

---

## Architecture Principles

This project follows strict principles defined in `.specify/memory/constitution.md`:

- **Spec-Driven**: All code generated from approved specifications
- **Type-Safe**: Strict type hints throughout (Mypy strict mode)
- **Clean Architecture**: Separation of Models, Services, Storage, and CLI
- **Test-First**: 100% coverage for core business logic
- **No Manual Code**: All implementation by Claude Code agents

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
