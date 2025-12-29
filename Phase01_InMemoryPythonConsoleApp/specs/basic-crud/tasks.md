---
description: "Task list for Basic CRUD Operations implementation"
---

# Tasks: Basic CRUD Operations

**Input**: Design documents from `/specs/basic-crud/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks included as requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project structure**: `src/`, `tests/` at repository root
- **Application structure**: `src/todo/models/`, `src/todo/services/`, `src/todo/storage/`, `src/todo/tui/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure with src/todo/ directory
- [ ] T002 Initialize Python project with UV and create pyproject.toml
- [ ] T003 [P] Configure linting (Ruff) and formatting tools
- [ ] T004 [P] Configure type checking (mypy) settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create Task data model in src/todo/models/task.py with proper type hints as required by constitution; include id (int, auto-increment), title (str, 1-100 chars, required), description (str, 0-500 chars, optional), completed (bool, default False), created_at (datetime), updated_at (datetime, optional)
- [ ] T006 Create TaskStore in-memory storage in src/todo/storage/task_store.py with proper type hints as required by constitution; implement full CRUD operations (add, get all, get by id, update, delete, toggle completion) using dictionary with auto-incrementing integer keys for task IDs
- [ ] T007 Create TaskService with CRUD operations in src/todo/services/task_service.py with proper type hints as required by constitution; implement add_task, get_all_tasks, get_task, update_task, delete_task, toggle_task_completion methods with proper validation and reactive message emission
- [ ] T008 Define reactive messages in src/todo/services/messages.py with proper type hints as required by constitution; implement TasksChanged (for view updates), TaskAdded, TaskUpdated, TaskDeleted, TaskToggled messages for reactive UI updates
- [ ] T009 Setup Textual TUI application structure in src/todo/tui/ with proper type hints as required by constitution

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Tasks (Priority: P1) 🎯 MVP

**Goal**: Display all tasks in a scrollable list on application startup with proper visual indicators and status bar

**Independent Test**: Launch the application and verify the task list displays correctly with proper visual indicators for empty state, tasks with ID/title/status, description previews, and status bar counts.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Unit test for TaskStore get_all_tasks in tests/unit/test_task_store.py
- [ ] T011 [P] [US1] Unit test for TaskService get_all_tasks in tests/unit/test_task_service.py
- [ ] T012 [P] [US1] TUI test for empty state display in tests/tui/test_view_tasks.py
- [ ] T013 [P] [US1] TUI test for task list display in tests/tui/test_view_tasks.py

### Implementation for User Story 1

- [ ] T014 [P] [US1] Create TaskList component in src/todo/tui/components/task_list.py with proper type hints as required by constitution; implement scrollable list display, handle empty state with "No tasks yet. Press 'a' to add one." message, and watch for TasksChanged messages to update reactively
- [ ] T015 [P] [US1] Create TaskItem component in src/todo/tui/components/task_item.py with proper type hints as required by constitution; display ID, title, completion status (✓/○), and truncated description (max 50 chars with "..."), support visual distinction for completed tasks (strikethrough/dim)
- [ ] T016 [US1] Create StatusBar component in src/todo/tui/components/status_bar.py with proper type hints as required by constitution; display total task count and completed count in format "X/Y completed", update reactively when task status changes
- [ ] T017 [US1] Implement main application with task list in src/todo/tui/app.py with proper type hints as required by constitution; initialize with TaskList and StatusBar components, implement keyboard navigation (↑/↓, j/k) for task selection, handle reactive updates via message subscription
- [ ] T018 [US1] Add empty state handling to TaskList component with proper type hints as required by constitution
- [ ] T019 [US1] Add task display with ID, title, completion status to TaskItem with proper type hints as required by constitution
- [ ] T020 [US1] Add description preview (truncated) to TaskItem with proper type hints as required by constitution
- [ ] T021 [US1] Implement status bar with total/completed counts with proper type hints as required by constitution
- [ ] T022 [US1] Add keyboard navigation for task selection (↑/↓, j/k) with proper type hints as required by constitution

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Add Task (Priority: P1)

**Goal**: Allow users to add new tasks with title and optional description via modal with validation

