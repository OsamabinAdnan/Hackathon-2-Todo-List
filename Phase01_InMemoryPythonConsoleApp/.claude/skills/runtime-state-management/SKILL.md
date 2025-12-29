---
name: runtime-state-management
description: Handle in-memory state lifecycle across program execution for the Todo app. Use this skill when implementing application state, singleton patterns, dependency injection, state initialization/cleanup, or managing shared state. For TUI-specific reactive patterns, see the tui-reactive-state skill.
---

# Runtime State Management

Handle in-memory state lifecycle across program execution for Phase 1 of the Todo app.

## Overview

This skill provides patterns for managing application state in an in-memory context:

- **State Initialization**: Bootstrap application state on startup
- **Singleton Pattern**: Single instance of TaskService across commands
- **Dependency Injection**: Testable state management
- **State Lifecycle**: Initialize, access, modify, cleanup
- **Thread Safety**: Safe concurrent access patterns

> **Note**: For TUI-specific reactive state patterns (reactive attributes, watchers, messages), see the `tui-reactive-state` skill under the `tui-designer` agent.

## State Management Patterns

### 1. Global Singleton (Simple)

Best for applications with single entry point.

```python
# src/todo/state.py
"""Global application state singleton."""

from todo.services.task_service import TaskService

# Module-level singleton
_service: TaskService | None = None


def get_service() -> TaskService:
    """
    Get the global TaskService instance.

    Creates instance on first access (lazy initialization).

    Returns:
        TaskService singleton instance
    """
    global _service
    if _service is None:
        _service = TaskService()
    return _service


def reset_service() -> None:
    """
    Reset the global service (useful for testing).

    Warning: Clears all in-memory data.
    """
    global _service
    _service = None
```

**Usage:**

```python
from todo.state import get_service

# Get singleton service
service = get_service()
task = service.add_task("My task")
print(f"Created: {task.id}")
```

### 2. Application Context (Recommended)

Better for complex applications with multiple services.

```python
# src/todo/context.py
"""Application context with dependency injection."""

from dataclasses import dataclass, field
from typing import Self

from todo.services.task_service import TaskService


@dataclass
class AppContext:
    """
    Application context holding all services and state.

    Provides centralized access to application components
    with support for dependency injection in tests.
    """

    task_service: TaskService = field(default_factory=TaskService)
    debug: bool = False
    version: str = "0.1.0"

    _instance: "AppContext | None" = field(default=None, repr=False, init=False)

    @classmethod
    def get(cls) -> "AppContext":
        """Get or create the singleton context."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set(cls, context: "AppContext") -> None:
        """Set the context (for testing/DI)."""
        cls._instance = context

    @classmethod
    def reset(cls) -> None:
        """Reset context to None."""
        cls._instance = None

    def __enter__(self) -> Self:
        """Context manager entry."""
        AppContext.set(self)
        return self

    def __exit__(self, *args) -> None:
        """Context manager exit."""
        AppContext.reset()
```

**Usage:**

```python
# Normal usage
ctx = AppContext.get()
task = ctx.task_service.add_task("My task")

# Testing with custom context
with AppContext(task_service=mock_service, debug=True):
    # Tests run with mock service
    pass

# After with-block, context is reset
```

### 3. State Container Class

For explicit state management with lifecycle hooks.

```python
# src/todo/state.py
"""State container with lifecycle management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from todo.services.task_service import TaskService


@dataclass
class AppState:
    """
    Application state container with lifecycle hooks.

    Manages initialization, access, and cleanup of
    application-wide state.
    """

    task_service: TaskService = field(default_factory=TaskService)
    started_at: datetime = field(default_factory=datetime.now)
    _initialized: bool = field(default=False, repr=False)
    _on_init_callbacks: list[Callable[[], None]] = field(
        default_factory=list, repr=False
    )
    _on_cleanup_callbacks: list[Callable[[], None]] = field(
        default_factory=list, repr=False
    )

    def initialize(self) -> None:
        """
        Initialize application state.

        Call once at application startup.
        Runs all registered on_init callbacks.
        """
        if self._initialized:
            return

        self.started_at = datetime.now()

        for callback in self._on_init_callbacks:
            callback()

        self._initialized = True

    def cleanup(self) -> None:
        """
        Cleanup application state.

        Call before application exit.
        Runs all registered on_cleanup callbacks.
        """
        for callback in self._on_cleanup_callbacks:
            callback()

        self._initialized = False

    def on_init(self, callback: Callable[[], None]) -> None:
        """Register initialization callback."""
        self._on_init_callbacks.append(callback)

    def on_cleanup(self, callback: Callable[[], None]) -> None:
        """Register cleanup callback."""
        self._on_cleanup_callbacks.append(callback)

    @property
    def is_initialized(self) -> bool:
        """Check if state is initialized."""
        return self._initialized

    def get_uptime_seconds(self) -> float:
        """Get seconds since state was initialized."""
        return (datetime.now() - self.started_at).total_seconds()


# Global state instance
_state: AppState | None = None


def get_state() -> AppState:
    """Get or create global state."""
    global _state
    if _state is None:
        _state = AppState()
        _state.initialize()
    return _state


def reset_state() -> None:
    """Reset global state."""
    global _state
    if _state is not None:
        _state.cleanup()
    _state = None
```

