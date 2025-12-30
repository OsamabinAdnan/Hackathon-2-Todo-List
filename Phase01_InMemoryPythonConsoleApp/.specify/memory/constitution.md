<!--
SYNC IMPACT REPORT
==================
Version change: 1.1.0 -> 1.2.0
Modified principles:
  - Principle VI: Added UV Package Management (NON-NEGOTIABLE)
Modified sections:
  - Technology Standards: Added UV as exclusive package manager
  - Added Agents and Skills Architecture section
Added sections:
  - Agents and Skills Architecture
Removed sections: None

Previous changes (v1.0.0 -> v1.1.0):
  - Principle V: Changed from "Rich CLI UX" to "Textual TUI Experience"
  - Technology Standards: Typer -> Textual, added TUI-specific requirements
  - Project Structure: cli/ -> tui/, added components and screens
  - Performance Requirements: Added TUI-specific metrics
  - Added TUI Architecture Guidelines

Skills updated (PHR 003, 004):
  - modular-code-generation: DONE - Trimmed TUI patterns, now core layer only
  - runtime-state-management: DONE - Trimmed TUI patterns, references tui-reactive-state
  - All 6 testing skills: DONE - Added TUI testing patterns

Agents updated (PHR 004):
  - python-todo-architect: DONE - Added tools field, YAML list format for skills
  - testing-expert: DONE - Added tools field, YAML list format for skills
  - tui-designer: DONE - Created with 5 TUI skills

New skills created (PHR 004, 005):
  - tui-navigation-routing: DONE
  - tui-input-validation: DONE
  - tui-output-styling: DONE
  - tui-feedback-notifications: DONE
  - tui-reactive-state: DONE
  - uv-package-management: DONE

Follow-up TODOs:
  - None (all constitution changes implemented)
-->

# Phase 1 - In-Memory Python Console Todo App Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All implementation MUST be performed by Claude Code or specialized subagents based on approved specifications.

- Zero manual coding: Human developers define requirements; AI executes implementation
- Every feature follows the SDD workflow: `/sp.specify` → `/sp.plan` → `/sp.tasks` → `/sp.implement`
- All changes MUST be traceable to spec documents in `/specs/<feature>/`
- Prompt History Records (PHRs) MUST document every significant AI interaction

**Rationale**: Ensures auditability, consistency, and adherence to the "No Manual Code" audit requirement.

### II. Architecture First

Prioritize system design and type-safety over immediate implementation.

- Clean Python architecture with proper `src/` layout
- Type hints MUST be used throughout the codebase (Python 3.13+ features)
- Separation of concerns: models, services, CLI layers remain distinct
- Data models MUST be defined before implementation begins
- In-memory storage (dictionaries/lists) for Phase 1; design MUST allow future persistence swap

**Rationale**: Type-safe, well-architected code reduces bugs and enables future extensibility.

### III. Clean Code Standards

Adherence to PEP 8 standards, descriptive naming, and modular architecture.

- Follow PEP 8 formatting (enforced via linting tools)
- Meaningful, descriptive variable and function names
- Functions MUST do one thing well (Single Responsibility)
- Favor clarity and simplicity over cleverness
- No premature optimization; no premature abstraction
- F-strings MUST be used for string formatting

**Rationale**: Readable, maintainable code is easier to test, debug, and extend.

### IV. Test-First Development

100% test coverage for core CRUD logic; verified by testing workflow.

- Tests MUST be written before implementation (Red-Green-Refactor)
- Core operations (Add, Delete, Update, View, Mark Complete) require unit tests
- Test files live in `tests/` directory mirroring `src/` structure
- pytest MUST be used as the testing framework
- Tests MUST fail before implementation, pass after

**Rationale**: TDD ensures correctness and provides a safety net for refactoring.

### V. Rich CLI Experience

A full-featured Command Line Interface (CLI) using Typer and Rich frameworks.

- Use Typer framework for command structure and argument parsing
- Use Rich for styled output, tables, and formatting
- Interactive console menu system with numbered options or command-based interface
- Real-time updates to console display when state changes
- Formatted output with tables, colors, and progress indicators using Rich
- Error messages MUST be displayed in console with appropriate formatting
- Success/failure states MUST be visually distinct with color coding via Rich
- Help system MUST be accessible via `--help` flags and interactive help command

**Rationale**: A CLI provides superior user experience with clear command structure, formatted output, and familiar terminal interaction patterns.

### VI. UV Package Management (NON-NEGOTIABLE)

Exclusively use `uv` for dependency management and project initialization.

- Project MUST be initialized with `uv init`
- Dependencies MUST be managed via `uv add`/`uv remove`
- Virtual environment MUST be created via `uv venv`
- README MUST provide one-command setup: `uv sync`
- No pip, poetry, or other package managers allowed

**Rationale**: UV provides fast, reproducible dependency management aligned with modern Python practices.

## Technology Standards

| Aspect | Standard |
|--------|----------|
| **Language** | Python 3.13+ |
| **Package Manager** | UV (exclusively) |
| **CLI Framework** | Typer |
| **Styling/Formatting** | Rich |
| **Testing** | pytest |
| **Linting** | Ruff |
| **Type Checking** | pyright or mypy |
| **State Management** | In-memory (dict/list) |

### Project Structure

```text
Phase01_InMemoryPythonConsoleApp/
├── .specify/           # SpecKit Plus configuration
├── specs/              # Feature specifications
│   └── <feature>/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── main.py             # Main Typer CLI application
├── src/
│   └── todo/
│       ├── __init__.py
│       ├── models/     # Data models (Task, Priority, etc.)
│       ├── services/   # Business logic (TaskService)
│       └── storage/    # In-memory storage layer
├── tests/
│   ├── unit/
│   ├── integration/
│   └── cli/            # CLI-specific tests
├── pyproject.toml      # UV project configuration
└── README.md           # One-command setup instructions
```

