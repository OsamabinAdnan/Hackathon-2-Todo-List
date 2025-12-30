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
- **Application structure**: `src/todo/models/`, `src/todo/services/`, `src/todo/storage/`, `src/todo/cli/`

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
- [ ] T008 Define CLI command result structures in src/todo/services/results.py with proper type hints as required by constitution; implement Result classes for command outcomes to facilitate proper return values from service layer to CLI layer
- [ ] T009 Setup Typer CLI application structure in main.py with proper type hints as required by constitution
- [ ] T010 Create interactive menu system in main.py with proper type hints as required by constitution; implement main menu with options for add, list, update, delete, toggle, and quit commands
- [ ] T011 Implement menu navigation functions in src/todo/cli/views/menu.py with proper type hints as required by constitution; handle user selection and command routing
- [ ] T012 Add user prompts and input validation for menu selections with proper type hints as required by constitution

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Tasks (Priority: P1) 🎯 MVP

**Goal**: Display all tasks in a scrollable list on application startup with proper visual indicators and status bar

**Independent Test**: Launch the application and verify the task list displays correctly with proper visual indicators for empty state, tasks with ID/title/status, description previews, and status bar counts.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Unit test for TaskStore get_all_tasks in tests/unit/test_task_store.py
- [ ] T011 [P] [US1] Unit test for TaskService get_all_tasks in tests/unit/test_task_service.py
- [ ] T012 [P] [US1] CLI test for empty state display in tests/cli/test_view_tasks.py
- [ ] T013 [P] [US1] CLI test for task list display in tests/cli/test_view_tasks.py

### Implementation for User Story 1

- [ ] T014 [P] [US1] Create task table display function in src/todo/cli/views/table_formatter.py with proper type hints as required by constitution; implement Rich table display, handle empty state with "No tasks yet. Run 'add' command to add one." message, and format tasks with ID, title, completion status (✓/○), and truncated description (max 50 chars with "...")
- [ ] T015 [P] [US1] Create task formatting function in src/todo/cli/views/formatters.py with proper type hints as required by constitution; display ID, title, completion status (✓/○), and truncated description (max 50 chars with "..."), support visual distinction for completed tasks (strikethrough/dim)
- [ ] T016 [US1] Create task count display function in src/todo/cli/views/status.py with proper type hints as required by constitution; display total task count and completed count in format "X/Y completed", format for inclusion in list output
- [ ] T017 [US1] Implement list command in main.py with proper type hints as required by constitution; integrate with TaskService to retrieve tasks, use Rich table formatting for display, include count summary
- [ ] T018 [US1] Add empty state handling to list command with proper type hints as required by constitution
- [ ] T019 [US1] Add task display with ID, title, completion status to table formatter with proper type hints as required by constitution
- [ ] T020 [US1] Add description preview (truncated) to task formatter with proper type hints as required by constitution
- [ ] T021 [US1] Implement task count display with total/completed counts with proper type hints as required by constitution
- [ ] T022 [US1] Add command-based task listing functionality with proper type hints as required by constitution

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Add Task (Priority: P1)

**Goal**: Allow users to add new tasks with title and optional description via modal with validation

**Independent Test**: Press 'a', fill in task details, verify task appears in the list with correct ID and timestamp.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US2] Unit test for TaskService add_task validation in tests/unit/test_task_service.py
- [ ] T024 [P] [US2] Unit test for TaskStore add_task in tests/unit/test_task_store.py
- [ ] T025 [P] [US2] CLI test for add command in tests/cli/test_add_task.py
- [ ] T026 [P] [US2] CLI test for validation error handling in tests/cli/test_add_task.py

### Implementation for User Story 2

- [ ] T027 [P] [US2] Create add command in main.py with proper type hints as required by constitution; implement title argument (required, 1-100 chars), optional description argument (max 500 chars), validation error display, integrate with TaskService for task creation
- [ ] T028 [US2] Add command registration for 'add' in main.py with proper type hints as required by constitution
- [ ] T029 [US2] Implement title validation (1-100 chars) in TaskService with proper type hints as required by constitution
- [ ] T030 [US2] Implement description validation (0-500 chars) in TaskService with proper type hints as required by constitution
- [ ] T031 [US2] Add input validation to add command with error display with proper type hints as required by constitution
- [ ] T032 [US2] Connect add command to TaskService for task creation with proper type hints as required by constitution
- [ ] T033 [US2] Add success message ("Task added") display in add command with proper type hints as required by constitution
- [ ] T034 [US2] Ensure new task appears in subsequent list views with correct ID with proper type hints as required by constitution
- [ ] T035 [US2] Add command error handling to gracefully handle invalid inputs with proper type hints as required by constitution

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Allow users to toggle task completion status with immediate visual feedback and status bar updates

**Independent Test**: Select a task and press Space to toggle status, verify visual change and status bar updates.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T036 [P] [US3] Unit test for TaskService toggle_task_completion in tests/unit/test_task_service.py
- [ ] T037 [P] [US3] Unit test for TaskStore toggle_task_completion in tests/unit/test_task_store.py
- [ ] T038 [P] [US3] CLI test for toggle command in tests/cli/test_mark_complete.py
- [ ] T039 [P] [US3] CLI test for status change feedback in tests/cli/test_mark_complete.py

