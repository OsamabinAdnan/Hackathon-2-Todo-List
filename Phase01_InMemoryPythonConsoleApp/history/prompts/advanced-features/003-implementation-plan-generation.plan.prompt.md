---
id: 003
title: Implementation Plan Generation
stage: plan
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5-20250929
feature: advanced-features
branch: main
user: OsamabinAdnan
command: /sp.plan
labels: ["planning", "architecture", "recurring-tasks", "reminders", "datetime"]
links:
  spec: specs/advanced-features/spec.md
  plan: specs/advanced-features/plan.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/advanced-features/plan.md
 - history/prompts/advanced-features/003-implementation-plan-generation.plan.prompt.md
tests:
 - N/A (planning phase, no tests yet)
---

## Prompt

```
/sp.plan

Level 3 Advanced Level Features: Intelligent Features for Phase I Todo In-Memory Python Console App

Create: Extended Task model with recurrence (enum type and optional interval), due_datetime as datetime.datetime, modified mark-complete logic to auto-create rescheduled task instance, reminder detection logic (overdue/soon), enhanced list command to show reminders and recurrence info, Rich styling for overdue/highlights, spec files in specs/advanced-features/, unit tests for recurrence rescheduling and reminder checks.

Integrated Level 3 features in the existing CLI (Level 1 and Level 2 already implemented). Level 3 features should be integrated and work perfectly within the interactive menu system as well.

Decisions needing documentation:
- Recurrence model (simple Enum: daily/weekly/monthly vs flexible timedelta; choose Enum for simplicity/no deps); Due field (upgrade from date to datetime.datetime for time support);
- Auto-reschedule behavior (clone task with new due + period, keep original completed vs replace; choose clone+add new for history);
- Reminder thresholds (overdue: now > due, soon: within 1 hour; configurable? fixed for simplicity);
- Notification method (console print with Rich highlight on list/start vs os.system notify; choose Rich print to avoid platform issues/no deps);
- Trigger reminders (on every list command + app entry vs separate remind command; integrate into list/start).

Testing strategy:
- Manual CLI testing (add recurring task with due time, mark complete and verify new instance appears with shifted due, set past/near-future dues and check list shows overdue/soon warnings);
- Pytest unit tests for reschedule calculation (weekly +7 days etc.), reminder classification, datetime parsing/validation;
- Edge cases (no recurrence, no due, invalid inputs, multiple completions); Validate full integration and styling per success criteria; Record <90s demo video showing recurring reschedule and reminder display.

Technical details:
- Use iterative spec refinement: Break spec into model, add/update, complete logic, display/reminders sections for Claude Code
- Folder structure: Specs in specs/advanced-features/, code updates in /src/todo (models.py, storage.py if needed, cli commands especially complete.py and list.py), main.py for entry reminders
- Claude workflow: Provide spec section + current code context per sub-task, refine generations until correct, log all prompts/results in CLAUDE.md
- Organize by sub-tasks:
    1. Model extension (recurrence enum, due_datetime),
    2. Add/update command options (recurring choice, datetime input with format validation),
    3. Mark-complete overhaul (auto-reschedule clone logic),
    4. Reminder detection function (overdue/soon checks using datetime.now()),
    5. List command enhancements (new columns for recurrence/due time, Rich coloring for reminders/overdue),
    6. App entry reminder summary (print on startup),
    7. Unit tests generation,
    8. Integration, error handling, help text updates
- Research if needed: Stdlib datetime/timedelta examples or platform-neutral console bell/beep if enhancing notifications (but stick to Rich print)
```

## Response snapshot

**Created Comprehensive Implementation Plan** for Level 3 Advanced Features with:

### Architectural Decision Records (6 ADRs):

1. **ADR-001: Recurrence Model Design** - Simple Enum (DAILY/WEEKLY/MONTHLY) chosen over flexible timedelta or cron expressions
2. **ADR-002: Due Date Field Upgrade Strategy** - Upgrade due_date from date to datetime with backward compatibility
3. **ADR-003: Auto-Reschedule Behavior** - Clone-and-add pattern preserves history, keeps completed task
4. **ADR-004: Reminder Detection Strategy** - Fixed thresholds (overdue: now > due, soon: within 60 min)
5. **ADR-005: Notification Display Method** - Rich console panels with color-coded styling
6. **ADR-006: Reminder Trigger Points** - App startup + list operations (not every command)

### Implementation Phases (8 phases):

0. **Research & Validation** - Validate datetime edge cases, month-end calculations
1. **Data Model Extension** - Add Recurrence enum, upgrade due_date to datetime
2. **Recurrence Calculation Logic** - Implement next occurrence calculator with edge cases
3. **Auto-Reschedule on Completion** - Clone task logic in toggle_task_completion
4. **Reminder Detection Service** - Implement check_reminders() with ReminderResult
5. **CLI Input Enhancement** - Add --recurring option, datetime format support
6. **Display Enhancements** - Recurrence column, datetime formatting, overdue styling
7. **Reminder Display Integration** - Rich panels on startup and list operations
8. **Testing & Validation** - Unit tests, integration tests, manual testing, success criteria validation

### Technical Specifications:

- **Language**: Python 3.13+
- **Dependencies**: No new deps (stdlib datetime/timedelta, existing Typer/Rich)
- **Storage**: In-memory dictionary (Phase 1 constraint)
- **Performance Goals**: <5s reschedule, <1s reminder display, 100% edge case handling
- **Testing**: pytest unit tests, manual CLI testing checklist, success criteria validation

### Risk Analysis:

Identified 5 high-impact risks with mitigation strategies:
- Month-end edge cases → comprehensive tests first
- Datetime upgrade breaks Level 2 → backward compatibility design
- Performance degradation → O(n) acceptable for Phase 1
- Infinite loops → safeguards in reschedule logic
- Terminal compatibility → Rich fallback handling

### Integration Points:

- Extends existing codebase (models, services, CLI views)
- No breaking changes to Level 1/2
- Full backward compatibility maintained
- Interactive menu integration throughout

## Outcome

- ✅ Impact: Created comprehensive 8-phase implementation plan with 6 ADRs documenting all major decisions, risk analysis, testing strategy, and success criteria validation
- 🧪 Tests: Defined test strategy (unit tests for recurrence/reminders, integration tests, manual testing checklist)
- 📁 Files: Created specs/advanced-features/plan.md (detailed implementation plan)
- 🔁 Next prompts: Run /sp.tasks to generate detailed implementation tasks from this plan
- 🧠 Reflection: Plan is comprehensive and well-structured with clear phases, ADRs documenting all decisions, risk mitigation, and testing strategy. Ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All planning criteria met
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.tasks to break down phases into actionable implementation tasks
