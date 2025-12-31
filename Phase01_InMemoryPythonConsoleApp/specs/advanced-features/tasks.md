# Tasks: Advanced Level Features - Intelligent Task Management

**Input**: Design documents from `specs/advanced-features/`
**Prerequisites**: plan.md (complete), spec.md (complete)

**Tests**: Unit tests are included for core recurrence and reminder logic as per constitution Test-First Development principle.

**Organization**: Tasks are grouped by user story (US1: Recurring Tasks, US2: Due DateTime, US3: Reminders) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/todo/`, `tests/` at repository root
- All paths are relative to `Phase01_InMemoryPythonConsoleApp/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project validation and environment setup

- [ ] T001 Validate existing project structure matches plan requirements
- [ ] T002 Verify Python 3.13+ and UV package manager installed
- [ ] T003 [P] Run existing Level 1/2 test suite to establish baseline

**Checkpoint**: Environment ready, baseline tests passing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model extensions that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create Recurrence enum in src/todo/models/task.py (NONE=0, DAILY=1, WEEKLY=2, MONTHLY=3)
- [ ] T005 Add recurrence field to Task dataclass with default Recurrence.NONE
- [ ] T006 Upgrade Task.due_date field from Optional[date] to Optional[datetime]
- [ ] T007 Update Task.__post_init__() to validate datetime fields if needed
- [ ] T008 Update Task.to_dict() to serialize datetime and recurrence
- [ ] T009 Update Task.from_dict() to deserialize datetime (handle both date and datetime formats) and recurrence
- [ ] T010 Update TaskStore serialization in src/todo/storage/task_store.py to handle datetime
- [ ] T011 Run Level 1/2 regression tests to verify backward compatibility

**Checkpoint**: Foundation ready - Task model extended, all existing tests still pass

---

## Phase 3: User Story 1 - Recurring Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable automatic rescheduling of tasks with daily, weekly, or monthly recurrence patterns

**Independent Test**: Create a recurring task with "weekly" pattern, mark it complete, verify a new instance is automatically created for next week with same attributes

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation (TDD)**

- [ ] T012 [P] [US1] Create tests/unit/test_recurrence.py test file
- [ ] T013 [P] [US1] Write test_daily_recurrence_calculation() - verify +1 day
- [ ] T014 [P] [US1] Write test_weekly_recurrence_calculation() - verify +7 days
- [ ] T015 [P] [US1] Write test_monthly_recurrence_calculation() - verify same day next month
- [ ] T016 [P] [US1] Write test_monthly_edge_case_jan31() - verify Jan 31 → Feb 28/29
- [ ] T017 [P] [US1] Write test_monthly_edge_case_leap_year() - verify Feb 29 → Feb 28 (non-leap)
- [ ] T018 [P] [US1] Write test_monthly_edge_case_dec31() - verify Dec 31 → Jan 31
- [ ] T019 [P] [US1] Write test_recurrence_none_raises_error() - verify ValueError for NONE
- [ ] T020 [P] [US1] Write test_complete_recurring_task_creates_next_instance() in tests/unit/test_recurrence.py
- [ ] T021 [P] [US1] Write test_complete_recurring_preserves_attributes() - title, description, priority, tags
- [ ] T022 [P] [US1] Write test_complete_recurring_generates_new_id() - verify different ID
- [ ] T023 [P] [US1] Write test_complete_non_recurring_no_new_instance() - verify no clone for NONE
- [ ] T024 [P] [US1] Write test_multiple_rapid_completions() - verify sequence of future instances

### Implementation for User Story 1

- [ ] T025 [US1] Implement calculate_next_occurrence(due_date: datetime, recurrence: Recurrence) -> datetime in src/todo/services/task_service.py
- [ ] T026 [US1] Implement DAILY logic: due_date + timedelta(days=1)
- [ ] T027 [US1] Implement WEEKLY logic: due_date + timedelta(weeks=1)
- [ ] T028 [US1] Implement MONTHLY logic with edge case handling (use relativedelta or pure datetime arithmetic)
- [ ] T029 [US1] Add ValueError for Recurrence.NONE in calculate_next_occurrence()
- [ ] T030 [US1] Modify toggle_task_completion() in src/todo/services/task_service.py to check for recurrence
- [ ] T031 [US1] Add auto-reschedule logic: if completed and recurrence != NONE, calculate next occurrence
- [ ] T032 [US1] Implement task cloning logic: create new Task with new ID, next due_date, completed=False
- [ ] T033 [US1] Call add_task() to add cloned task to store
- [ ] T034 [US1] Add --recurring option to add command in main.py (accept none|daily|weekly|monthly)
- [ ] T035 [US1] Add --recurring option to update command in main.py
- [ ] T036 [US1] Add recurrence prompt to handle_add_task() in src/todo/cli/views/menu.py
- [ ] T037 [US1] Create parse_recurrence_input() helper in src/todo/cli/views/menu.py (accept n/d/w/m shortcuts)
- [ ] T038 [US1] Add recurrence option to handle_update_task() in src/todo/cli/views/menu.py
- [ ] T039 [US1] Validate that recurring tasks must have due_date (reject recurrence without due_date)
- [ ] T040 [US1] Add "Recurrence" column to task table in src/todo/cli/views/formatters.py
- [ ] T041 [US1] Display recurrence pattern with visual indicator (e.g., "🔁 Daily", "🔁 Weekly", "🔁 Monthly", "-" for NONE)
- [ ] T042 [US1] Run tests/unit/test_recurrence.py - verify all tests pass
- [ ] T043 [US1] Manual test: Add daily recurring task, complete it, verify tomorrow's instance created
- [ ] T044 [US1] Manual test: Add monthly task due Jan 31, complete, verify Feb 28/29 instance

