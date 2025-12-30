# Implementation Plan: Phase 1 Level 1 - Basic Level (Core Essentials)

**File Path:** `specs/basic-crud/plan.md`

## Technical Context

- **Feature**: Basic CRUD Operations (Add, Delete, Update, View, Mark Complete)
- **Architecture**: Clean, layered architecture with models, storage, services, and CLI layers
- **Technology Stack**: Python 3.13+, Typer CLI framework, Rich formatting, UV package manager
- **Storage**: In-memory only (dict/list based)
- **State Management**: Module-level `TaskStore` singleton + `TaskService` wrapper
- **Output**: Rich-formatted console output
- **UI Framework**: Typer with Rich-formatted console output
- **Data Model**: Task entity with id, title, description, completed, created_at, updated_at
- **Unknowns**: NEEDS CLARIFICATION

### Dependencies

- **Primary**: Typer (CLI framework), Rich (formatting)
- **Testing**: pytest
- **Linting**: Ruff
- **Type Checking**: mypy

## Architecture Sketch

The application follows a clean, layered architecture with strict separation of concerns, designed for type-safety, testability, and future extensibility:

- **Models Layer** (`src/todo/models/`): Pure data structures (`Task` dataclass).
- **Storage Layer** (`src/todo/storage/`): In-memory persistence abstraction (`TaskStore` singleton).
- **Services Layer** (`src/todo/services/`): Business logic and validation (`TaskService`), emits reactive messages.
- **CLI Layer** (`src/todo/cli/`): Typer-based command interface with Rich-formatted console output, command-driven navigation.

Data flow is unidirectional: CLI Command → Service → Storage → Service returns result → CLI displays formatted output.

Output updates are achieved through Rich formatting to console — no DOM manipulation needed.

## Constitution Check

### Compliance Status

- ✅ **Spec-Driven Development**: Implementation follows approved specification
- ✅ **Architecture First**: Clean Python architecture with proper `src/` layout
- ✅ **Clean Code Standards**: PEP 8, type hints, descriptive naming
- ✅ **Test-First Development**: 100% test coverage for core CRUD logic
- ✅ **Rich CLI Experience**: Full-featured CLI using Typer framework
- ✅ **UV Package Management**: Exclusively uses `uv` for dependency management

### Gate Evaluations

- **GATE-001**: Architecture compliance - PASSED
- **GATE-002**: Constitution adherence - PASSED
- **GATE-003**: Technology stack alignment - PASSED

## Section Structure

This plan is organized into four phases as required:

1. **Research Phase** – Identify best practices and patterns.
2. **Foundation Phase** – Establish core backend and project skeleton.
3. **Analysis Phase** – Design CLI commands and Rich formatting patterns.
4. **Synthesis Phase** – Integrate, polish, and validate.

## Research Approach

Adopt a **research-concurrent** approach:
- Research is conducted in parallel with planning and writing.
- Key decisions are informed by real-time validation of Typer and Rich documentation, examples, and community patterns.
- No exhaustive upfront research; instead, targeted lookups during each phase (e.g., "How to build Rich tables", "Best practices for CLI command validation").
- All external references cited in APA style where applicable.

## Quality Validation

- **Constitution Compliance Check**: Every deliverable verified against Phase 1 Constitution principles (type hints, uv, no manual code, clean structure).
- **Test-Driven Validation**: 100% coverage for `TaskStore` and `TaskService` CRUD operations before TUI integration.
- **Acceptance Criteria Mapping**: Each user story from `spec.md` has corresponding validation steps.
- **Peer Review Simulation**: Agent outputs cross-checked for consistency (architect → designer → tester).

## Decisions Needing Documentation

| Decision | Options Considered | Chosen Approach | Tradeoffs |
|----------|---------------------|-----------------|-----------|
| State Management | Global module variables vs. App-level attribute vs. Dedicated reactive store | Module-level `TaskStore` singleton + `TaskService` wrapper | Simple, no boilerplate; sufficient for Phase 1 in-memory scope. Less flexible than full reactive store (e.g., textual-reactive) but avoids over-abstraction. |
| Output Mechanism | Textual reactive UI vs. Rich console formatting | Rich-formatted console output via Typer commands | Direct, immediate feedback; aligns with CLI best practices. Clear separation between command input and formatted output. |
| Command Structure | TUI modals vs. CLI commands | Separate Typer commands for add/list/update/delete/toggle | Reduces complexity, follows CLI conventions. Clear command separation makes each function focused. |
| Task ID Generation | UUID vs. Auto-increment integer | Sequential integer starting at 1 | Human-readable in output, simpler debugging. Not globally unique but sufficient for in-memory single session. |
| Completion Styling | Checkbox character + strikethrough vs. separate completed list | Visual styling in Rich table output (strikethrough + dim) | Keeps all tasks visible in one list; matches common todo app UX. Uses Rich formatting for visual distinction. |

