---
id: 002
title: Constitution Update - CLI to TUI Migration
stage: constitution
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: osamabinadnan
command: conversation
labels: ["constitution", "tui", "textual", "architecture-change"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .claude/skills/modular-code-generation/SKILL.md
tests:
  - null
---

## Prompt

User requested to switch from CLI (Typer) approach to TUI (Textual) approach for the Todo console application. User asked: "First tell me can i used TUI approach for my todo console in-memory python app?" and after receiving options, chose option 2 (Switch to TUI approach).

## Response snapshot

Updated constitution from v1.0.0 to v1.1.0 with the following changes:

**Modified Principle V**: Changed from "Rich CLI User Experience" to "Textual TUI Experience"
- Replaced Typer CLI framework with Textual TUI framework
- Added reactive UI updates, keyboard navigation, mouse support
- Added in-app notifications/modals for error handling
- Added keyboard shortcuts discoverability requirement

**Modified Technology Standards**:
- CLI Framework: Typer -> TUI Framework: Textual
- Output Formatting: Rich -> Styling/Formatting: Rich (via Textual)
- Testing: pytest -> pytest + textual.testing
- State Management: Added "with reactive bindings"

**Modified Project Structure**:
- Replaced `cli/` directory with `tui/` directory
- Added subdirectories: screens/, components/, modals/, styles/
- Added tests/tui/ for TUI-specific tests

**Added TUI Architecture Guidelines**:
- Component hierarchy (TodoApp -> MainScreen -> TaskListView -> TaskItem)
- Reactive data flow pattern
- Keyboard navigation mapping (a, e, d, space, p, t, /, ?, q, j/k)

**Modified Performance Requirements**:
- TUI startup time: under 1 second
- Added UI responsiveness requirement
- Added smooth scrolling for 100+ items

Also updated `modular-code-generation` skill with TUI patterns including:
- Textual App, Screen, Widget templates
- Modal dialog patterns
- TCSS stylesheet examples
- Message pattern for component communication
- Reactive attribute patterns

## Outcome

- Impact: Major architectural change from CLI to TUI paradigm
- Tests: TUI tests will use textual.testing framework
- Files: 2 files modified (constitution.md, modular-code-generation/SKILL.md)
- Next prompts: Review and update remaining agents/skills for TUI compatibility
- Reflection: Constitution versioning (1.0.0 -> 1.1.0) properly documented with SYNC IMPACT REPORT

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - constitution update
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create tui-components skill and update remaining skills/agents