**Checkpoint**: User Story 1 complete - Recurring tasks fully functional, all tests passing

---

## Phase 4: User Story 2 - Due Date/Time Management (Priority: P2)

**Goal**: Enable time precision for due dates, upgrade from date-only to datetime tracking

**Independent Test**: Create task with "2025-01-15 14:30", list tasks, verify datetime is displayed with time, verify sorting by complete datetime

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation (TDD)**

- [ ] T045 [P] [US2] Create tests/unit/test_datetime.py test file
- [ ] T046 [P] [US2] Write test_parse_datetime_format() - verify "YYYY-MM-DD HH:MM" parsing
- [ ] T046a [P] [US2] Write test_backward_compat_date_only_input() - verify CLI accepts "YYYY-MM-DD" format without requiring time, creates datetime at 00:00, displays correctly, and sorts properly alongside datetime tasks (backward compatibility with Level 2)
- [ ] T047 [P] [US2] Write test_parse_date_only_format() - verify "YYYY-MM-DD" defaults to 00:00
- [ ] T048 [P] [US2] Write test_validate_future_datetime() - verify rejection of past datetimes
- [ ] T049 [P] [US2] Write test_datetime_serialization() - verify to_dict() includes time
- [ ] T050 [P] [US2] Write test_datetime_deserialization() - verify from_dict() handles datetime
- [ ] T051 [P] [US2] Write test_datetime_sorting() - verify sort by complete datetime (not just date)
- [ ] T052 [P] [US2] Write test_overdue_detection() - verify current_datetime > due_date

### Implementation for User Story 2

- [ ] T053 [P] [US2] Create parse_datetime_input(value: str) -> Optional[datetime] helper in src/todo/cli/views/menu.py
- [ ] T054 [P] [US2] Accept both "YYYY-MM-DD HH:MM" and "YYYY-MM-DD" formats in parse_datetime_input()
- [ ] T055 [P] [US2] Default time to 00:00 when only date provided
- [ ] T056 [P] [US2] Create validate_future_datetime(dt: datetime) -> bool helper in src/todo/cli/views/menu.py
- [ ] T057 [US2] Reject past datetimes with error message
- [ ] T058 [US2] Update --due option in add command in main.py to accept datetime format
- [ ] T059 [US2] Update --due option in update command in main.py to accept datetime format
- [ ] T060 [US2] Update due date prompt in handle_add_task() in src/todo/cli/views/menu.py to request datetime
- [ ] T061 [US2] Show example format in prompt: "e.g., 2025-01-15 14:30 or 2025-01-15"
- [ ] T062 [US2] Add validation loop: reject past datetimes, require future datetime
- [ ] T063 [US2] Update due date prompt in handle_update_task() in src/todo/cli/views/menu.py
- [ ] T064 [US2] Update "Due Date" column in src/todo/cli/views/formatters.py to display datetime
- [ ] T065 [US2] Format datetime as "2025-01-15 02:00 PM" when time is not 00:00
- [ ] T066 [US2] Format as "2025-01-15" when time is 00:00 (backward compatibility)
- [ ] T067 [US2] Ensure sort_by="due_date" in search_tasks() sorts by complete datetime
- [ ] T068 [US2] Run tests/unit/test_datetime.py - verify all tests pass
- [ ] T069 [US2] Manual test: Add task with "2025-01-15 14:30", list, verify time displayed
- [ ] T070 [US2] Manual test: Add multiple tasks with different times same day, sort by due_date, verify time order

**Checkpoint**: User Story 2 complete - Datetime precision working, all tests passing

---

## Phase 5: User Story 3 - Reminder Notifications (Priority: P3)

**Goal**: Proactive console-based notifications for overdue and due-soon tasks

**Independent Test**: Create task due in past, launch app, verify overdue reminder displayed in red panel before menu

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation (TDD)**

- [ ] T071 [P] [US3] Create tests/unit/test_reminders.py test file
- [ ] T072 [P] [US3] Write test_no_reminders_all_completed() - verify empty result when all complete
- [ ] T073 [P] [US3] Write test_no_reminders_no_due_dates() - verify empty result when no due_date
- [ ] T074 [P] [US3] Write test_overdue_detection() - verify due_date < now classified as overdue
- [ ] T075 [P] [US3] Write test_due_soon_detection() - verify within 60 minutes classified as due_soon
- [ ] T076 [P] [US3] Write test_boundary_exactly_60_minutes() - verify threshold boundary
- [ ] T077 [P] [US3] Write test_date_only_tasks_excluded() - verify tasks with due_date.time() == time(0,0,0) excluded from reminders
- [ ] T078 [P] [US3] Write test_completed_tasks_excluded() - verify completed=True excluded
- [ ] T079 [P] [US3] Write test_reminder_counts_accurate() - verify overdue_count and due_soon_count

### Implementation for User Story 3

- [ ] T080 [P] [US3] Create ReminderResult dataclass in src/todo/services/results.py
- [ ] T081 [P] [US3] Add fields: overdue_tasks, due_soon_tasks, overdue_count, due_soon_count
- [ ] T082 [US3] Implement check_reminders() -> ReminderResult in src/todo/services/task_service.py
- [ ] T083 [US3] Get current datetime with datetime.now()
- [ ] T084 [US3] Calculate due_soon threshold: now + timedelta(minutes=60)
- [ ] T085 [US3] Filter incomplete tasks with due_date
- [ ] T086 [US3] Classify overdue: due_date < now
- [ ] T087 [US3] Classify due_soon: now <= due_date < threshold
- [ ] T088 [US3] Return ReminderResult with lists and counts
- [ ] T089 [US3] Create humanize_time_diff(td: timedelta) -> str helper in src/todo/cli/views/formatters.py
- [ ] T090 [US3] Format as "X hours Y mins", "X days", or "Y mins" for positive and negative deltas
- [ ] T091 [US3] Create display_reminders(result: ReminderResult) -> None in src/todo/cli/views/formatters.py
- [ ] T092 [US3] Use Rich Panel with title "📋 Reminders", border_style="cyan"
- [ ] T093 [US3] Show overdue count with "⚠️" icon and red styling
- [ ] T094 [US3] List up to 5 overdue tasks with humanized time ("2 hours overdue")
- [ ] T095 [US3] Show due_soon count with "⏰" icon and yellow styling
- [ ] T096 [US3] List up to 5 due_soon tasks with humanized time ("due in 30 min")
- [ ] T097 [US3] Return early (silent) if no reminders exist
- [ ] T098 [US3] Integrate reminder check into main_callback() in main.py (app startup)
- [ ] T099 [US3] Call check_reminders() and display_reminders() before showing interactive menu
- [ ] T100 [US3] Integrate reminder check into list_tasks() command in main.py
- [ ] T101 [US3] Display reminders before task table
- [ ] T102 [US3] Integrate reminder check into handle_list_tasks() in src/todo/cli/views/menu.py
- [ ] T103 [US3] Integrate reminder check into handle_filter_tasks() in src/todo/cli/views/menu.py
- [ ] T104 [US3] Integrate reminder check into handle_search_tasks() in src/todo/cli/views/menu.py
- [ ] T105 [US3] Add overdue styling to task table in src/todo/cli/views/formatters.py
- [ ] T106 [US3] Check if task.due_date < now in format_task_table()
- [ ] T107 [US3] Apply red + bold styling to overdue task rows
- [ ] T108 [US3] Add "⚠️" indicator in Status column for overdue tasks
- [ ] T109 [US3] Apply yellow styling to tasks due within 60 minutes
- [ ] T110 [US3] Run tests/unit/test_reminders.py - verify all tests pass
- [ ] T111 [US3] Manual test: Add task due yesterday, launch app, verify red overdue reminder
- [ ] T112 [US3] Manual test: Add task due in 30 min, launch app, verify yellow due-soon reminder
- [ ] T113 [US3] Manual test: List tasks with overdue, verify red styling in table

**Checkpoint**: User Story 3 complete - Reminder system fully functional, all tests passing

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, help text updates, validation, and documentation

