# Feature Specification: Phase 1 Level 1 - Basic CRUD Operations

**Feature Branch**: `basic-crud`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Phase 1 Level 1 - Basic Level (Core Essentials) with Add, Delete, Update, View, and Mark Complete operations"

## Overview

This specification defines the minimal viable Todo application for Phase 1, focusing exclusively on the five core CRUD operations: **Add**, **Delete**, **Update**, **View**, and **Mark Complete**.

The application MUST be a fully interactive Typer CLI with Rich-formatted console output, in-memory storage, and a clean, type-safe architecture that adheres strictly to the Phase 1 Constitution.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Tasks (Priority: P1)

As a user, I want to see a list of all my tasks upon launching the app so that I can quickly understand my current todo list.

**Why this priority**: This is the foundation - users must be able to see their tasks before they can do anything else. Without viewing, no other operation makes sense.

**Independent Test**: Can be fully tested by launching the application and verifying the task list displays correctly. Delivers immediate value by showing the user their current state.

**Acceptance Scenarios**:

1. **Given** the application is launched with existing tasks, **When** the `list` command is run or user views tasks in menu, **Then** all tasks are displayed immediately in a Rich-formatted table showing ID, title, and completion status (symbol: ✓ for complete, ○ for incomplete)

2. **Given** the application is launched with no tasks, **When** the main screen loads, **Then** an empty state message is displayed: "No tasks yet. Run 'add' command or press 'a' in menu to add one."

3. **Given** multiple tasks exist, **When** viewing the task list with `list` command or in menu, **Then** tasks are displayed in creation order (oldest first) with sequential IDs

4. **Given** the task list is displayed, **When** viewing with `list` command or in menu, **Then** total task count and completed count are shown (e.g., "3/5 completed")

5. **Given** a task has a description, **When** viewing the task in the list, **Then** the description is shown truncated (max 50 chars with "..." if longer)

---

### User Story 2 - Add Task (Priority: P1)

As a user, I want to add a new task with a title and optional description so that I can capture new todos.

**Why this priority**: Adding tasks is equally critical as viewing - without the ability to add, the application has no value. This is co-priority P1 with View.

**Independent Test**: Can be tested by running the `add` command, filling in task details, and verifying the task appears in the list. Delivers value by allowing users to capture their todos.

**Acceptance Scenarios**:

1. **Given** the CLI is active, **When** user runs `add "Task Title"` or selects "Add Task" from menu, **Then** the task is created with auto-incrementing ID, `completed=False`, `created_at` timestamp

2. **Given** the CLI is active, **When** user runs `add "Task Title" "Task Description"`, **Then** both title and description are saved to the new task

3. **Given** user provides invalid input to add command, **When** user runs `add` with empty or whitespace-only title, **Then** validation error is shown ("Title is required") and task is not created

4. **Given** a new task is successfully created, **When** the add operation completes, **Then** a success message appears ("Task added") and the task list reflects the new task

5. **Given** user is in interactive menu mode, **When** user selects add task option and provides valid input, **Then** the task is created and user returns to menu

---

### User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

As a user, I want to toggle a task's completion status so that I can track my progress.

**Why this priority**: After viewing and adding tasks, the most common action is marking them complete. This is the core value proposition of a todo app.

**Independent Test**: Can be tested by running the `toggle` command with a task ID. Delivers value by enabling progress tracking.

**Acceptance Scenarios**:

1. **Given** an incomplete task exists, **When** user runs `toggle 1` (with valid task ID), **Then** the task is marked complete immediately with status change (○ → ✓ in next list view)

2. **Given** a complete task exists, **When** user runs `toggle 1` (with valid task ID), **Then** the task is marked incomplete immediately with status change (✓ → ○ in next list view)

3. **Given** a task completion status changes, **When** the change occurs, **Then** the task list reflects the updated status on next view

4. **Given** a task is marked complete, **When** viewing the task list, **Then** completed tasks are visually distinct (strikethrough or dimmed styling in Rich output)

5. **Given** a task completion toggle occurs, **When** the action completes, **Then** a success message appears ("Task marked complete/incomplete")

---

### User Story 4 - Update Task (Priority: P2)

As a user, I want to edit an existing task's title and/or description so that I can correct or refine task details.

**Why this priority**: Users need to fix typos and update details. Less frequent than marking complete but essential for maintaining accurate task information.

**Independent Test**: Can be tested by running the `update` command with a task ID and new values. Delivers value by allowing task refinement.

**Acceptance Scenarios**:

1. **Given** a task exists, **When** user runs `update 1 "New Title"` (with valid task ID and new title), **Then** the task title is updated and the original task ID is preserved

2. **Given** a task exists, **When** user runs `update 1 "New Title" "New Description"`, **Then** both title and description are updated and the `updated_at` timestamp is set

3. **Given** user provides invalid input to update command, **When** user runs `update` with empty or whitespace-only title, **Then** validation error is shown ("Title is required") and task is not updated

4. **Given** a task is successfully updated, **When** the update operation completes, **Then** a success message appears ("Task updated") and changes are reflected in subsequent list views

5. **Given** user is in interactive menu mode, **When** user selects update task option and provides valid input, **Then** the task is updated and user returns to menu

---

### User Story 5 - Delete Task (Priority: P3)

As a user, I want to permanently delete a task so that I can remove tasks that are no longer needed.

**Why this priority**: Deleting is destructive and less frequent than other operations. Users typically complete tasks rather than delete them.

**Independent Test**: Can be tested by running the `delete` command with a task ID and confirming deletion. Delivers value by keeping the list clean.

**Acceptance Scenarios**:

1. **Given** a task exists, **When** user runs `delete 1` (with valid task ID), **Then** the task is permanently removed after confirmation

2. **Given** user runs delete command, **When** user confirms deletion (for interactive mode), **Then** the task is permanently removed and the task list updates

3. **Given** user runs delete command, **When** user declines confirmation (for interactive mode), **Then** no changes are made and user returns to previous state

4. **Given** a task is successfully deleted, **When** the action completes, **Then** a success message appears ("Task deleted") and the task no longer appears in subsequent list views

5. **Given** the only task is deleted, **When** the action completes, **Then** the empty state message is displayed when viewing the task list

---

### Edge Cases

- **Empty title validation**: Title field rejects empty strings, whitespace-only strings, and strings exceeding 100 characters
- **Description length**: Description field accepts up to 500 characters; longer input is truncated or rejected with validation message
- **Rapid toggles**: Multiple quick Space presses on the same task are handled correctly without race conditions
- **Delete during edit**: If a task is deleted while its edit modal is open (edge case for future multi-user), handle gracefully
- **ID generation**: IDs remain unique and sequential even after deletions (no ID reuse)
- **Large task list**: Console output renders efficiently with 100+ tasks (<50ms display time)
- **Special characters**: Title and description support Unicode, emoji, and special characters
- **Command responsiveness**: CLI commands execute quickly with perceptible response time (<50ms)

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display all tasks in a Rich-formatted table when `list` command is executed
- **FR-002**: System MUST allow creating tasks with required title (1-100 chars) and optional description (0-500 chars) via `add` command
- **FR-003**: System MUST validate all user input before state changes (non-empty title, length limits)
- **FR-004**: System MUST allow toggling task completion status via `toggle` command with immediate feedback
- **FR-005**: System MUST allow editing existing task title and description via `update` command while preserving task ID
- **FR-006**: System MUST require confirmation before permanently deleting a task via `delete` command
- **FR-007**: System MUST generate unique, sequential integer IDs starting from 1
- **FR-008**: System MUST store all tasks in-memory only (no persistence to disk)
- **FR-009**: System MUST update console output when task state changes (no manual refresh needed)
- **FR-010**: System MUST display success/error notifications in console output
- **FR-011**: System MUST support command-based navigation (add, list, update, delete, toggle commands)
- **FR-012**: System MUST maintain task creation order for display (oldest first)
- **FR-013**: System MUST track and display task counts in list output (total and completed)
- **FR-014**: System MUST record `created_at` timestamp when task is created
- **FR-015**: System MUST record `updated_at` timestamp when task is modified

### Key Entities

- **Task**: The core entity representing a todo item
  - `id`: Unique sequential integer (auto-generated, starts at 1)
  - `title`: Required string (1-100 characters)
  - `description`: Optional string (0-500 characters)
  - `completed`: Boolean flag (default: False)
  - `created_at`: DateTime timestamp (set on creation)
  - `updated_at`: Optional DateTime timestamp (set on modification)

---

## Non-Functional Requirements

- **NFR-001**: All operations MUST complete with <50ms perceived latency
- **NFR-002**: Application MUST remain responsive during all operations (no UI freezing)
- **NFR-003**: Application MUST return to main menu or command prompt after operations
- **NFR-004**: Error messages MUST appear as console output, never as unhandled exceptions
- **NFR-005**: Application MUST handle terminal output formatting properly
- **NFR-006**: All code MUST include type hints per Constitution requirements
- **NFR-007**: All public functions MUST include docstrings
- **NFR-008**: Application MUST launch via `uv run todo` or `python main.py`

---

## Out of Scope for Level 1

- Priorities (Low, Medium, High, Critical)
- Tags and categorization
- Due dates and reminders
- Recurring tasks
- Search, filtering, and sorting
- Persistence to disk or database
- Mouse interaction beyond basic clicking
- Custom styling themes
- Multi-user support
- Undo/redo functionality

---

## Clarifications

### Session 2025-12-30

- Q: What timestamp format should be used for created_at and updated_at fields? → A: Use Python's built-in datetime
- Q: What storage approach should be used for in-memory task storage? → A: Use a dictionary with auto-incrementing integer keys for task IDs
- Q: What mechanism should be used for console output updates? → A: Use Rich for formatted console output
- Q: What application structure should be used for the CLI? → A: Main Typer application with command functions for add/list/update/delete/toggle operations
- Q: What command structure approach should be implemented? → A: Use Typer commands as defined in constitution

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five user stories (View, Add, Mark Complete, Update, Delete) are fully implemented and demonstrable
- **SC-002**: Application launches successfully with `uv run todo` command
- **SC-003**: Zero crashes or unhandled exceptions during normal operation (tested with 50+ operations)
- **SC-004**: 100% unit test coverage for TaskService CRUD methods
- **SC-005**: All commands (add, list, update, delete, toggle) function correctly
- **SC-006**: Console output updates immediately after state changes
- **SC-007**: Full compliance with Phase 1 Constitution (type hints, clean architecture, no manual code)
- **SC-008**: Code passes `uv run ruff check src/` with no errors
- **SC-009**: Code passes `uv run mypy src/todo/` with no errors

### Definition of Done

- [ ] All acceptance scenarios pass manual testing
- [ ] All unit tests pass (`uv run pytest tests/unit/`)
- [ ] All CLI tests pass (`uv run pytest tests/cli/`)
- [ ] Code coverage meets 100% for `src/todo/services/task_service.py`
- [ ] No linting errors (ruff)
- [ ] No type errors (mypy)
- [ ] PHR created documenting the implementation
- [ ] Committed to feature branch with conventional commit message