## Testing Strategy

Validation directly mapped to acceptance criteria in `spec.md`:

| User Story | Validation Checks |
|------------|-------------------|
| US-001: View Tasks | - App starts with empty state message<br>- Tasks appear with ID, title, status, description preview in Rich table<br>- Count display shows correct totals<br>- Output updates after add/delete |
| US-002: Add Task | - `add` command creates task<br>- Title required validation<br>- Success message on valid submit<br>- New task appears in list with correct ID |
| US-003: Mark Task Complete/Incomplete | - `toggle` command changes status<br>- Status change visible in next list view<br>- Count display updates |
| US-004: Update Task | - `update` command modifies task<br>- Changes persist after save<br>- ID and created_at unchanged |
| US-005: Delete Task | - `delete` command with confirmation<br>- Delete only on confirm<br>- Task removed from subsequent list views |

**Test Types**:
- Unit tests: `TaskStore` and `TaskService` (100% coverage, red → green)
- Integration tests: Command execution → service → storage flow
- CLI tests: Command output validation and interaction flows

## Technical Details

### Phase 1: Research

Conducted concurrently:
- Typer documentation review for command patterns (arguments, options, validation)
- Rich documentation for formatting patterns (tables, styling, output)
- Examples of CLI command structures and input validation

### Phase 2: Foundation

- Project bootstrap with `uv`
- Implement `Task` model
- Implement `TaskStore` with full CRUD
- Implement `TaskService` with validation and `TasksChanged` message
- Achieve 100% unit test coverage

### Phase 3: Analysis

- Design Rich table formatting for task display
- Design CLI command functions for add/list/update/delete/toggle
- Define command arguments, options and validation
- Plan Rich styling for console output

### Phase 4: Synthesis

- Integrate CLI commands with backend via service
- Implement Rich-formatted output
- Add notifications, empty state, error handling
- Final polish: command flow, user experience
- Execute full test suite and constitution compliance audit

## Agent Assignment

| Agent                  | Phase Focus                                      |
|------------------------|--------------------------------------------------|
| `python-todo-architect` | Foundation (models, storage, service)           |
| `cli-designer`         | Analysis & Synthesis (CLI commands, Rich formatting)|
| `testing-expert`       | All phases (test writing and validation)        |

This plan ensures a robust, constitution-compliant implementation of the Basic Level while maintaining clarity, testability, and readiness for Intermediate and Advanced extensions.

## Phase 0: Outline & Research

### Research Tasks Identified

1. **Typer Command Patterns**: How to implement CLI commands with proper arguments and options
2. **Rich Formatting**: Best practices for creating Rich-formatted console output
3. **Task Table Display**: Examples of Rich table implementations for task display
4. **CLI Input Validation**: Proper implementation of input validation in Typer commands
5. **Console Notifications**: How to implement user feedback in console applications

### Research Findings

**Decision**: Use Typer's built-in command patterns
- **Rationale**: Aligns with Typer's architecture and provides clean separation of concerns
- **Alternatives considered**: Manual argument parsing, custom CLI frameworks

**Decision**: Implement Rich-formatted console output
- **Rationale**: Provides professional-looking output with tables and styling
- **Alternatives considered**: Basic print statements, custom formatting

**Decision**: Use integer-based sequential IDs
- **Rationale**: Human-readable and simpler for debugging
- **Alternatives considered**: UUIDs, string-based IDs

## Phase 1: Design & Contracts

### Data Model

**Task Entity**:
- `id`: int (auto-increment, unique)
- `title`: str (1-100 characters, required)
- `description`: str (0-500 characters, optional)
- `completed`: bool (default: False)
- `created_at`: datetime (set on creation)
- `updated_at`: datetime (set on modification, optional)

### API Contracts

**TaskService Methods**:
- `add_task(title: str, description: str = "") -> Task`
- `delete_task(task_id: int) -> bool`
- `update_task(task_id: int, title: str, description: str, completed: bool) -> Task`
- `toggle_task_completion(task_id: int) -> Task`
- `get_all_tasks() -> List[Task]`
- `get_task(task_id: int) -> Task`

**Messages**:
- `TasksChanged(tasks: List[Task])`
- `TaskAdded(task: Task)`
- `TaskUpdated(task: Task)`
- `TaskDeleted(task_id: int)`
- `TaskToggled(task: Task)`