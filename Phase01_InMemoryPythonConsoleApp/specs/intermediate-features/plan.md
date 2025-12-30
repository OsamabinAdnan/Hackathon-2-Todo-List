# Implementation Plan: Phase 1 Level 2 - Intermediate Features (Organization & Usability)

**Branch**: `main` | **Date**: 2025-12-30 | **Spec**: [specs/intermediate-features/spec.md](spec.md)
**Input**: Feature specification from `/specs/intermediate-features/spec.md`

## Summary

Enhance the Phase 1 Todo application by implementing organization and usability features: **Priorities**, **Tags**, **Search**, **Filtering**, and **Sorting**.

The technical approach involves:
- Extending the `Task` model with `priority` (Enum), `tags` (List), and `due_date`.
- Updating `TaskStore` and `TaskService` to handle new attributes and implement search/filter/sort logic.
- Enhancing the Typer CLI with new command options and a dedicated `search` command.
- Integrating these features into the existing interactive menu system using Rich for stylized output.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Typer, Rich
**Storage**: In-memory dictionary (TaskStore)
**Testing**: pytest (unit and CLI)
**Target Platform**: Windows (WSL2/PowerShell)
**Project Type**: Python CLI
**Performance Goals**: <50ms latency for all operations on lists up to 100 tasks.
**Constraints**: No new external dependencies; strictly build on existing Phase 1 architecture.
**Scale/Scope**: intermediate task management for individual users.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Smallest viable change: Building directly on the existing `Task` and `TaskService`.
- [x] Type Hints: All new code will use strict Python type hints.
- [x] Clean Architecture: Maintains separation between Models, Services, Storage, and CLI.

## Project Structure

### Documentation (this feature)

```text
specs/intermediate-features/
├── plan.md              # This file
├── spec.md              # Feature specification
├── tasks.md             # Implementation tasks
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code

```text
src/todo/
├── models/
│   └── task.py          # Updated with Priority Enum and tags
├── services/
│   ├── task_service.py  # Updated with search/filter/sort logic
│   └── results.py       # Updated with new result types if needed
├── storage/
│   └── task_store.py    # Updated to store new attributes
└── cli/
    ├── views/
    │   ├── formatters.py # Updated for Priority/Tags columns
    │   └── menu.py       # Updated with search/filter/sort options
    └── main.py          # Updated Typer app with new commands/options
```

**Structure Decision**: Single project structure (Phase 1 standard).

## Key Decisions and Rationale

1. **Enum for Priority**:
   - **Rationale**: Provides type safety and prevents invalid string inputs at the service layer.
   - **Trade-off**: Slightly more boilerplate but much easier to maintain and sort.

2. **Due Date as datetime.date**:
   - **Rationale**: Simplifies comparison and sorting without dealing with time-zones or hours for basic level features.

3. **Comma-Separated Tag Parsing**:
   - **Rationale**: Best UX for CLI `add --tags "work,urgent"` where user can type a single string.
   - **Internal Storage**: `Set[str]` for uniqueness and fast lookups.

4. **Cumulative "AND" Filtering**:
   - **Rationale**: Standard expected behavior for business apps. Filtering for "priority=high" AND "status=incomplete" is more useful than "OR".

5. **Sorting Logic**:
   - **Priority Sort**: Map enum members to integers (High=3, Medium=2, Low=1, None=0) for predictable numeric sorting.
   - **Secondary Sort**: Always fall back to `id` (creation order) for stable results when primary fields match.

## Risk Analysis and Mitigation

1. **CLI Table Width**:
   - **Risk**: Adding columns (Priority, Tags) may cause table wrapping on small terminals.
   - **Mitigation**: Use Rich's overflow handling (e.g., `truncate` or `no_wrap` on specific columns) and shorten headers.

2. **Parsing Complexity**:
   - **Risk**: User input for dates can be tricky.
   - **Mitigation**: Standard ISO format (YYYY-MM-DD) for initial implementation; use `datetime.date.fromisoformat`.

3. **Menu Bloat**:
   - **Risk**: Adding too many menu items makes navigation difficult.
   - **Mitigation**: Create a "Search/Filter" sub-menu if the main menu exceeds 8 items.

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
