---
name: tui-reactive-state
description: Implement reactive state management, data binding, and message-based communication for Textual TUI applications. Use this skill when connecting UI components to the service layer, implementing reactive attributes, creating watchers, and designing message-based updates between components.
---

# TUI Reactive State

Reactive state management and data binding patterns for Textual applications.

## Overview

This skill provides patterns for:

- **Reactive Attributes**: Auto-updating UI state
- **Watch Methods**: Responding to state changes
- **Message System**: Component communication
- **Service Integration**: Connecting UI to business logic
- **State Synchronization**: Keeping UI in sync with data

## Reactive Attributes

### Basic Reactive Pattern

```python
from textual.reactive import reactive
from textual.widgets import Static


class TaskCounter(Static):
    """Widget with reactive count."""

    # Reactive attribute - UI updates automatically when changed
    count: reactive[int] = reactive(0)

    def render(self) -> str:
        """Render using reactive value."""
        return f"Tasks: {self.count}"

    # Watch method called when count changes
    def watch_count(self, new_value: int) -> None:
        """React to count changes."""
        if new_value == 0:
            self.add_class("empty")
        else:
            self.remove_class("empty")
```

### Reactive with Validation

```python
class PriorityWidget(Static):
    """Widget with validated reactive priority."""

    priority: reactive[str] = reactive("medium")

    def validate_priority(self, value: str) -> str:
        """Validate priority before setting."""
        valid = {"low", "medium", "high", "critical"}
        if value.lower() not in valid:
            return "medium"  # Default
        return value.lower()

    def watch_priority(self, value: str) -> None:
        """Update styling on priority change."""
        # Remove old priority classes
        for p in ["low", "medium", "high", "critical"]:
            self.remove_class(f"priority-{p}")
        # Add new
        self.add_class(f"priority-{value}")
```

### Reactive Initialization

```python
class TaskStats(Static):
    """Stats widget with initialized reactives."""

    total: reactive[int] = reactive(0)
    completed: reactive[int] = reactive(0)
    pending: reactive[int] = reactive(0, init=False)  # Don't call watch on init

    def compute_pending(self) -> int:
        """Computed reactive value."""
        return self.total - self.completed

    def watch_total(self, value: int) -> None:
        """Update pending when total changes."""
        self.pending = self.compute_pending()

    def watch_completed(self, value: int) -> None:
        """Update pending when completed changes."""
        self.pending = self.compute_pending()
```

## Watch Methods

### Watch Method Patterns

```python
class TaskListView(Static):
    """List view with watch methods."""

    tasks: reactive[list[Task]] = reactive([], init=False)
    filter_query: reactive[str] = reactive("")
    selected_index: reactive[int] = reactive(0)

    def watch_tasks(self, tasks: list[Task]) -> None:
        """React to task list changes."""
        self._rebuild_list()
        # Update parent components
        self.post_message(TaskListChanged(len(tasks)))

    def watch_filter_query(self, query: str) -> None:
        """React to filter changes."""
        self._apply_filter(query)

    def watch_selected_index(self, index: int) -> None:
        """React to selection changes."""
        self._highlight_item(index)
        # Notify parent
        task = self._get_task_at(index)
        if task:
            self.post_message(TaskSelected(task))

    def _rebuild_list(self) -> None:
        """Rebuild list from tasks."""
        self.query("TaskItem").remove()
        for task in self.tasks:
            self.mount(TaskItem(task))

    def _apply_filter(self, query: str) -> None:
        """Apply filter to visible items."""
        query = query.lower()
        for item in self.query(TaskItem):
            matches = query in item.task.title.lower()
            item.display = matches
```

### Watch with Old Value

```python
class SelectionTracker(Static):
    """Track selection changes."""

    selected_id: reactive[str | None] = reactive(None)

    def watch_selected_id(
        self,
        old_value: str | None,
        new_value: str | None,
    ) -> None:
        """Watch with access to old value."""
        # Deselect old
        if old_value:
            self._deselect(old_value)
        # Select new
        if new_value:
            self._select(new_value)

    def _select(self, task_id: str) -> None:
        try:
            item = self.query_one(f"#task-{task_id}")
            item.add_class("selected")
        except Exception:
            pass

    def _deselect(self, task_id: str) -> None:
        try:
            item = self.query_one(f"#task-{task_id}")
            item.remove_class("selected")
        except Exception:
            pass
```

## Message System

### Custom Messages

