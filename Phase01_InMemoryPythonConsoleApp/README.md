# Todo CLI Application

A robust, type-safe Python Todo application built with Typer and Rich. This is **Phase 1: In-Memory Python Console App**, implemented following Spec-Driven Development (SDD) principles.

---

![App Screenshot](assets/App%20screenshot.png)

---


## Features (Basic CRUD - Completed)

- **Add Tasks**: Capture todos with titles (1-100 chars) and optional descriptions (0-500 chars).
- **View Tasks**: Display tasks in a formatted table with status indicators (✓ for complete, ○ for incomplete).
- **Mark Complete/Incomplete**: Toggle status or explicitly mark tasks as complete/incomplete.
- **Update Tasks**: Refine titles and descriptions of existing tasks.
- **Delete Tasks**: Remove tasks permanently (with confirmation).
- **Interactive Menu**: User-friendly numbered menu for easy navigation.
- **Typer CLI**: Support for dedicated commands (e.g., `todo add`, `todo list`).

## Tech Stack

- **Python 3.13+**
- **Typer**: CLI application framework.
- **Rich**: Formatted console output and tables.
- **UV**: Fast Python package and project manager.
- **Pytest**: Comprehensive unit and CLI testing.
- **Mypy**: Strict static type checking.
- **Ruff**: Fast linting and formatting.

## Project Structure

```text
.
├── history/                # Prompt History Records (PHRs) for SDD
│   └── prompts/
│       ├── basic-crud/     # History for CRUD feature implementation
│       └── constitution/   # History for project principles
├── img/                    # Project screenshots and assets
├── specs/                  # SDD Design Artifacts
│   └── basic-crud/        # Specs, plans, and tasks for CRUD
├── src/                    # Source code
│   └── todo/               # Core application package
│       ├── cli/            # CLI layer (Typer commands)
│       │   └── views/      # Rich formatted console views
│       ├── models/         # Data models (Task entity)
│       ├── services/       # Business logic (TaskService)
│       └── storage/        # In-memory storage (TaskStore)
├── tests/                  # Test suite
│   ├── cli/                # Functional tests for CLI commands
│   └── unit/               # Unit tests for core logic
├── CLAUDE.md               # Project-specific AI rules
├── main.py                 # Application entry point
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # Project documentation
└── uv.lock                 # Reproducible dependency lockfile
```

## Getting Started

### Installation

Ensure you have [uv](https://github.com/astral-sh/uv) installed.

```bash
# Install dependencies
uv sync
```

### Usage

Run the main interactive menu (default):

```bash
uv run main.py
```
or

```bash
uv run python main.py menu
```

Or use specific commands:

```bash
uv run main.py list
uv run main.py add "Buy groceries" --description "Milk, Eggs, Bread"
uv run main.py toggle 1
uv run main.py delete 1
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src
```

### Quality Assurance

```bash
# Linting
uv run ruff check src/

# Type Checking
uv run mypy src/todo/
```

## Spec-Driven Development (SDD)

This project follows a strict SDD workflow. Artifacts can be found in the `specs/` directory:
- `spec.md`: Feature requirements and user stories.
- `plan.md`: Architectural design and implementation strategy.
- `tasks.md`: Detailed testable tasks.

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
