---
id: "006"
title: "CLI Architecture Transition"
stage: "spec"
date: "2025-12-30"
model: "opus"
feature: "basic-crud"
branch: "main"
user: "claude"
command: "sp.specify"
labels: ["architecture", "cli", "transition", "specification"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "specs/basic-crud/spec.md"
  - "specs/basic-crud/plan.md"
  - "specs/basic-crud/tasks.md"
  - ".specify/memory/constitution.md"
tests: []
---

# CLI Architecture Transition

## Overview
This PHR documents the comprehensive transition of the Todo application architecture from a Textual TUI approach to a Typer CLI approach. The changes affect all core specification documents (constitution, spec, plan, tasks) to ensure consistency across the entire project.

## Changes Made

### Constitution Updates
- Updated Principle V from "Textual TUI Experience" to "Rich CLI Experience"
- Changed technology stack from Textual to Typer and Rich frameworks
- Updated project structure to use main.py instead of tui/ directory
- Modified CLI Architecture Guidelines to replace TUI Architecture Guidelines
- Updated performance requirements from TUI-specific to CLI-specific metrics
- Updated agent responsibilities to use cli-designer instead of tui-designer
- Created new CLI-specific skills and removed TUI-specific skills

### Spec Document Updates
- Changed application overview from "Textual TUI" to "Typer CLI with Rich-formatted console output"
- Updated user stories to reflect CLI commands instead of TUI interactions
- Modified acceptance scenarios to use CLI-specific language (commands, console output)
- Updated functional requirements to specify CLI operations
- Adjusted edge cases for CLI performance requirements
- Updated clarifications to reflect CLI approach

### Plan Document Updates
- Updated technical context to specify CLI architecture with Typer and Rich
- Changed architecture sketch to define CLI layer instead of TUI layer
- Updated constitution compliance to reflect Rich CLI Experience
- Modified decisions to document CLI-specific choices
- Aligned testing strategy with CLI commands and output validation
- Updated research tasks for CLI patterns

### Tasks Document Updates
- Updated path conventions to use src/todo/cli/ instead of src/todo/tui/
- Modified foundational tasks to implement CLI components
- Updated user stories to implement CLI commands (add, list, update, delete, toggle)
- Changed test paths from tests/tui/ to tests/cli/
- Added tasks for interactive menu system
- Aligned all implementation tasks with CLI approach

## Motivation
The transition was necessary to align with the project's decision to implement a command-line interface instead of a terminal user interface. This change provides:
- Simpler architecture with reduced complexity
- Better performance characteristics for console-based operations
- More familiar interaction patterns for command-line users
- Easier maintenance and extension possibilities

## Impact
- All specification documents are now consistently aligned with CLI architecture
- Development team can proceed with CLI implementation without confusion
- Future development will follow CLI patterns and conventions
- Test strategies are aligned with CLI command structure

## Validation
- All documents cross-reference each other consistently
- Architecture decisions are properly documented
- Task breakdown aligns with implementation requirements
- No TUI references remain in any documents
- Performance requirements are appropriate for CLI

## Files Affected
- `.specify/memory/constitution.md` - Updated core principles and technology stack
- `specs/basic-crud/spec.md` - Updated user stories and requirements
- `specs/basic-crud/plan.md` - Updated technical approach and architecture
- `specs/basic-crud/tasks.md` - Updated implementation tasks and file paths

## Outcome
Successfully transitioned the entire specification stack from TUI to CLI architecture while maintaining consistency and completeness across all documents. The project is now ready for CLI implementation following the updated specifications.

## Evaluation
The transition has been completed successfully with all documents properly aligned. The CLI architecture is now clearly defined across all specification levels, providing a solid foundation for implementation. The changes maintain all core functionality (Add, Delete, Update, View, Mark Complete) while adapting the interface to command-line interactions.