**Independent Test**: Press 'a', fill in task details, verify task appears in the list with correct ID and timestamp.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US2] Unit test for TaskService add_task validation in tests/unit/test_task_service.py
- [ ] T024 [P] [US2] Unit test for TaskStore add_task in tests/unit/test_task_store.py
- [ ] T025 [P] [US2] TUI test for AddTaskModal in tests/tui/test_add_task.py
- [ ] T026 [P] [US2] TUI test for validation error handling in tests/tui/test_add_task.py

### Implementation for User Story 2

- [ ] T027 [P] [US2] Create AddTaskModal in src/todo/tui/modals/add_task_modal.py with proper type hints as required by constitution; include title field (required, 1-100 chars), optional description field (max 500 chars), validation error display, focus on title field when opened, support Escape key to close without creating
- [ ] T028 [US2] Add keyboard binding 'a' to open modal in src/todo/tui/app.py with proper type hints as required by constitution
- [ ] T029 [US2] Implement title validation (1-100 chars) in TaskService with proper type hints as required by constitution
- [ ] T030 [US2] Implement description validation (0-500 chars) in TaskService with proper type hints as required by constitution
- [ ] T031 [US2] Add form validation to AddTaskModal with inline error display with proper type hints as required by constitution
- [ ] T032 [US2] Connect AddTaskModal to TaskService for task creation with proper type hints as required by constitution
- [ ] T033 [US2] Add success toast notification ("Task added") in src/todo/tui/app.py with proper type hints as required by constitution
- [ ] T034 [US2] Ensure new task appears at bottom of list with correct ID with proper type hints as required by constitution
- [ ] T035 [US2] Add escape key handling to close modal without creating task with proper type hints as required by constitution

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Allow users to toggle task completion status with immediate visual feedback and status bar updates

**Independent Test**: Select a task and press Space to toggle status, verify visual change and status bar updates.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T036 [P] [US3] Unit test for TaskService toggle_task_completion in tests/unit/test_task_service.py
- [ ] T037 [P] [US3] Unit test for TaskStore toggle_task_completion in tests/unit/test_task_store.py
- [ ] T038 [P] [US3] TUI test for completion toggle in tests/tui/test_mark_complete.py
- [ ] T039 [P] [US3] TUI test for visual feedback in tests/tui/test_mark_complete.py

### Implementation for User Story 3

- [ ] T040 [P] [US3] Add toggle completion method to TaskService in src/todo/services/task_service.py with proper type hints as required by constitution
- [ ] T041 [P] [US3] Add toggle completion method to TaskStore in src/todo/storage/task_store.py with proper type hints as required by constitution
- [ ] T042 [US3] Add keyboard binding Space to toggle completion in src/todo/tui/app.py with proper type hints as required by constitution
- [ ] T043 [US3] Add visual indicators (✓/○) to TaskItem component with proper type hints as required by constitution; show ○ for incomplete tasks and ✓ for complete tasks, support immediate visual feedback when toggled
- [ ] T044 [US3] Add visual styling for completed tasks (strikethrough/dim) with proper type hints as required by constitution; apply strikethrough and dimmed styling to completed tasks to make them visually distinct from incomplete tasks
- [ ] T045 [US3] Update status bar counters reactively when completion toggles with proper type hints as required by constitution
- [ ] T046 [US3] Ensure immediate visual feedback with no modal required with proper type hints as required by constitution

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - Update Task (Priority: P2)

**Goal**: Allow users to edit existing task's title and description via modal while preserving ID

**Independent Test**: Select a task, press 'e', modify fields, verify changes persist with same ID and updated timestamp.

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T047 [P] [US4] Unit test for TaskService update_task validation in tests/unit/test_task_service.py
- [ ] T048 [P] [US4] Unit test for TaskStore update_task in tests/unit/test_task_store.py
- [ ] T049 [P] [US4] TUI test for EditTaskModal in tests/tui/test_update_task.py
- [ ] T050 [P] [US4] TUI test for validation error handling in tests/tui/test_update_task.py

### Implementation for User Story 4

