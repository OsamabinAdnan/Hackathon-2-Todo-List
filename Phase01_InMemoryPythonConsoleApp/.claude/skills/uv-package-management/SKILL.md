---
name: uv-package-management
description: Manage Python projects using UV package manager. Use this skill for project initialization, dependency management, virtual environments, running commands, and pyproject.toml configuration. UV is the primary package manager for all Todo application development across all levels.
---

# UV Package Management

UV-based Python project management for the Todo application.

## Overview

This skill provides patterns for:

- **Project Setup**: Initialize projects with UV
- **Dependency Management**: Add, remove, sync dependencies
- **Virtual Environments**: Create and manage venvs
- **Running Commands**: Execute Python, pytest, and scripts
- **pyproject.toml**: Configuration patterns

## Why UV?

UV is a fast, modern Python package manager that replaces pip, pip-tools, and virtualenv:

- **Speed**: 10-100x faster than pip
- **Reliable**: Deterministic builds with lock files
- **Simple**: Single tool for all package operations
- **Compatible**: Works with existing pyproject.toml

## Project Initialization

### New Project Setup

```bash
# Initialize new project in current directory
uv init

# Initialize with specific name
uv init todo-app

# Initialize with Python version
uv init --python 3.12
```

### Generated Structure

```
todo-app/
├── pyproject.toml      # Project configuration
├── uv.lock             # Lock file (auto-generated)
├── .python-version     # Python version pin
├── README.md           # Project readme
└── src/
    └── todo/
        └── __init__.py
```

### pyproject.toml Template

```toml
[project]
name = "todo-app"
version = "0.1.0"
description = "In-memory Todo application with Textual TUI"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
todo = "todo.tui:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/todo"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
pythonpath = ["src"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

## Virtual Environment

### Creating Environment

```bash
# Create venv (auto-created on first uv command)
uv venv

# Create with specific Python version
uv venv --python 3.12

# Create in custom location
uv venv .venv
```

### Environment Location

UV creates `.venv/` in project root by default.

```bash
# Activate (optional - uv run doesn't need activation)
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### Using Without Activation

```bash
# UV automatically uses project's venv
uv run python script.py
uv run pytest
uv run todo
```

## Dependency Management

### Adding Dependencies

```bash
# Add production dependency
uv add textual

# Add multiple dependencies
uv add textual rich

# Add with version constraint
uv add "textual>=0.40.0"
uv add "rich>=13.0,<14.0"

# Add development dependency
uv add --dev pytest
uv add --dev pytest-asyncio pytest-cov ruff

# Add optional dependency group
uv add --optional test pytest pytest-asyncio
```

### Todo App Dependencies

```bash
# Core dependencies
uv add textual rich

# Development dependencies
uv add --dev pytest pytest-asyncio pytest-cov
uv add --dev ruff mypy
uv add --dev pytest-mock
```

### Removing Dependencies

```bash
# Remove dependency
uv remove requests

# Remove dev dependency
uv remove --dev pytest-xdist
```

### Syncing Dependencies

```bash
# Install all dependencies from lock file
uv sync

# Sync including dev dependencies (default)
uv sync

# Sync only production dependencies
uv sync --no-dev

# Sync specific optional group
uv sync --extra test
```

### Viewing Dependencies

```bash
# List installed packages
uv pip list

# Show dependency tree
uv pip tree

# Check for outdated packages
uv pip list --outdated
```

### Updating Dependencies

```bash
# Update all dependencies
uv lock --upgrade

# Update specific package
uv lock --upgrade-package textual

# Then sync to install updates
uv sync
```

## Lock File (uv.lock)

### Purpose

- Ensures reproducible builds
- Pins exact versions of all dependencies
- Should be committed to git

### Regenerating Lock File

```bash
# Regenerate from pyproject.toml
uv lock

# Force regenerate
uv lock --refresh
```

### Lock File in Git

```gitignore
# .gitignore - DO NOT ignore uv.lock
# uv.lock should be committed

# Do ignore the venv
.venv/
```

## Running Commands

### Python Execution

```bash
# Run Python script
uv run python src/todo/main.py

# Run module
uv run python -m todo.tui

# Run with arguments
uv run python script.py --verbose
```

### Running the Application

