---
name: readme-writer
description: Generate comprehensive, well-structured README.md files for software projects. Use this skill when the user asks to create, update, or improve a README file, or when completing a project that needs documentation. Automatically analyzes project structure, tech stack, dependencies, features, and generates professional documentation with proper sections (Overview, Features, Installation, Usage, Development, Contributing, License).
---

# README Writer

## Overview

This skill helps create professional, comprehensive README.md files by analyzing project structure, configuration files, and source code to automatically generate well-organized documentation.

## Workflow

### 1. Analyze Project Context

Gather information from these sources:

**Configuration Files:**
- `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` - Dependencies and metadata
- `.gitignore` / `.dockerignore` - Deployment context
- `Dockerfile` / `docker-compose.yml` - Container setup
- CI/CD configs (`.github/workflows/`, `.gitlab-ci.yml`) - Build/deploy info

**Source Structure:**
- Main entry points (`main.py`, `index.js`, `app.py`, `src/main.rs`)
- Directory organization (`src/`, `lib/`, `tests/`, `docs/`)
- Key modules and their purposes

**Existing Documentation:**
- `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md`
- Inline code comments and docstrings
- Existing `README.md` (if updating)

### 2. Determine README Structure

Use this standard structure (adapt based on project type):

```markdown
# Project Title

Brief tagline (1 sentence)

---

[Optional: Badges - build status, coverage, version, license]
[Optional: Screenshot or demo GIF]

---

## Features

- Bullet list of key capabilities
- Focus on user value, not implementation

## Tech Stack / Built With

- Language/Framework
- Key dependencies
- Development tools

## Getting Started

### Prerequisites

- Required software/versions
- System requirements

### Installation

Step-by-step setup instructions

### Usage

Basic usage examples with code blocks

## Development

### Running Tests

### Linting/Formatting

### Building/Deployment

## Project Structure

```text
project/
├── src/
└── tests/
```

## Contributing

[Link to CONTRIBUTING.md or inline guidelines]

## License

[License info or link to LICENSE file]

## Acknowledgments / Credits

[Optional]
```

### 3. Generate Content

**Title & Tagline:**
- Extract from `package.json` name/description or `pyproject.toml`
- Make it concise and descriptive

**Features:**
- Identify from main source files, CLI commands, API routes
- Focus on user-facing capabilities
- Use action verbs (e.g., "Manage tasks with priorities")

**Installation:**
- Detect package manager (npm, uv, pip, cargo, go)
- Provide one-command setup if possible
- Include environment setup (`.env` templates)

**Usage:**
- Show the most common use case first
- Include CLI commands, API examples, or code snippets
- Use actual commands that work in the project

**Development:**
- Extract from scripts in `package.json`, `Makefile`, or docs
- Include test commands, linting, formatting

**Project Structure:**
- Generate tree from actual directory structure
- Add comments explaining each major directory

### 4. Quality Checks

Before finalizing:
- [ ] All commands are copy-pasteable and actually work
- [ ] Code blocks have proper language syntax highlighting
- [ ] Links are valid (relative paths for internal docs)
- [ ] Badges (if included) are functional
- [ ] No placeholder text remains (TODO, FIXME, etc.)
- [ ] Formatting is consistent (heading levels, bullet styles)
- [ ] Length is appropriate (not too verbose, not too sparse)

### 5. Special Cases

**For CLI Apps:**
- Include help output (`--help` flag)
- Show example commands for common tasks
- Explain configuration options

**For Libraries:**
- API documentation or link to API docs
- Quick start code example
- Link to full documentation site

**For Web Apps:**
- Environment variables table
- API endpoint documentation
- Deployment instructions

**For Existing READMEs:**
- Read current README first
- Preserve custom sections user added
- Update outdated information
- Maintain existing tone/style

## References

For detailed README sections and templates, see:
- [references/readme-templates.md](references/readme-templates.md) - Complete templates for different project types