- [ ] T051 [P] [US4] Create EditTaskModal in src/todo/tui/modals/edit_task_modal.py with proper type hints as required by constitution; include pre-filled title and description fields, validation matching AddTaskModal (title 1-100 chars, description max 500 chars), validation error display, support Escape key to close without saving
- [ ] T052 [US4] Add keyboard binding 'e' to open edit modal in src/todo/tui/app.py with proper type hints as required by constitution
- [ ] T053 [US4] Implement update_task method in TaskService with validation with proper type hints as required by constitution
- [ ] T054 [US4] Implement update_task method in TaskStore with proper type hints as required by constitution
- [ ] T055 [US4] Add pre-filled form fields to EditTaskModal with current values with proper type hints as required by constitution
- [ ] T056 [US4] Add validation to EditTaskModal with inline error display with proper type hints as required by constitution
- [ ] T057 [US4] Connect EditTaskModal to TaskService for task updates with proper type hints as required by constitution
- [ ] T058 [US4] Add success toast notification ("Task updated") in src/todo/tui/app.py with proper type hints as required by constitution
- [ ] T059 [US4] Preserve original task ID and set updated_at timestamp with proper type hints as required by constitution
- [ ] T060 [US4] Add escape key handling to close modal without saving changes with proper type hints as required by constitution

**Checkpoint**: At this point, User Stories 1, 2, 3 AND 4 should all work independently

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Allow users to permanently delete tasks with confirmation modal

**Independent Test**: Select a task, press 'd', confirm deletion, verify task is removed and selection adjusted.

### Tests for User Story 5 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T061 [P] [US5] Unit test for TaskService delete_task in tests/unit/test_task_service.py
- [ ] T062 [P] [US5] Unit test for TaskStore delete_task in tests/unit/test_task_store.py
- [ ] T063 [P] [US5] TUI test for ConfirmDeleteModal in tests/tui/test_delete_task.py
- [ ] T064 [P] [US5] TUI test for selection adjustment after deletion in tests/tui/test_delete_task.py

### Implementation for User Story 5

- [ ] T065 [P] [US5] Create ConfirmDeleteModal in src/todo/tui/modals/confirm_delete_modal.py with proper type hints as required by constitution; include confirmation message "Delete this task? This cannot be undone.", OK/Cancel buttons, support Enter to confirm, Escape to cancel
- [ ] T066 [US5] Add keyboard binding 'd' to open delete confirmation in src/todo/tui/app.py with proper type hints as required by constitution
- [ ] T067 [US5] Implement delete_task method in TaskService with proper type hints as required by constitution
- [ ] T068 [US5] Implement delete_task method in TaskStore with proper type hints as required by constitution
- [ ] T069 [US5] Add confirmation modal with proper message and buttons with proper type hints as required by constitution
- [ ] T070 [US5] Connect ConfirmDeleteModal to TaskService for task deletion with proper type hints as required by constitution
- [ ] T071 [US5] Add success toast notification ("Task deleted") in src/todo/tui/app.py with proper type hints as required by constitution
- [ ] T072 [US5] Adjust task selection after deletion (next task or previous if last) with proper type hints as required by constitution
- [ ] T073 [US5] Handle empty state when last task is deleted with proper type hints as required by constitution

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T074 [P] Documentation updates in README.md
- [ ] T075 Code cleanup and refactoring across all components with proper type hints as required by constitution
- [ ] T076 Performance optimization for large task lists (100+ tasks) with <50ms latency as required by constitution
- [ ] T077 [P] Additional unit tests to achieve 100% coverage in tests/unit/
- [ ] T078 CSS styling improvements in src/todo/tui/styles/
- [ ] T079 Error handling and edge case handling (special chars, rapid toggles) with proper type hints as required by constitution
- [ ] T080 Run full test suite and validate acceptance criteria

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3 but should be independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3/US4 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Unit test for TaskStore get_all_tasks in tests/unit/test_task_store.py"
Task: "Unit test for TaskService get_all_tasks in tests/unit/test_task_service.py"
Task: "TUI test for empty state display in tests/tui/test_view_tasks.py"
Task: "TUI test for task list display in tests/tui/test_view_tasks.py"

# Launch all components for User Story 1 together:
Task: "Create TaskList component in src/todo/tui/components/task_list.py"
Task: "Create TaskItem component in src/todo/tui/components/task_item.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence