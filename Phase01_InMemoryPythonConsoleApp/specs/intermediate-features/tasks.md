---
description: "Task list for Intermediate Features (Organization & Usability) implementation"
---

# Tasks: Intermediate Features

**Input**: Design documents from `/specs/intermediate-features/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Unit tests for core functions included as requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Application structure**: `src/todo/models/`, `src/todo/services/`, `src/todo/storage/`, `src/todo/cli/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project state preparation

- [ ] T001 Verify existing Phase 1 environment and dependencies (Typer, Rich, UV)
- [ ] T002 [P] Create directory structure for checklists if missing in specs/intermediate-features/checklists/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model and service enhancements that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Define Priority Enum in src/todo/models/task.py with values HIGH, MEDIUM, LOW, NONE
- [ ] T004 Update Task dataclass in src/todo/models/task.py to include priority (Enum), tags (Set[str]), and due_date (Optional[date]) with proper type hints
- [ ] T005 Update TaskStore in src/todo/storage/task_store.py to support storing and retrieving the new task attributes
- [ ] T006 Update TaskService in src/todo/services/task_service.py to handle new attributes in add/update methods with proper validation (including 20-char limit per tag)
- [ ] T007 [P] Create result types for search/filter operations in src/todo/services/results.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Categorize Tasks (Priority: P1) 🎯 MVP

**Goal**: Assign priorities and tags to tasks with visual color-coding in the CLI

**Independent Test**: Add/Update a task with priority/tags and verify they appear correctly in the task list with colors.

### Tests for User Story 1
- [ ] T008 [P] [US1] Unit test for Priority Enum and Task model updates in tests/unit/test_task_models.py
- [ ] T009 [P] [US1] Unit test for TaskService add/update with metadata in tests/unit/test_task_service.py

### Implementation for User Story 1
- [ ] T010 [US1] Update `add` command in main.py to support `--priority` and `--tags` options with validation
- [ ] T011 [US1] Update `update` command in main.py to support modifying priority and tags
- [ ] T012 [US1] Update table formatter in src/todo/cli/views/formatters.py to include Priority and Tags columns
- [ ] T013 [US1] Implement priority color-coding logic in src/todo/cli/views/formatters.py (High=Red, Medium=Yellow, Low=Green)
- [ ] T014 [US1] Update interactive menu "Add Task" and "Update Task" flows in src/todo/cli/views/menu.py to include priority/tags prompts

**Checkpoint**: User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Filter and Search (Priority: P1)

**Goal**: Find tasks by keyword, status, priority, or tags

**Independent Test**: Run search/filter commands and verify only matching tasks are displayed.

### Tests for User Story 2
- [ ] T015 [P] [US2] Unit test for TaskService search/filter logic in tests/unit/test_task_service.py
- [ ] T016 [P] [US2] CLI test for search command in tests/cli/test_search.py

### Implementation for User Story 2
- [ ] T017 [US2] Implement search/filter logic in TaskService (src/todo/services/task_service.py) with cumulative AND logic
- [ ] T018 [US2] Create new `search` command in main.py supporting keyword, priority, and tag filters
- [ ] T019 [US2] Update `list` command in main.py to support filtering by status, priority, and tags
- [ ] T020 [US2] Implement "Clear filters" functionality in list/search commands and interactive menu
- [ ] T021 [US2] Add "Search Tasks" and "Filter Tasks" options to interactive menu in src/todo/cli/views/menu.py

---

## Phase 5: User Story 3 - Sort Task List (Priority: P2)

**Goal**: View tasks sorted by priority, date, or title

**Independent Test**: Run list with sort options and verify correct ordering.

### Tests for User Story 3
- [ ] T022 [P] [US3] Unit test for sorting logic in TaskService (tests/unit/test_task_service.py)

### Implementation for User Story 3
- [ ] T023 [US3] Implement sorting logic in TaskService (src/todo/services/task_service.py) with priority mapping (High=3 to None=0)
- [ ] T024 [US3] Update `list` command in main.py to support `--sort` option (priority, date, title)
- [ ] T025 [US3] Add "Sort List" option or prompt to the interactive menu in src/todo/cli/views/menu.py

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements

- [ ] T026 [P] Update README.md with new Level 2 commands and usage examples
- [ ] T027 Code refactoring for consistency and adherence to Constitution
- [ ] T028 Final manual testing of the full integrated CLI and Menu system
- [ ] T029 Performance check for filtering/sorting with 50+ tasks

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 & 2**: MUST be completed first as they define the new data shape.
- **User Stories**: US1 is the highest priority (P1) and provides the metadata needed for US2 and US3.
- **US2 & US3**: Can be implemented in parallel once US1 and Foundation are ready.

### Parallel Opportunities

- T008, T009 (US1 Tests) can run in parallel.
- T015, T016 (US2 Tests) can run in parallel.
- Different developers can work on US2 (Search) and US3 (Sort) simultaneously.

---

## Implementation Strategy

### MVP First
1. Complete Foundational (Phase 2)
2. Complete US1 (Categorize)
3. Validate: Verify tasks can be added with priority/tags and appear in the list.

### Incremental Delivery
1. Add Search/Filter (US2)
2. Add Sort (US3)
3. Final Polish and Docs.