```python
# src/todo/tui/messages.py
from textual.message import Message
from todo.models.task import Task


class TaskCreated(Message):
    """Emitted when a task is created."""

    def __init__(self, task: Task) -> None:
        self.task = task
        super().__init__()


class TaskUpdated(Message):
    """Emitted when a task is updated."""

    def __init__(self, task: Task) -> None:
        self.task = task
        super().__init__()


class TaskDeleted(Message):
    """Emitted when a task is deleted."""

    def __init__(self, task_id: str, task_title: str) -> None:
        self.task_id = task_id
        self.task_title = task_title
        super().__init__()


class TaskSelected(Message):
    """Emitted when a task is selected."""

    def __init__(self, task: Task) -> None:
        self.task = task
        super().__init__()


class FilterChanged(Message):
    """Emitted when filters change."""

    def __init__(
        self,
        search_query: str = "",
        priority: str | None = None,
        show_completed: bool = True,
    ) -> None:
        self.search_query = search_query
        self.priority = priority
        self.show_completed = show_completed
        super().__init__()


class RefreshRequested(Message):
    """Request UI refresh."""

    pass
```

### Posting Messages

```python
class AddTaskModal(ModalScreen):
    """Modal that posts messages on completion."""

    def action_submit(self) -> None:
        """Submit and notify."""
        title = self.query_one("#title-input", Input).value

        try:
            task = self.task_service.add_task(title)

            # Post message to parent
            self.post_message(TaskCreated(task))

            # Close modal
            self.dismiss(True)

        except ValidationError as e:
            self._show_error(str(e))
```

### Handling Messages

```python
class MainScreen(Screen):
    """Screen that handles task messages."""

    def on_task_created(self, event: TaskCreated) -> None:
        """Handle task creation."""
        # Refresh the list
        self.query_one(TaskListView).refresh_tasks()

        # Update status bar
        self.query_one(StatusBar).refresh_counts()

        # Show notification
        self.app.notify(f"Created: {event.task.title}")

    def on_task_updated(self, event: TaskUpdated) -> None:
        """Handle task update."""
        self.query_one(TaskListView).refresh_tasks()
        self.app.notify(f"Updated: {event.task.title}")

    def on_task_deleted(self, event: TaskDeleted) -> None:
        """Handle task deletion."""
        self.query_one(TaskListView).refresh_tasks()
        self.query_one(StatusBar).refresh_counts()
        self.app.notify(f"Deleted: {event.task_title}", severity="warning")

    def on_filter_changed(self, event: FilterChanged) -> None:
        """Handle filter changes."""
        task_list = self.query_one(TaskListView)
        task_list.apply_filter(
            search=event.search_query,
            priority=event.priority,
            show_completed=event.show_completed,
        )

    def on_refresh_requested(self, event: RefreshRequested) -> None:
        """Handle refresh request."""
        self.query_one(TaskListView).refresh_tasks()
        self.query_one(StatusBar).refresh_counts()
```

### Message Bubbling

```python
# Messages bubble up through the DOM tree
# Parent widgets can handle messages from children

class TaskItem(Static):
    """Item that posts messages."""

    def on_click(self) -> None:
        # Posts to parent (ListView -> Screen -> App)
        self.post_message(TaskSelected(self.task))


class TaskListView(ListView):
    """List handles some messages, bubbles others."""

    def on_task_selected(self, event: TaskSelected) -> None:
        # Handle locally
        self._highlight_task(event.task.id)
        # Let it bubble (don't call event.stop())


class MainScreen(Screen):
    """Screen handles bubbled messages."""

    def on_task_selected(self, event: TaskSelected) -> None:
        # Update sidebar with task details
        self.query_one(Sidebar).show_task(event.task)
```

## Service Integration

### App-Level Service

```python
# src/todo/tui/app.py
from todo.services.task_service import TaskService
from todo.context import AppContext


class TodoApp(App):
    """App with service integration."""

    def __init__(self, task_service: TaskService | None = None) -> None:
        """
        Initialize with optional service injection.

        Args:
            task_service: TaskService for dependency injection (testing)
        """
        super().__init__()

        if task_service:
            self.task_service = task_service
        else:
            # Get from context
            ctx = AppContext.get()
            self.task_service = ctx.task_service

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        # Pass service to main screen
        self.push_screen(MainScreen(self.task_service))
```

### Screen-Level Integration

```python
class MainScreen(Screen):
    """Screen with service access."""

    def __init__(self, task_service: TaskService) -> None:
        super().__init__()
        self.task_service = task_service

    def compose(self) -> ComposeResult:
        # Pass service to components
        yield Sidebar(id="sidebar")
        yield TaskListView(self.task_service, id="task-list")
        yield StatusBar(self.task_service, id="status-bar")
```

### Component Service Pattern

```python
class TaskListView(ListView):
    """Component with service reference."""

    def __init__(self, task_service: TaskService, **kwargs) -> None:
        super().__init__(**kwargs)
        self.task_service = task_service

    def refresh_tasks(self) -> None:
        """Refresh from service."""
        self.clear()
        tasks = self.task_service.get_all_tasks()

        for task in tasks:
            self.append(ListItem(TaskItem(task)))

    def delete_task(self, task_id: str) -> None:
        """Delete via service."""
        task = self.task_service.get_task(task_id)
        self.task_service.delete_task(task_id)
        self.refresh_tasks()
        self.post_message(TaskDeleted(task_id, task.title))
```