### CLI Architecture Guidelines

#### Command Structure
```
main.py (Typer App)
├── add_task()        # Add new task command
├── list_tasks()      # List all tasks command
├── update_task()     # Update task command
├── delete_task()     # Delete task command
├── toggle_task()     # Toggle completion command
├── interactive_menu() # Interactive menu command
└── help_command()    # Help command
```

#### Data Flow
- Commands call service layer methods
- Services interact with storage layer
- Output is formatted using Rich and displayed to console
- State changes are immediately reflected in storage

#### User Interaction Patterns
| Command | Action |
|---------|--------|
| `add` | Add new task with title and optional description |
| `list` | List all tasks with completion status |
| `update` | Update task title and/or description |
| `delete` | Delete selected task |
| `toggle` | Mark task as complete/incomplete |
| `menu` | Interactive menu system |
| `--help` | Show help information |

### Performance Requirements

- In-memory operations MUST be near-instantaneous (<10ms)
- CLI startup time MUST be under 1 second
- Commands MUST execute quickly without perceptible delay
- No blocking operations in the main thread
- Console output MUST render efficiently for large task lists (100+ items)

## Agents and Skills Architecture

### Agent Responsibilities

| Agent | Domain | Skills |
|-------|--------|--------|
| `python-todo-architect` | Core application (models, services, storage) | uv-package-management, task-data-modeling, basic-crud-implementation, intermediate-feature-implementation, advanced-feature-implementation, modular-code-generation, runtime-state-management |
| `cli-designer` | CLI layer (commands, console display, user interaction) | cli-command-structure, cli-input-validation, cli-output-formatting, cli-interactive-menu, cli-error-handling |
| `testing-expert` | Testing (unit, integration, CLI tests) | basic-feature-testing, intermediate-feature-testing, advanced-feature-testing, edge-case-testing, regression-testing, in-memory-state-validation |

### Agent YAML Format

All agents MUST follow this YAML frontmatter format:

```yaml
---
name: agent-name
description: When to use this agent...
model: opus
color: green
tools: All tools
skills:
  - skill-name-1
  - skill-name-2
---
```

### Skill Organization

```text
.claude/
  agents/
    python-todo-architect.md    # Core application agent
    cli-designer.md             # CLI layer agent
    testing-expert.md           # Testing agent
  skills/
    uv-package-management/      # UV commands, dependencies
    task-data-modeling/         # Task model, enums
    basic-crud-implementation/  # CRUD operations
    intermediate-feature-implementation/  # Priority, tags, search
    advanced-feature-implementation/      # Recurring, due dates
    modular-code-generation/    # Code structure (core layer)
    runtime-state-management/   # State lifecycle (core layer)
    cli-command-structure/      # CLI command patterns
    cli-input-validation/       # Input validation for CLI
    cli-output-formatting/      # Console output formatting
    cli-interactive-menu/       # Interactive menu system
    cli-error-handling/         # CLI-specific error handling
    basic-feature-testing/      # Basic CRUD tests
    intermediate-feature-testing/  # Filter/search tests
    advanced-feature-testing/   # Recurring/reminder tests
    edge-case-testing/          # Edge cases
    regression-testing/         # Regression tests
    in-memory-state-validation/ # State isolation tests
```

## Development Workflow

### Feature Implementation Lifecycle

1. **Specify** (`/sp.specify`): Create feature specification with user stories
2. **Plan** (`/sp.plan`): Design architecture and data models
3. **Tasks** (`/sp.tasks`): Generate implementation task list
4. **Implement** (`/sp.implement`): Execute tasks via AI agents
5. **Commit** (`/sp.git.commit_pr`): Version control with clear history

### Level Progression (Phase 1 Scope)

Implementation proceeds through three levels, each with separate specs:

| Level | Features | Status |
|-------|----------|--------|
| **Basic** | Add, Delete, Update, View, Mark Complete | Pending |
| **Intermediate** | Priorities, Tags, Search, Filter, Sort | Pending |
| **Advanced** | Recurring Tasks, Due Dates, Reminders | Pending |

Each level MUST be fully implemented and tested before proceeding to the next.

### Commit Standards

- Every major feature implementation MUST have a clear commit
- Commit messages MUST follow conventional commits format
- Commits MUST reference the task ID (e.g., `feat(basic): T001 add task model`)

## Governance

### Constitution Authority

This constitution supersedes all other development practices for Phase 1. All PRs, code reviews, and implementations MUST verify compliance with these principles.

### Amendment Process

1. Proposed amendments MUST be documented with rationale
2. Amendments MUST be approved before implementation
3. Version MUST be incremented according to semantic versioning:
   - **MAJOR**: Backward-incompatible principle changes
   - **MINOR**: New principles or materially expanded guidance
   - **PATCH**: Clarifications, typo fixes, non-semantic changes
4. All dependent templates MUST be reviewed for consistency

### Compliance Review

- Every `/sp.implement` run MUST verify constitution compliance
- "No Manual Code" audit: All changes traceable to PHRs
- Test coverage MUST meet 100% threshold for core CRUD

### Success Criteria Checklist

- [ ] All three levels (Basic → Intermediate → Advanced) implemented
- [ ] Add, Delete, Update, View, Mark Complete demonstrated
- [ ] Filter and Recurring tasks functional
- [ ] Project passes "No Manual Code" audit
- [ ] README provides one-command setup via `uv`
- [ ] 100% test coverage for core CRUD logic

**Version**: 1.2.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2025-12-29
