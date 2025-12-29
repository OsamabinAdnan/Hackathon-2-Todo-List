---
id: 003
title: Agents and Skills TUI Alignment
stage: constitution
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: osamabinadnan
command: conversation
labels: ["constitution", "tui", "textual", "agents", "skills", "alignment"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/python-todo-architect.md
  - .claude/agents/testing-expert.md
  - .claude/skills/advanced-feature-implementation/SKILL.md
  - .claude/skills/runtime-state-management/SKILL.md
  - .claude/skills/basic-feature-testing/SKILL.md
  - .claude/skills/intermediate-feature-testing/SKILL.md
  - .claude/skills/advanced-feature-testing/SKILL.md
  - .claude/skills/edge-case-testing/SKILL.md
  - .claude/skills/regression-testing/SKILL.md
  - .claude/skills/in-memory-state-validation/SKILL.md
tests:
  - null
---

## Prompt

User requested to "check all agents and skills for last constitution update" before creating TUI agents and skills. The constitution was updated from v1.0.0 to v1.1.0, changing from CLI (Typer) to TUI (Textual) approach.

## Response snapshot

Reviewed and updated all agents and skills for TUI compatibility:

**Agents Updated:**
- `python-todo-architect.md`: Changed specialization from "console-based applications" to "Textual TUI applications", updated file organization from CLI to TUI structure, added TUI Architecture section with component hierarchy and keyboard bindings
- `testing-expert.md`: Changed from "console applications" to "Textual TUI applications", added `textual.testing` to Primary Tools, updated test structure with `tui/` directory, added TUI testing patterns with AppTester examples

**Implementation Skills Updated:**
- `advanced-feature-implementation`: Changed "console-based reminders" to "TUI-based notifications", updated check_reminders() to return list for TUI display, added TUI component examples (ReminderNotification, ReminderPanel, ReminderModal)
- `runtime-state-management`: Changed from CLI integration patterns to TUI integration patterns, added reactive state binding patterns, message-based state updates, TUI testing with AppTester

**Testing Skills Updated:**
- `basic-feature-testing`: Added TUI Testing Patterns section with CRUD operations via TUI (AddTaskTUI, ToggleCompleteTUI)
- `intermediate-feature-testing`: Added TUI Testing Patterns for filter/search via TUI (SearchTUI, PriorityFilterTUI, TagFilterTUI)
- `advanced-feature-testing`: Added TUI Testing Patterns for reminders and due dates (ReminderNotificationsTUI, RecurringTasksTUI, DueDateDisplayTUI)
- `edge-case-testing`: Added TUI Edge Case Testing section (EmptyStateTUI, ValidationErrorsTUI, KeyboardEdgeCases)
- `regression-testing`: Added TUI Regression Testing Patterns (TUIKeyboardStability, TUIReactiveUpdates, TUIBugFixes)
- `in-memory-state-validation`: Added TUI State Validation Patterns (TUIStateIsolation, TUIReactiveState, TUIStatePersistence, TUIServiceInjection)

## Outcome

- Impact: All agents and skills now aligned with TUI paradigm
- Tests: Added textual.testing patterns to all 6 testing skills
- Files: 10 files modified (2 agents, 8 skills)
- Next prompts: Create tui-components skill with dedicated TUI patterns
- Reflection: Comprehensive update ensures consistency across entire codebase for TUI development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - alignment update
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create tui-components skill to centralize TUI widget patterns