## State Synchronization

### Syncing UI with Service State

```python
class TaskListView(ListView):
    """List that stays in sync with service."""

    # Reactive representation of service state
    tasks: reactive[list[Task]] = reactive([])

    def on_mount(self) -> None:
        """Initial sync on mount."""
        self.sync_with_service()

    def sync_with_service(self) -> None:
        """Sync reactive tasks with service."""
        self.tasks = self.task_service.get_all_tasks()

    def watch_tasks(self, tasks: list[Task]) -> None:
        """Rebuild UI when tasks change."""
        self.clear()
        if not tasks:
            self.append(ListItem(Static("[dim]No tasks[/dim]")))
            return

        for task in tasks:
            self.append(ListItem(TaskItem(task)))

    # Service operations trigger sync
    def add_task(self, title: str) -> None:
        task = self.task_service.add_task(title)
        self.sync_with_service()  # Resync
        return task

    def delete_task(self, task_id: str) -> None:
        self.task_service.delete_task(task_id)
        self.sync_with_service()
```

### Debounced Sync

```python
from textual.timer import Timer


class SearchableList(Static):
    """List with debounced search."""

    search_query: reactive[str] = reactive("")
    _search_timer: Timer | None = None

    def watch_search_query(self, query: str) -> None:
        """Debounce search."""
        # Cancel pending search
        if self._search_timer:
            self._search_timer.stop()

        # Start new timer
        self._search_timer = self.set_timer(
            0.3,  # 300ms debounce
            lambda: self._do_search(query),
        )

    def _do_search(self, query: str) -> None:
        """Perform actual search."""
        results = self.task_service.search(query)
        self.tasks = results
```

## Testing Patterns

### Testing Reactive State

```python
# tests/tui/test_reactive.py
import pytest
from textual.testing import AppTester
from todo.tui.app import TodoApp


class TestReactiveUpdates:
    """Tests for reactive state updates."""

    async def test_task_count_updates(self, app_tester, task_service):
        """Task count updates when tasks added."""
        counter = app_tester.app.query_one(TaskCounter)

        # Initial count
        assert counter.count == 0

        # Add task
        task_service.add_task("Test")
        app_tester.app.query_one(TaskListView).refresh_tasks()

        # Count should update
        assert counter.count == 1

    async def test_filter_updates_list(self, app_tester, task_service):
        """Filter changes update list."""
        task_service.add_task("Work task")
        task_service.add_task("Personal task")

        # Apply filter
        sidebar = app_tester.app.query_one(Sidebar)
        sidebar.query_one("#search-input", Input).value = "work"

        # Should trigger FilterChanged message
        await app_tester.pause()

        # List should be filtered
        visible = [
            item
            for item in app_tester.app.query(TaskItem)
            if item.display
        ]
        assert len(visible) == 1


class TestMessageHandling:
    """Tests for message handling."""

    async def test_task_created_refreshes_list(self, app_tester, task_service):
        """TaskCreated message refreshes list."""
        await app_tester.press("a")
        await app_tester.type("New task")
        await app_tester.press("ctrl+s")

        # List should have new task
        items = app_tester.app.query(TaskItem)
        assert len(items) == 1

    async def test_task_deleted_updates_status(self, app_tester, sample_task):
        """TaskDeleted message updates status bar."""
        status = app_tester.app.query_one(StatusBar)
        initial_total = status.total

        # Delete task
        await app_tester.press("d")
        await app_tester.press("enter")  # Confirm

        assert status.total == initial_total - 1


class TestServiceIntegration:
    """Tests for service integration."""

    async def test_mock_service_injection(self, mock_service):
        """Mock service can be injected."""
        from todo.models.task import Task

        mock_service.get_all_tasks.return_value = [
            Task(title="Mock Task 1"),
            Task(title="Mock Task 2"),
        ]

        app = TodoApp(task_service=mock_service)
        async with AppTester.run_test(app) as tester:
            items = tester.app.query(TaskItem)
            assert len(items) == 2

    async def test_service_called_on_add(self, app_tester, mock_service):
        """Service is called when adding task."""
        await app_tester.press("a")
        await app_tester.type("Test task")
        await app_tester.press("ctrl+s")

        mock_service.add_task.assert_called_once()
```

## Running Tests

```bash
# Run reactive tests
uv run pytest tests/tui/test_reactive.py -v

# Run message tests
uv run pytest tests/tui/test_reactive.py -k "message" -v

# Run integration tests
uv run pytest tests/tui/test_reactive.py -k "integration" -v
```

## Checklist

Before completing reactive state implementation:
- [ ] Reactive attributes update UI automatically
- [ ] Watch methods handle state changes
- [ ] Messages flow correctly between components
- [ ] Service integration uses dependency injection
- [ ] State syncs with service layer
- [ ] Filters update reactively
- [ ] Tests cover state changes
- [ ] Tests verify message handling
