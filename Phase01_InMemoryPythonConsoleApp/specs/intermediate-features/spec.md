# Feature Specification: Phase 1 Level 2 - Intermediate Features (Organization & Usability)

**Feature Branch**: `main` (Intermediate Features)
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Level 2 Intermediate Level Features: Organization & Usability for Phase I Todo In-Memory Python Console App. Focus: Enhance basic todo app with priorities, tags, search/filter, and sort capabilities."

## Overview

This specification extends the Phase 1 Todo application with organization and usability features. The goal is to transform the basic CRUD app into a more powerful productivity tool by adding **Priorities**, **Tags**, **Search/Filter**, and **Sorting** capabilities.

The application remains an in-memory Typer CLI with Rich formatting, ensuring high performance and a polished user interface.

## Clarifications

### Session 2025-12-30

- Q: Should the interactive menu also be updated with Level 2 features? → A: Yes, integrate Level 2 features (Search, Filter, Sort) into the existing interactive menu system.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Categorize Tasks with Priorities and Tags (Priority: P1)

As a user, I want to assign priorities (High, Medium, Low) and multiple tags to my tasks so that I can categorize and identify urgent items at a glance.

**Why this priority**: Categorization is the foundation for search, filter, and sort. Without metadata, organization features cannot function.

**Independent Test**: Add a task with a priority and tags, then view the list to ensure they are displayed correctly with visual styling (colors for priorities).

**Acceptance Scenarios**:

1. **Given** the `add` command, **When** user provides a priority (e.g., `--priority high`), **Then** the task is created with that priority and displayed with color-coding (e.g., Red for High, Yellow for Medium, Green for Low)
2. **Given** the `add` command, **When** user provides multiple tags (e.g., `--tags work,urgent`), **Then** the task stores these tags and displays them as a comma-separated list or distinct labels in the task view
3. **Given** an existing task, **When** user runs `update` with a new priority or updated tags, **Then** the task metadata is updated correctly

---

### User Story 2 - Filter and Search Tasks (Priority: P1)

As a user, I want to filter tasks by status, priority, or tags, and search by keywords in title/description so that I can quickly find relevant tasks in a large list.

**Why this priority**: Essential for usability when the task list grows beyond a few items. Provides the "Organization" promised in the requirements.

**Independent Test**: Use the `search` or `list` command with filter arguments (e.g., `--priority high --status incomplete`) and verify only matching tasks are displayed.

**Acceptance Scenarios**:

1. **Given** a list of tasks with varied priorities, **When** user filters by `high` priority, **Then** only High priority tasks are shown
2. **Given** tasks with tags, **When** user filters by a specific tag (e.g., `--tag work`), **Then** only tasks containing that tag are shown
3. **Given** a task with title "Buy milk", **When** user searches for keyword "milk", **Then** that task is returned in the results

---

### User Story 3 - Sort Task List (Priority: P2)

As a user, I want to sort my task list by creation date, priority, or title so that I can view my todos in the order that makes the most sense for my workflow.

**Why this priority**: Improves usability by allowing users to bring important or related tasks together, though filtering is often more powerful for finding specific items.

**Independent Test**: Run the list command with sort arguments (e.g., `--sort priority`) and verify the order of displayed tasks matches the expected sorting logic.

**Acceptance Scenarios**:

1. **Given** tasks with different priorities, **When** user sorts by priority (Descending), **Then** High priority tasks appear at the top
2. **Given** tasks created at different times, **When** user sorts by date (Newest first), **Then** the most recently added tasks appear first
3. **Given** tasks with various titles, **When** user sorts by title (A-Z), **Then** tasks are listed alphabetically

---

### Edge Cases

- **Invalid Priority**: What happens when user enters an invalid priority level? → System MUST reject with a helpful message: "Invalid priority. Use: high, medium, low."
- **Empty Search**: How does system handle a search keyword that matches nothing? → System MUST display: "No tasks found matching your search criteria."
- **Multiple Filters**: How does system handle conflicting filters? → System MUST apply filters cumulatively (AND logic).
- **Tag Formatting**: How are tags handled if user includes extra spaces? → System MUST trim whitespace and deduplicate tags.
- **Sorting Tied Values**: How are tasks ordered when they have the same priority/date? → Fall back to secondary sort by ID (creation order).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support three priority levels: High, Medium, Low (represented by an Enum).
- **FR-002**: System MUST allow adding/updating multiple tags (case-insensitive) for any task.
- **FR-003**: System MUST display Priority and Tags in the main task list table.
- **FR-004**: System MUST color-code priorities in the CLI (High=Red, Medium=Yellow, Low=Green, None=Default).
- **FR-005**: System MUST implement a `search` command that filters by keyword in title and description.
- **FR-006**: System MUST allow filtering the `list` command by status (complete/incomplete), priority, or tags.
- **FR-007**: System MUST allow sorting the task list by: Priority (High to Low), Created Date (Newest/Oldest), and Title (A-Z/Z-A).
- **FR-008**: System MUST support cumulative filtering (e.g., "incomplete tasks with high priority").
- **FR-009**: System MUST support a "Clear filters" or "Reset" mechanism to view all tasks again.
- **FR-010**: System MUST validate tag length (e.g., max 20 characters per tag).

### Key Entities

- **Task (Enhanced)**:
  - `priority`: Enum (High, Medium, Low, None)
  - `tags`: Set of strings (unique, case-insensitive)
  - `due_date`: Optional date (ISO 8601 YYYY-MM-DD, for future-proofing)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can filter a list of 50 tasks by priority and tags in <50ms.
- **SC-002**: Search keyword results return exact matches in title and description 100% of the time.
- **SC-003**: Task list table effectively displays 5+ columns (ID, Title, Priority, Tags, Status) without wrapping on standard 80-char terminals.
- **SC-004**: Zero regressions in Basic CRUD functionality (Add/View/Update/Delete/Toggle still work perfectly).
- **SC-005**: All CLI commands for intermediate features are fully discoverable via `--help`.

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