```bash
# Run via entry point (defined in pyproject.toml)
uv run todo

# Run TUI directly
uv run python -m todo.tui
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_task.py

# Run specific test class
uv run pytest tests/unit/test_task.py::TestTaskModel

# Run specific test
uv run pytest tests/unit/test_task.py::TestTaskModel::test_create_task

# Run with coverage
uv run pytest --cov=src/todo --cov-report=html

# Run TUI tests
uv run pytest tests/tui/ -v

# Run with markers
uv run pytest -m "not slow"

# Run async tests
uv run pytest tests/tui/ -v --asyncio-mode=auto
```

### Code Quality

```bash
# Run linter
uv run ruff check src/

# Run linter with auto-fix
uv run ruff check src/ --fix

# Format code
uv run ruff format src/

# Type checking
uv run mypy src/todo/
```

## pyproject.toml Patterns

### Full Configuration for Todo App

```toml
[project]
name = "todo-app"
version = "0.1.0"
description = "In-memory Todo application with Textual TUI"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"
authors = [
    { name = "Your Name", email = "you@example.com" }
]
keywords = ["todo", "tui", "textual", "cli"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "textual>=0.40.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.scripts]
todo = "todo.tui:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/todo"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
pythonpath = ["src"]
markers = [
    "slow: marks tests as slow",
    "tui: marks TUI tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["src/todo"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]

[tool.ruff]
line-length = 88
target-version = "py311"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # pyflakes
    "I",      # isort
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "SIM",    # flake8-simplify
]
ignore = [
    "E501",   # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["todo"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_ignores = true
```

### Dependency Groups Pattern

```toml
[project.optional-dependencies]
# Testing dependencies
test = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
]

# Development tools
dev = [
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

# Documentation
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
]

# All development dependencies
all = [
    "todo-app[test,dev,docs]",
]
```

```bash
# Install specific group
uv sync --extra test

# Install multiple groups
uv sync --extra test --extra dev

# Install all
uv sync --extra all
```

## Common Workflows

### Initial Project Setup

```bash
# 1. Initialize project
uv init todo-app
cd todo-app

# 2. Add dependencies
uv add textual rich
uv add --dev pytest pytest-asyncio pytest-cov ruff mypy pytest-mock

# 3. Create source structure
mkdir -p src/todo/{models,services,storage,tui,utils}
mkdir -p src/todo/tui/{screens,components,modals,styles}
mkdir -p tests/{unit,integration,tui}

# 4. Create __init__.py files
touch src/todo/__init__.py
touch src/todo/models/__init__.py
# ... etc

# 5. Verify setup
uv run python -c "import todo; print('Setup complete!')"
```

### Daily Development

```bash
# Start of day - sync dependencies
uv sync

# Run tests before changes
uv run pytest

# Make changes...

# Run tests after changes
uv run pytest -v

# Check code quality
uv run ruff check src/ --fix
uv run ruff format src/

# Run the app
uv run todo
```

### Adding New Feature

```bash
# 1. Ensure dependencies synced
uv sync

# 2. Run existing tests
uv run pytest

# 3. Implement feature...

# 4. Run tests for new feature
uv run pytest tests/unit/test_new_feature.py -v

# 5. Run all tests
uv run pytest

# 6. Check code quality
uv run ruff check src/
```

### CI/CD Commands

```bash
# Install dependencies (CI)
uv sync --frozen

# Run tests with coverage
uv run pytest --cov=src/todo --cov-report=xml

# Lint check (no fix in CI)
uv run ruff check src/

# Type check
uv run mypy src/todo/
```

## Troubleshooting

### Common Issues

```bash
# Clear UV cache
uv cache clean

# Force reinstall all packages
uv sync --reinstall

# Rebuild lock file
uv lock --refresh

# Check Python version
uv run python --version

# Verify package installed
uv pip show textual
```

### Environment Issues

```bash
# Remove and recreate venv
rm -rf .venv
uv venv
uv sync

# Use specific Python
uv venv --python 3.12
uv sync
```

### Lock File Conflicts

```bash
# After merge conflicts in uv.lock
uv lock --refresh
uv sync
```

## Checklist

Before considering project setup complete:
- [ ] `uv init` run successfully
- [ ] pyproject.toml configured properly
- [ ] All dependencies added (core + dev)
- [ ] uv.lock committed to git
- [ ] `uv run pytest` works
- [ ] `uv run todo` launches app
- [ ] Ruff and mypy configured
- [ ] CI commands documented
