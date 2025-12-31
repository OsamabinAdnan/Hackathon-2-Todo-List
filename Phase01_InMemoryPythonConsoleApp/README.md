# Phase 1: In-Memory Python Console Todo App

A robust, type-safe Python CLI application built with Typer and Rich, implementing a full-featured task management system with **no persistent storage** - all data lives in memory during runtime.

---

![App Screenshot](assets/App%20screenshot.png)

---

## Implementation Status

**Phase 1** progresses through 3 complexity levels:

- ✅ **Level 1 - Basic**: Core CRUD operations (Add, View, Update, Delete, Toggle)
- ✅ **Level 2 - Intermediate**: Priorities, Tags, Filtering, Search, Sorting
- ✅ **Level 3 - Advanced**: Recurring tasks, DateTime precision, Smart reminders

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

### Level 3 - Intelligent Task Management (✅ Completed)

- **🔁 Recurring Tasks**: Tasks that automatically reschedule when completed
  - **Patterns**: DAILY, WEEKLY, MONTHLY with shorthand input (d/w/m)
  - **Edge Case Handling**: Monthly tasks handle Feb 29, Jan 31 → Feb 28, and year boundaries
  - **Auto-Rescheduling**: Complete a recurring task, get a new instance for the next occurrence
  - **Validation**: Recurring tasks must have a due date

- **📅 DateTime Precision**: Specific due dates with time support
  - **Formats**: `YYYY-MM-DD HH:MM` (e.g., "2025-01-15 14:30") or `YYYY-MM-DD` (defaults to 00:00)
  - **Future Validation**: Rejects past datetimes with clear error messages
  - **Time Display**: Shows time when not midnight, date-only for 00:00 (backward compatibility)
  - **Accurate Sorting**: Sorts by complete datetime, not just date

- **⏰ Smart Reminders**: Proactive console notifications
  - **Overdue Detection**: Tasks past their due datetime (red styling with ⚠️ indicator)
  - **Due Soon**: Tasks due within 60 minutes (yellow styling with ⏰ indicator)
  - **Humanized Time**: "2 hours overdue", "due in 30 min", "1 day overdue"
  - **Date-Only Exclusion**: Tasks with time=00:00 excluded from reminders (no nagging for deadlines without specific times)
  - **Rich Panel Display**: Reminders shown at app startup and after list/search/filter commands

---

## Screenshots

### Main Menu & Task Management

**Interactive Menu**

![App Screenshot](assets/App%20screenshot.png)

**Adding Tasks with Priority, Tags, Due Date & Recurrence**

![Add New Task](assets/Add%20New%20Task.png)

**List All Tasks - Rich Table Display**

![List Tasks](assets/List%20Tasks.png)

### Level 2 Features

**Filter Tasks by Status, Priority, or Tags**

![Filter Tasks](assets/Filter%20Tasks.png)

**Sort Tasks by Priority, Date, Title, or Due Date**

![Sort Tasks](assets/Sort%20Tasks.png)

**Search Tasks by Keywords**

![Search Tasks](assets/Search%20Tasks%20by%20KWs%20in%20title%20and%20description.png)

**Update Task Details**

![Update Tasks](assets/Update%20Tasks.png)

**Toggle Task Status**

![Toggle Task](assets/Toggle%20task%20as%20completed.png)

**Delete Task by ID**

![Delete Task](assets/Delete%20task%20using%20ID.png)

### Level 3 Features

**Recurring Task Auto-Rescheduling**

When you complete a recurring task, a new instance is automatically created for the next occurrence:

![Recurring Task Reschedule](assets/due%20to%20toggled%20recurring%20task%2C%20it%20rescheduled.png)

**Smart Reminders - Due Soon Notification**

Reminders appear automatically for tasks that are overdue or due within 60 minutes:

![Reminder Panel](assets/Reminder%20when%20task%20about%20to%20due.png)

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
  --due "2026-01-20 15:00" \
  --description "Deploy v2.0 release"

# Add a recurring weekly meeting
uv run main.py add "Team Standup" \
  --due "2025-01-06 09:00" \
  --recurring weekly \
  --priority high

# List incomplete high-priority tasks sorted by due date
uv run main.py list --status todo --priority high --sort due_date

# Search for tasks containing "meeting"
uv run main.py search "meeting" --priority high

# Update task with new due date and recurrence
uv run main.py update 3 \
  --title "Updated title" \
  --priority medium \
  --due "2025-02-01 14:30" \
  --recurring monthly

# Toggle task completion (auto-reschedules recurring tasks)
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
│   ├── advanced-features/  # Level 3 development logs
│   └── constitution/       # Project principles logs
├── specs/                  # Design artifacts
│   ├── basic-crud/
│   │   ├── spec.md         # Requirements & user stories
│   │   ├── plan.md         # Architecture decisions
│   │   └── tasks.md        # Implementation roadmap
│   ├── intermediate-features/
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   └── checklists/     # Quality validation
│   └── advanced-features/
│       ├── spec.md         # Level 3: Recurring, DateTime, Reminders
│       ├── plan.md         # Architecture for intelligent features
│       └── tasks.md        # 132 implementation tasks
├── src/todo/               # Application code
│   ├── cli/views/          # Console UI (formatters, menu)
│   ├── models/             # Data models (Task, Priority, Recurrence)
│   ├── services/           # Business logic (TaskService, results)
│   └── storage/            # In-memory storage (TaskStore)
├── tests/
│   └── unit/               # Unit tests
│       ├── test_datetime.py    # 21 datetime tests
│       ├── test_recurrence.py  # 16 recurrence tests
│       └── test_reminders.py   # 17 reminder tests
├── assets/                 # Screenshots and media
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

## Level 3 Usage Examples

### Recurring Tasks

```bash
# Add a daily gym reminder at 7 AM
uv run main.py add "Morning Gym" --due "2025-01-02 07:00" --recurring daily

# Add a weekly team meeting every Monday at 10 AM
uv run main.py add "Weekly Standup" --due "2025-01-06 10:00" --recurring weekly

# Add a monthly report due on the 15th at 2 PM
uv run main.py add "Monthly Report" --due "2025-02-15 14:00" --recurring monthly

# When you complete task 1 (daily recurring), task 6 is auto-created for next day
uv run main.py toggle 1
# Output: Task 1 marked complete.
#         New recurring instance created: 6 - Morning Gym
```

### DateTime Precision

```bash
# Task with specific time (will trigger reminders)
uv run main.py add "Doctor Appointment" --due "2025-01-15 14:30"

# Date-only task (won't trigger time-based reminders)
uv run main.py add "Project Deadline" --due "2025-01-20"

# Past dates are rejected
uv run main.py add "Old Task" --due "2024-12-01 10:00"
# Error: Error: Due date cannot be in the past
```

### Smart Reminders

Reminders appear automatically when you:
- Launch the app (if overdue or due-soon tasks exist)
- List, filter, or search tasks

Example reminder panel:
```
╭─────────────────────────────────── 📋 Reminders ───────────────────────────────────╮
│                                                                                     │
│ ⚠️  2 Overdue Tasks                                                                 │
│   • Task 3: Doctor Appointment (2 hours overdue)                                   │
│   • Task 5: Submit Report (1 day overdue)                                          │
│                                                                                     │
│ ⏰ 1 Due Soon                                                                       │
│   • Task 7: Team Meeting (due in 30 min)                                           │
│                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────╯
```

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
