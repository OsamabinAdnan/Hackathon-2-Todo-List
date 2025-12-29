---
id: 005
title: UV Package Management Skill Creation
stage: constitution
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: osamabinadnan
command: conversation
labels: ["constitution", "uv", "package-management", "skill", "tooling"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/uv-package-management/SKILL.md
  - .claude/agents/python-todo-architect.md
tests:
  - null
---

## Prompt

User asked whether to create a separate agent or skill for UV package manager, stating: "I want to do this project using UV package manager, all working, dependencies, installation will be done using uv?"

## Response snapshot

Recommended creating a **skill** instead of an agent because:

| Factor | Skill (Recommended) | Agent |
|--------|---------------------|-------|
| Scope | UV is supporting tool | Agents own entire domains |
| Frequency | Used occasionally | Continuous work |
| Integration | Supports architect's work | Separate decision-making |
| Complexity | Straightforward patterns | Complex reasoning |

Created `uv-package-management` skill (400+ lines) with comprehensive patterns:

**Project Setup:**
- `uv init` initialization
- pyproject.toml full template for Todo app
- Directory structure creation
- `.python-version` pin

**Dependency Management:**
- `uv add textual rich` for core dependencies
- `uv add --dev pytest pytest-asyncio pytest-cov ruff mypy` for dev dependencies
- `uv remove`, `uv sync`, `uv lock` commands
- Dependency groups pattern (`[project.optional-dependencies]`)
- Lock file handling (`uv.lock`)

**Virtual Environment:**
- `uv venv` creation
- Activation (optional with `uv run`)
- Python version specification

**Running Commands:**
- `uv run python` for scripts
- `uv run pytest` for tests with various options
- `uv run todo` for application entry point
- `uv run ruff check/format` for linting

**pyproject.toml Configuration:**
- Full template with all tool sections
- pytest configuration with markers
- coverage configuration
- ruff linting rules
- mypy strict mode
- hatchling build system
- Entry points for CLI

**Workflows:**
- Initial project setup (step-by-step)
- Daily development workflow
- Adding new feature workflow
- CI/CD commands

**Troubleshooting:**
- Cache clearing
- Environment recreation
- Lock file conflict resolution

**Added to `python-todo-architect` agent:**
- Added `uv-package-management` to YAML frontmatter skills list (first position)
- Added to Available Skills table with location and purpose
- Added to Skill Usage Examples section

## Outcome

- Impact: UV is now the standard package manager for all Todo development
- Tests: Skill includes comprehensive test running patterns (`uv run pytest`)
- Files: 2 files (1 new skill created, 1 agent updated)
- Next prompts: Initialize project with `uv init`, add dependencies, create project structure
- Reflection: Skill approach is correct - tooling supports architecture work, doesn't own a separate domain

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - tooling setup
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run `uv init` and set up actual project structure following the skill patterns