### Implementation for User Story 3

- [ ] T040 [P] [US3] Add toggle completion method to TaskService in src/todo/services/task_service.py with proper type hints as required by constitution
- [ ] T041 [P] [US3] Add toggle completion method to TaskStore in src/todo/storage/task_store.py with proper type hints as required by constitution
- [ ] T042 [US3] Add toggle command to main.py with proper type hints as required by constitution
- [ ] T043 [US3] Add status change indicators (✓/○) to task display functions with proper type hints as required by constitution; show ○ for incomplete tasks and ✓ for complete tasks, reflect status in next list view
- [ ] T044 [US3] Add visual styling for completed tasks (strikethrough/dim) with proper type hints as required by constitution; apply strikethrough and dimmed styling to completed tasks to make them visually distinct in Rich output
- [ ] T045 [US3] Update task count display to reflect completion changes in subsequent list views with proper type hints as required by constitution
- [ ] T046 [US3] Ensure status change feedback appears in console output with proper type hints as required by constitution

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - Update Task (Priority: P2)

**Goal**: Allow users to edit existing task's title and description via modal while preserving ID

**Independent Test**: Select a task, press 'e', modify fields, verify changes persist with same ID and updated timestamp.

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T047 [P] [US4] Unit test for TaskService update_task validation in tests/unit/test_task_service.py
- [ ] T048 [P] [US4] Unit test for TaskStore update_task in tests/unit/test_task_store.py
- [ ] T049 [P] [US4] CLI test for update command in tests/cli/test_update_task.py
- [ ] T050 [P] [US4] CLI test for validation error handling in tests/cli/test_update_task.py

### Implementation for User Story 4

- [ ] T051 [P] [US4] Create update command in main.py with proper type hints as required by constitution; implement task_id argument, optional title and description arguments, validation matching add command (title 1-100 chars, description max 500 chars), validation error display
- [ ] T052 [US4] Add command registration for 'update' in main.py with proper type hints as required by constitution
- [ ] T053 [US4] Implement update_task method in TaskService with validation with proper type hints as required by constitution
- [ ] T054 [US4] Implement update_task method in TaskStore with proper type hints as required by constitution
- [ ] T055 [US4] Add argument validation to update command with proper type hints as required by constitution
- [ ] T056 [US4] Add validation to update command with error display with proper type hints as required by constitution
- [ ] T057 [US4] Connect update command to TaskService for task updates with proper type hints as required by constitution
- [ ] T058 [US4] Add success message ("Task updated") display in update command with proper type hints as required by constitution
- [ ] T059 [US4] Preserve original task ID and set updated_at timestamp with proper type hints as required by constitution
- [ ] T060 [US4] Add command error handling to gracefully handle invalid inputs with proper type hints as required by constitution

**Checkpoint**: At this point, User Stories 1, 2, 3 AND 4 should all work independently

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Allow users to permanently delete tasks with confirmation modal

**Independent Test**: Select a task, press 'd', confirm deletion, verify task is removed and selection adjusted.

### Tests for User Story 5 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T061 [P] [US5] Unit test for TaskService delete_task in tests/unit/test_task_service.py
- [ ] T062 [P] [US5] Unit test for TaskStore delete_task in tests/unit/test_task_store.py
- [ ] T063 [P] [US5] CLI test for delete command in tests/cli/test_delete_task.py
- [ ] T064 [P] [US5] CLI test for task list updates after deletion in tests/cli/test_delete_task.py

### Implementation for User Story 5

- [ ] T065 [P] [US5] Create delete command in main.py with proper type hints as required by constitution; include task_id argument, confirmation prompt "Delete this task? This cannot be undone.", support for confirmation before deletion
- [ ] T066 [US5] Add command registration for 'delete' in main.py with proper type hints as required by constitution
- [ ] T067 [US5] Implement delete_task method in TaskService with proper type hints as required by constitution
- [ ] T068 [US5] Implement delete_task method in TaskStore with proper type hints as required by constitution
- [ ] T069 [US5] Add confirmation prompt with proper message to delete command with proper type hints as required by constitution
- [ ] T070 [US5] Connect delete command to TaskService for task deletion with proper type hints as required by constitution
- [ ] T071 [US5] Add success message ("Task deleted") display in delete command with proper type hints as required by constitution
- [ ] T072 [US5] Update task list display after deletion to reflect removal with proper type hints as required by constitution
- [ ] T073 [US5] Handle empty state when last task is deleted in list command with proper type hints as required by constitution

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T074 [P] Documentation updates in README.md
- [ ] T075 Code cleanup and refactoring across all components with proper type hints as required by constitution
- [ ] T076 Performance optimization for large task lists (100+ tasks) with <50ms latency as required by constitution
- [ ] T077 [P] Additional unit tests to achieve 100% coverage in tests/unit/
- [ ] T078 Rich formatting improvements in src/todo/cli/views/
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
Task: "CLI test for empty state display in tests/cli/test_view_tasks.py"
Task: "CLI test for task list display in tests/cli/test_view_tasks.py"

# Launch all components for User Story 1 together:
Task: "Create task table display function in src/todo/cli/views/table_formatter.py"
Task: "Create task formatting function in src/todo/cli/views/formatters.py"
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