**Usage with lifecycle:**

```python
# Application entry point
def main() -> None:
    state = get_state()

    try:
        # Run application
        app()
    finally:
        # Ensure cleanup
        reset_state()
```

## State Lifecycle

### Initialization Flow

```
Application Start
       |
       v
  get_state()
       |
       v
  State exists? --No--> Create AppState
       |                      |
      Yes                     v
       |              Initialize services
       |                      |
       |              Run on_init callbacks
       |                      |
       +<---------------------+
       |
       v
  Return state
       |
       v
  Run CLI commands
```

### Cleanup Flow

```
Application Exit / Signal
       |
       v
  reset_state()
       |
       v
  Run on_cleanup callbacks
       |
       v
  Clear state reference
       |
       v
  (State garbage collected)
```

## Testing Patterns

### Fixture for Fresh State

```python
# tests/conftest.py
import pytest
from todo.state import AppState, reset_state
from todo.context import AppContext


@pytest.fixture(autouse=True)
def fresh_state():
    """Ensure fresh state for each test."""
    reset_state()
    AppContext.reset()
    yield
    reset_state()
    AppContext.reset()


@pytest.fixture
def app_state() -> AppState:
    """Provide initialized AppState."""
    state = AppState()
    state.initialize()
    yield state
    state.cleanup()


@pytest.fixture
def mock_service(mocker):
    """Provide mock TaskService."""
    return mocker.Mock(spec=TaskService)


@pytest.fixture
def app_context_with_mock(mock_service):
    """AppContext with mock service."""
    with AppContext(task_service=mock_service) as ctx:
        yield ctx
```

### Testing with State Injection

```python
# tests/unit/test_state.py
import pytest
from todo.state import get_service, reset_service
from todo.context import AppContext


def test_singleton_returns_same_instance():
    """Verify singleton pattern works."""
    service1 = get_service()
    service2 = get_service()
    assert service1 is service2


def test_reset_clears_singleton():
    """Verify reset creates new instance."""
    service1 = get_service()
    service1.add_task("Test")

    reset_service()

    service2 = get_service()
    assert service1 is not service2
    assert len(service2.get_all_tasks()) == 0


def test_context_manager_injection(mock_service):
    """Verify context manager allows DI."""
    with AppContext(task_service=mock_service) as ctx:
        ctx.task_service.add_task("Test")

    mock_service.add_task.assert_called_once_with("Test")
```

> **Note**: For TUI-specific testing patterns with AppTester, see the `tui-reactive-state` skill.

## State Boundaries

### What Lives in State

| Include | Exclude |
|---------|---------|
| TaskService instance | Individual Task objects |
| Configuration values | Request-specific data |
| Initialized flags | Temporary calculations |
| Service references | User input |

### State Scope

```
+------------------------------------------+
|              Application State            |
|  +------------------------------------+  |
|  |          TaskService               |  |
|  |  +------------------------------+  |  |
|  |  |    _tasks: dict[str, Task]   |  |  |
|  |  |    (Task instances live here)|  |  |
|  |  +------------------------------+  |  |
|  +------------------------------------+  |
|  | debug: bool                        |  |
|  | started_at: datetime               |  |
+------------------------------------------+
```

## Constitution Compliance

- [x] Single source of truth for state (Principle II)
- [x] Type hints on all state access functions
- [x] Testable via dependency injection (Principle IV)
- [x] No global mutable state without accessor functions
- [x] Clear lifecycle (init/cleanup) for resource management
