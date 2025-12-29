# Feature Specification: Phase 1 Level 1 - Basic CRUD Operations

**Feature Branch**: `basic-crud`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Phase 1 Level 1 - Basic Level (Core Essentials) with Add, Delete, Update, View, and Mark Complete operations"

## Overview

This specification defines the minimal viable Todo application for Phase 1, focusing exclusively on the five core CRUD operations: **Add**, **Delete**, **Update**, **View**, and **Mark Complete**.

The application MUST be a fully interactive Textual TUI with real-time reactive updates, in-memory storage, and a clean, type-safe architecture that adheres strictly to the Phase 1 Constitution.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Tasks (Priority: P1)

As a user, I want to see a list of all my tasks upon launching the app so that I can quickly understand my current todo list.

**Why this priority**: This is the foundation - users must be able to see their tasks before they can do anything else. Without viewing, no other operation makes sense.

**Independent Test**: Can be fully tested by launching the application and verifying the task list displays correctly. Delivers immediate value by showing the user their current state.

**Acceptance Scenarios**:

1. **Given** the application is launched with existing tasks, **When** the main screen loads, **Then** all tasks are displayed immediately in a scrollable list showing ID, title, and completion status (checkbox visual: ✓ for complete, ○ for incomplete)

2. **Given** the application is launched with no tasks, **When** the main screen loads, **Then** an empty state message is displayed: "No tasks yet. Press 'a' to add one."

3. **Given** multiple tasks exist, **When** viewing the task list, **Then** tasks are displayed in creation order (oldest first) with sequential IDs

4. **Given** the task list is displayed, **When** looking at the status bar, **Then** total task count and completed count are shown (e.g., "3/5 completed")

5. **Given** a task has a description, **When** viewing the task in the list, **Then** the description is shown truncated (max 50 chars with "..." if longer)

---

### User Story 2 - Add Task (Priority: P1)

As a user, I want to add a new task with a title and optional description so that I can capture new todos.

**Why this priority**: Adding tasks is equally critical as viewing - without the ability to add, the application has no value. This is co-priority P1 with View.

**Independent Test**: Can be tested by pressing 'a', filling in task details, and verifying the task appears in the list. Delivers value by allowing users to capture their todos.

**Acceptance Scenarios**:

1. **Given** the main screen is displayed, **When** user presses `a`, **Then** an "Add Task" modal opens with focus on the Title field

2. **Given** the Add Task modal is open, **When** user enters a valid title (1-100 characters) and presses Enter/Submit, **Then** the task is created with auto-incrementing ID, `completed=False`, `created_at` timestamp, and the modal closes

3. **Given** the Add Task modal is open, **When** user enters a title and optional description (max 500 chars), **Then** both fields are saved to the new task

4. **Given** the Add Task modal is open, **When** user tries to submit with empty or whitespace-only title, **Then** validation error is shown inline ("Title is required") and submission is blocked

5. **Given** a new task is successfully created, **When** the modal closes, **Then** a success toast notification appears ("Task added") and the task list updates reactively showing the new task at the bottom

6. **Given** the Add Task modal is open, **When** user presses `Escape`, **Then** the modal closes without creating a task

---

### User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

As a user, I want to toggle a task's completion status so that I can track my progress.

**Why this priority**: After viewing and adding tasks, the most common action is marking them complete. This is the core value proposition of a todo app.

**Independent Test**: Can be tested by selecting a task and pressing Space to toggle status. Delivers value by enabling progress tracking.

**Acceptance Scenarios**:

1. **Given** an incomplete task is selected, **When** user presses `Space`, **Then** the task is marked complete immediately with visual indicator change (○ → ✓)

2. **Given** a complete task is selected, **When** user presses `Space`, **Then** the task is marked incomplete immediately with visual indicator change (✓ → ○)

3. **Given** a task completion status changes, **When** the change occurs, **Then** the status bar counters update reactively (e.g., "2/5 completed" → "3/5 completed")

4. **Given** a task is marked complete, **When** viewing the task list, **Then** completed tasks are visually distinct (dimmed text color or strikethrough styling)

5. **Given** a task completion toggle occurs, **When** the action completes, **Then** no modal is shown - action is immediate with subtle visual feedback only

---

### User Story 4 - Update Task (Priority: P2)

As a user, I want to edit an existing task's title and/or description so that I can correct or refine task details.

**Why this priority**: Users need to fix typos and update details. Less frequent than marking complete but essential for maintaining accurate task information.

**Independent Test**: Can be tested by selecting a task, pressing 'e', modifying fields, and verifying changes persist. Delivers value by allowing task refinement.

**Acceptance Scenarios**:

1. **Given** a task is selected, **When** user presses `e`, **Then** an "Edit Task" modal opens with Title and Description fields pre-filled with current values

2. **Given** the Edit Task modal is open, **When** user modifies the title and/or description and submits, **Then** changes are saved immediately and the list updates reactively

3. **Given** the Edit Task modal is open, **When** user tries to submit with empty title, **Then** validation error is shown ("Title is required") and submission is blocked

4. **Given** a task is successfully updated, **When** the modal closes, **Then** a success toast appears ("Task updated"), the original task ID is preserved, and `updated_at` timestamp is set

5. **Given** the Edit Task modal is open, **When** user presses `Escape`, **Then** the modal closes without saving changes

---

### User Story 5 - Delete Task (Priority: P3)

As a user, I want to permanently delete a task so that I can remove tasks that are no longer needed.

**Why this priority**: Deleting is destructive and less frequent than other operations. Users typically complete tasks rather than delete them.

**Independent Test**: Can be tested by selecting a task, pressing 'd', confirming deletion, and verifying task is removed from list. Delivers value by keeping the list clean.

**Acceptance Scenarios**:

1. **Given** a task is selected, **When** user presses `d`, **Then** a confirmation modal appears: "Delete this task? This cannot be undone."

2. **Given** the delete confirmation modal is open, **When** user confirms (presses Enter or clicks "Delete"), **Then** the task is permanently removed and the list updates reactively

3. **Given** the delete confirmation modal is open, **When** user cancels (presses Escape or clicks "Cancel"), **Then** the modal closes and no changes are made

4. **Given** a task is successfully deleted, **When** the action completes, **Then** a success toast appears ("Task deleted") and selection moves to the next task (or previous if deleting the last task)

5. **Given** the only task is deleted, **When** the action completes, **Then** the empty state message is displayed

---

### Edge Cases

- **Empty title validation**: Title field rejects empty strings, whitespace-only strings, and strings exceeding 100 characters
- **Description length**: Description field accepts up to 500 characters; longer input is truncated or rejected with validation message
- **Rapid toggles**: Multiple quick Space presses on the same task are handled correctly without race conditions
- **Delete during edit**: If a task is deleted while its edit modal is open (edge case for future multi-user), handle gracefully
- **ID generation**: IDs remain unique and sequential even after deletions (no ID reuse)
- **Large task list**: UI remains responsive with 100+ tasks (scrolling, selection)
- **Special characters**: Title and description support Unicode, emoji, and special characters
- **Keyboard navigation**: Arrow keys (↑/↓) and vim keys (j/k) work consistently for task selection

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display all tasks in a scrollable list on application startup
- **FR-002**: System MUST allow creating tasks with required title (1-100 chars) and optional description (0-500 chars)
- **FR-003**: System MUST validate all user input before state changes (non-empty title, length limits)
- **FR-004**: System MUST allow toggling task completion status with immediate visual feedback
- **FR-005**: System MUST allow editing existing task title and description while preserving task ID
- **FR-006**: System MUST require confirmation before permanently deleting a task
- **FR-007**: System MUST generate unique, sequential integer IDs starting from 1
- **FR-008**: System MUST store all tasks in-memory only (no persistence to disk)
- **FR-009**: System MUST update UI reactively when task state changes (no manual refresh)
- **FR-010**: System MUST display success/error notifications as in-app toasts
- **FR-011**: System MUST support keyboard navigation (↑/↓, j/k for selection; a/e/d/Space for actions)
- **FR-012**: System MUST maintain task creation order for display (oldest first)
- **FR-013**: System MUST track and display task counts in status bar (total and completed)
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
- **NFR-003**: Focus MUST return to task list after modal operations
- **NFR-004**: Error messages MUST appear as in-app notifications, never as unhandled exceptions
- **NFR-005**: Application MUST handle terminal resize gracefully
- **NFR-006**: All code MUST include type hints per Constitution requirements
- **NFR-007**: All public functions MUST include docstrings
- **NFR-008**: Application MUST launch via `uv run todo` or `uv run python -m todo.tui`

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
- Q: What mechanism should be used for real-time UI updates? → A: Use Textual's reactive properties and message system
- Q: What UI structure should be used for the application? → A: Single main screen with modal dialogs for add/edit/delete operations
- Q: What keyboard navigation approach should be implemented? → A: Use standard keyboard shortcuts as defined in constitution

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five user stories (View, Add, Mark Complete, Update, Delete) are fully implemented and demonstrable
- **SC-002**: Application launches successfully with `uv run todo` command
- **SC-003**: Zero crashes or unhandled exceptions during normal operation (tested with 50+ operations)
- **SC-004**: 100% unit test coverage for TaskService CRUD methods
- **SC-005**: All keyboard shortcuts (a, e, d, Space, ↑, ↓, j, k, Escape, q) function correctly
- **SC-006**: UI updates reactively within 50ms of state changes
- **SC-007**: Full compliance with Phase 1 Constitution (type hints, clean architecture, no manual code)
- **SC-008**: Code passes `uv run ruff check src/` with no errors
- **SC-009**: Code passes `uv run mypy src/todo/` with no errors

### Definition of Done

- [ ] All acceptance scenarios pass manual testing
- [ ] All unit tests pass (`uv run pytest tests/unit/`)
- [ ] All TUI tests pass (`uv run pytest tests/tui/`)
- [ ] Code coverage meets 100% for `src/todo/services/task_service.py`
- [ ] No linting errors (ruff)
- [ ] No type errors (mypy)
- [ ] PHR created documenting the implementation
- [ ] Committed to feature branch with conventional commit message
