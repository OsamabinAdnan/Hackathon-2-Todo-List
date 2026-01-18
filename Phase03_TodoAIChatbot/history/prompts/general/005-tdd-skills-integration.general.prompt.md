---
id: 005
title: "TDD Testing Specialist Skills Integration"
stage: "general"
date_iso: "2026-01-03"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "assistant"
command: "create-skills"
labels: ["tdd", "testing", "skills", "agent", "integration"]
links: {"spec": null, "ticket": null, "adr": null, "pr": null}
files_yaml: |
  - .claude/skills/test-generation/skill.md
  - .claude/skills/test-execution-analysis/skill.md
  - .claude/skills/tdd-iteration-refactor/skill.md
  - .claude/agents/tdd-testing-specialist.md
tests_yaml: |
  - "N/A - Configuration work"
prompt_text: |
  Create three skills for the tdd-testing-specialist agent:
  1. Test Generation Skill - Create comprehensive test specs first describing unit/integration/E2E scenarios using pytest (FastAPI/SQLModel) and Vitest/React Testing Library (Next.js). Cover edge cases like auth failures, recurring tasks, priorities, filters, and browser notifications. Output failing test outlines tied to features for red phase.
  2. Test Execution and Analysis Skill - Run full test suites (pytest for backend, Vitest for frontend) after code regeneration; capture outputs, coverage reports, and failures. Analyze errors (e.g., JWT mismatches, query inefficiencies, UI render bugs) with stack traces and suggestions. Report pass/fail status, coverage metrics, and prioritized failures for main agent delegation.
  3. TDD Iteration and Refactor Skill - Upon test failures, generate refined Markdown specs for domain subagents to implement green/refactor phases. Suggest refactors for cleaner code (e.g., modular components, optimized SQLModel queries) while preserving intent. Loop with code reviewer until 100% pass rate; enforce no manual edits, full spec-driven compliance for hackathon judging.
response_text: |
  Successfully created three comprehensive skills for the tdd-testing-specialist agent:
  1. Test Generation Skill - Includes backend and frontend test examples, edge case coverage for authentication, recurring tasks, priorities, and filters, E2E test generation with Playwright, test data factory generation, coverage-driven test generation, and red phase test outlines.
  2. Test Execution and Analysis Skill - Includes backend test execution (pytest), frontend test execution (Vitest), E2E test execution (Playwright), output capture and analysis with error classification, JWT error analysis, database error analysis, UI/React error analysis, coverage analysis, and comprehensive test reports.
  3. TDD Iteration and Refactor Skill - Includes failure-driven spec refinement with Markdown generation, refactoring suggestions for code quality improvement, database query optimization examples with SQLModel, test-driven refactoring loop with automated processes, code review integration, and spec-driven compliance verification.
  All skills were properly integrated into the tdd-testing-specialist agent with correct paths, trigger keywords, and purposes. Invalid references were fixed to point to actual project files.
outcome: "Successfully created and integrated three skills for the tdd-testing-specialist agent with proper configuration and documentation."
evaluation: "All three skills are properly configured and ready for use in Test-Driven Development workflows."
---

# TDD Testing Specialist Skills Integration

## Summary
Created three comprehensive skills for the tdd-testing-specialist agent to support Test-Driven Development workflows in the Hackathon II Phase 2 project. The skills cover test generation, execution/analysis, and iteration/refactoring phases of the TDD cycle.

## Changes Made
1. Created test-generation skill with comprehensive test creation capabilities
2. Created test-execution-analysis skill for running and analyzing test suites
3. Created tdd-iteration-refactor skill for handling test failures and refactoring
4. Integrated all three skills into the tdd-testing-specialist agent
5. Fixed invalid references in skills to point to actual project files

## Files Created/Modified
- .claude/skills/test-generation/skill.md
- .claude/skills/test-execution-analysis/skill.md
- .claude/skills/tdd-iteration-refactor/skill.md
- .claude/agents/tdd-testing-specialist.md

## Verification
All skills are properly configured with correct paths, trigger keywords, and purposes. The tdd-testing-specialist agent now has access to these skills for comprehensive TDD support.