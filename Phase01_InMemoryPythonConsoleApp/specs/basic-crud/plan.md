# Implementation Plan: Phase 1 Level 1 - Basic Level (Core Essentials)

**File Path:** `specs/basic-crud/plan.md`

## Technical Context

- **Feature**: Basic CRUD Operations (Add, Delete, Update, View, Mark Complete)
- **Architecture**: Clean, layered architecture with models, storage, services, and TUI layers
- **Technology Stack**: Python 3.13+, Textual TUI framework, UV package manager
- **Storage**: In-memory only (dict/list based)
- **State Management**: Module-level `TaskStore` singleton + `TaskService` wrapper
- **Reactivity**: Textual messages + `watch` decorators
- **UI Framework**: Textual with reactive components
- **Data Model**: Task entity with id, title, description, completed, created_at, updated_at
- **Unknowns**: NEEDS CLARIFICATION

### Dependencies

- **Primary**: Textual (TUI framework)
- **Testing**: pytest, textual.testing
- **Linting**: Ruff
- **Type Checking**: mypy

## Architecture Sketch

The application follows a clean, layered architecture with strict separation of concerns, designed for type-safety, testability, and future extensibility:

- **Models Layer** (`src/todo/models/`): Pure data structures (`Task` dataclass).
- **Storage Layer** (`src/todo/storage/`): In-memory persistence abstraction (`TaskStore` singleton).
- **Services Layer** (`src/todo/services/`): Business logic and validation (`TaskService`), emits reactive messages.
- **TUI Layer** (`src/todo/tui/`): Textual-based user interface with reactive widgets, modals, and keyboard-driven navigation.

Data flow is unidirectional: TUI → Service → Storage → Service emits `TasksChanged` → TUI reacts.

Reactive updates are achieved exclusively through Textual's message system and `watch` decorators — no manual DOM manipulation or polling.

## Constitution Check

### Compliance Status

- ✅ **Spec-Driven Development**: Implementation follows approved specification
- ✅ **Architecture First**: Clean Python architecture with proper `src/` layout
- ✅ **Clean Code Standards**: PEP 8, type hints, descriptive naming
- ✅ **Test-First Development**: 100% test coverage for core CRUD logic
- ✅ **Textual TUI Experience**: Full-featured TUI using Textual framework
- ✅ **UV Package Management**: Exclusively uses `uv` for dependency management

### Gate Evaluations

- **GATE-001**: Architecture compliance - PASSED
- **GATE-002**: Constitution adherence - PASSED
- **GATE-003**: Technology stack alignment - PASSED

## Section Structure

This plan is organized into four phases as required:

1. **Research Phase** – Identify best practices and patterns.
2. **Foundation Phase** – Establish core backend and project skeleton.
3. **Analysis Phase** – Design TUI components and reactive patterns.
4. **Synthesis Phase** – Integrate, polish, and validate.

## Research Approach

Adopt a **research-concurrent** approach:
- Research is conducted in parallel with planning and writing.
- Key decisions are informed by real-time validation of Textual documentation, examples, and community patterns.
- No exhaustive upfront research; instead, targeted lookups during each phase (e.g., "How to build reactive lists in Textual", "Best practices for modal forms in Textual").
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
| Reactivity Mechanism | Textual messages + watch() vs. reactive variables vs. manual refresh | Messages (`TasksChanged`) + `watch` on service | Explicit, traceable events; aligns with Textual best practices. Slightly more code than reactive vars, but clearer intent and easier testing. |
| Modal Reuse | Separate Add/Edit modals vs. Single reusable form modal | Single `TaskFormModal` used for both Add and Edit | Reduces duplication, easier maintenance. Requires careful pre-fill logic but worth the clarity. |
| Task ID Generation | UUID vs. Auto-increment integer | Sequential integer starting at 1 | Human-readable in UI, simpler debugging. Not globally unique but sufficient for in-memory single session. |
| Completion Styling | Checkbox character + strikethrough vs. separate completed list | Visual styling on same list (strikethrough + dim) | Keeps all tasks visible in one list; matches common todo app UX. Slightly more CSS work. |

## Testing Strategy

Validation directly mapped to acceptance criteria in `spec.md`:

| User Story | Validation Checks |
|------------|-------------------|
| US-001: View Tasks | - App starts with empty state message<br>- Tasks appear with ID, title, status, description preview<br>- Status bar shows correct counts<br>- Reactive update after add/delete |
| US-002: Add Task | - `a` opens modal with empty fields<br>- Title required validation<br>- Success toast on valid submit<br>- New task appears at bottom with correct ID |
| US-003: Mark Task Complete/Incomplete | - `space` toggles instantly<br>- Visual change immediate<br>- Status bar updates |
| US-004: Update Task | - `e` on selected task opens pre-filled modal<br>- Changes persist after save<br>- ID and created_at unchanged |
| US-005: Delete Task | - `d` opens confirmation modal<br>- Delete only on confirm<br>- Task removed and selection adjusted |

**Test Types**:
- Unit tests: `TaskStore` and `TaskService` (100% coverage, red → green)
- Integration tests: Modal submit → service → storage flow
- TUI tests: Snapshot of main screen states (empty, few tasks, completed tasks) using `textual.testing`

## Technical Details

### Phase 1: Research

Conducted concurrently:
- Textual documentation review for reactive patterns (messages, watch, compose)
- Best practices for modal forms and input validation
- Examples of task list widgets and keyboard navigation

### Phase 2: Foundation

- Project bootstrap with `uv`
- Implement `Task` model
- Implement `TaskStore` with full CRUD
- Implement `TaskService` with validation and `TasksChanged` message
- Achieve 100% unit test coverage

### Phase 3: Analysis

- Design `TaskItem`, `TaskList`, `StatusBar`
- Design reusable `TaskFormModal` and `ConfirmDeleteModal`
- Define keyboard bindings and action handlers
- Plan CSS structure (`styles/main.tcss`)

### Phase 4: Synthesis

- Integrate TUI with backend via service
- Implement full reactivity
- Add notifications, empty state, error handling
- Final polish: focus management, smooth navigation
- Execute full test suite and constitution compliance audit

## Agent Assignment

| Agent                  | Phase Focus                                      |
|------------------------|--------------------------------------------------|
| `python-todo-architect` | Foundation (models, storage, service)           |
| `tui-designer`         | Analysis & Synthesis (TUI components, reactivity)|
| `testing-expert`       | All phases (test writing and validation)        |

This plan ensures a robust, constitution-compliant implementation of the Basic Level while maintaining clarity, testability, and readiness for Intermediate and Advanced extensions.

## Phase 0: Outline & Research

### Research Tasks Identified

1. **Textual Reactive Patterns**: How to implement reactive updates with messages and watch decorators
2. **Modal Form Implementation**: Best practices for creating reusable modal forms in Textual
3. **Task List Widgets**: Examples of task list implementations in Textual
4. **Keyboard Navigation**: Proper implementation of keyboard shortcuts in Textual applications
5. **Toast Notifications**: How to implement toast notifications in Textual

### Research Findings

**Decision**: Use Textual's built-in reactive patterns
- **Rationale**: Aligns with Textual's architecture and provides clean separation of concerns
- **Alternatives considered**: Manual DOM manipulation, polling mechanisms

**Decision**: Implement reusable modal components
- **Rationale**: Reduces code duplication and improves maintainability
- **Alternatives considered**: Separate add/edit modals

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