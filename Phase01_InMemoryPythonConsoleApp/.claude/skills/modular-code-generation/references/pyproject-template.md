# pyproject.toml Template

Standard UV project configuration for the Todo app.

## Complete Template

```toml
[project]
name = "todo"
version = "0.1.0"
description = "A simple in-memory todo list application"
readme = "README.md"
requires-python = ">=3.13"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
keywords = ["todo", "cli", "task-management"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.13",
    "Topic :: Utilities",
]

dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "python-dateutil>=2.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "freezegun>=1.2.0",
    "ruff>=0.1.0",
    "pyright>=1.1.0",
]

[project.scripts]
todo = "todo.cli.app:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/todo"]

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # Pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["todo"]

[tool.pyright]
pythonVersion = "3.13"
typeCheckingMode = "strict"
include = ["src"]
exclude = ["tests"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["src/todo"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
fail_under = 100
```

## Section Explanations

### [project]

Core package metadata:

- `name`: Package name (importable as `import todo`)
- `version`: Semantic version
- `requires-python`: Minimum Python version (3.13+)
- `dependencies`: Runtime dependencies

### [project.optional-dependencies]

Development dependencies installed via:

```bash
uv add --dev pytest pytest-cov ruff pyright
```

### [project.scripts]

CLI entry point:

```bash
# After installation, run:
todo add "My task"
todo list
```

### [tool.ruff]

Linting and formatting:

```bash
# Lint
uv run ruff check src/

# Format
uv run ruff format src/
```

### [tool.pyright]

Type checking:

```bash
uv run pyright src/
```

### [tool.pytest]

Test configuration:

```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=todo --cov-report=term-missing
```

## Project Initialization Commands

```bash
# Initialize project
uv init todo-app
cd todo-app

# Create source structure
mkdir -p src/todo/{models,services,storage,cli,utils}
mkdir -p tests/{unit,integration}

# Add dependencies
uv add typer rich python-dateutil
uv add --dev pytest pytest-cov freezegun ruff pyright

# Create virtual environment
uv venv

# Sync dependencies
uv sync

# Verify setup
uv run python -c "import todo; print(todo.__version__)"
```

## README.md Template

```markdown
# Todo App

A simple in-memory todo list application.

## Quick Start

```bash
# Install
uv sync

# Run
uv run todo add "My first task"
uv run todo list
uv run todo done <task-id>
```

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Lint
uv run ruff check src/

# Type check
uv run pyright src/
```
```