- [ ] T114 [P] Update CLI --help text for add command to document --recurring option
- [ ] T115 [P] Update CLI --help text for add/update commands to document datetime format
- [ ] T116 [P] Update interactive menu help (option 0) in src/todo/cli/views/menu.py
- [ ] T117 [P] Add Level 3 features to help text: recurring tasks, datetime precision, reminders
- [ ] T118 [P] Add error handling for invalid recurrence input with helpful message
- [ ] T119 [P] Add error handling for invalid datetime format with example
- [ ] T120 [P] Add error handling for past datetime with clear rejection message
- [ ] T121 Run full test suite: uv run pytest
- [ ] T122 Verify test coverage >95% for new code: uv run pytest --cov=src --cov-report=html
- [ ] T123 Run type checking: uv run mypy src/todo/
- [ ] T124 Run linting: uv run ruff check src/
- [ ] T125 Fix any linting or type errors
- [ ] T126 Run Level 1/2 regression tests - verify no breaking changes
- [ ] T127 Manual integration test: Full workflow from add recurring task → complete → list with reminders
- [ ] T128 Update README.md with Level 3 features documentation
- [ ] T129 Add usage examples for recurring tasks in README.md
- [ ] T130 Add usage examples for datetime input in README.md
- [ ] T131 Add reminder system description to README.md
- [ ] T132 Update project status to show Level 3 complete

**Checkpoint**: Level 3 implementation complete - All features working, documented, tested

---

## Dependencies & Execution Order

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundation)
                      ↓
    ┌─────────────────┼─────────────────┐
    ↓                 ↓                 ↓
US1 (Recurring)   US2 (DateTime)    US3 (Reminders)
Priority P1       Priority P2       Priority P3
INDEPENDENT       INDEPENDENT       Depends on US2
                                   (needs datetime)
```

**Execution Strategy**:
- **Sequential Phases**: Phase 1 → Phase 2 must complete first
- **Parallel User Stories**: US1 and US2 can be implemented in parallel after Phase 2
- **US3 Dependency**: US3 requires US2 complete (needs datetime field)
- **MVP Delivery**: Complete US1 first for minimum viable product

### Parallel Execution Opportunities

**Within Phase 2 (Foundation)**:
- T004-T010 can mostly run in parallel (different aspects of Task model)
- T011 must wait for all others

**Within US1 (Recurring Tasks)**:
- T012-T024: All test writing tasks can run in parallel (13 tasks)
- T025-T029: Recurrence calculation can run while T030-T033 wait
- T034-T038: CLI input tasks can run in parallel (5 tasks)
- T040-T041: Display tasks can run in parallel with CLI tasks

**Within US2 (DateTime)**:
- T045-T052: All test writing tasks can run in parallel (8 tasks)
- T053-T056: Helper functions can run in parallel (4 tasks)
- T058-T063: CLI input updates can run in parallel (6 tasks)
- T064-T066: Display updates can run in parallel (3 tasks)

**Within US3 (Reminders)**:
- T071-T079: All test writing tasks can run in parallel (9 tasks)
- T080-T081: ReminderResult dataclass independent
- T089-T090: Humanize helper independent
- T098-T104: Integration points can run in parallel once T082-T097 complete
- T105-T109: Table styling can run in parallel

**Within Phase 6 (Polish)**:
- T114-T120: All documentation and error handling tasks can run in parallel (7 tasks)

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**MVP = Phase 1 + Phase 2 + Phase 3 (US1 only)**

Delivers:
- Recurring task creation and automatic rescheduling
- Basic functionality fully testable
- Immediate user value (eliminates manual task recreation)

**Timeline**: ~40 tasks (T001-T044)

### Incremental Delivery

1. **Sprint 1**: MVP (US1) - Recurring tasks
2. **Sprint 2**: US2 - Datetime precision
3. **Sprint 3**: US3 - Reminders (depends on US2)
4. **Sprint 4**: Polish and documentation

### Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundation)**: 8 tasks
- **Phase 3 (US1)**: 32 tasks (13 tests + 19 implementation)
- **Phase 4 (US2)**: 26 tasks (8 tests + 18 implementation)
- **Phase 5 (US3)**: 43 tasks (9 tests + 34 implementation)
- **Phase 6 (Polish)**: 19 tasks

**Total**: 132 tasks

### Parallel Opportunities Summary

- **Test Writing**: 30 test tasks can run in parallel (T012-T024, T045-T052, T071-T079)
- **CLI Input**: 15 input-related tasks can run in parallel across US1/US2
- **Display**: 8 display tasks can run in parallel
- **Documentation**: 7 polish tasks can run in parallel

**Estimated Parallelization**: ~60 tasks (45%) can run in parallel with proper coordination

---

## Validation Checklist

Before considering implementation complete, verify:

- [ ] All 132 tasks completed
- [ ] All unit tests passing (100% for new code)
- [ ] Level 1/2 regression tests passing (no breaking changes)
- [ ] Type checking passes (mypy strict mode)
- [ ] Linting passes (ruff with no errors)
- [ ] Manual testing checklist complete (recurring, datetime, reminders)
- [ ] All 8 success criteria from spec.md validated
- [ ] Help text updated and accurate
- [ ] README.md updated with Level 3 features
- [ ] PHRs created for all significant AI interactions

---

**Next Step**: Begin implementation with Phase 1 (Setup) tasks T001-T003, then proceed to Phase 2 (Foundation).
