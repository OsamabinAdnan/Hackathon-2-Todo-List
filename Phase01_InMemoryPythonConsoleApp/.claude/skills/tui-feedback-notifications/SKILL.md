---
name: tui-feedback-notifications
description: Implement user feedback, notifications, toasts, confirmations, and status updates for Textual TUI applications. Use this skill when adding toast messages, confirmation dialogs, inline error display, loading states, and status bar updates.
---

# TUI Feedback & Notifications

User feedback, notifications, and confirmation patterns for Textual applications.

## Overview

This skill provides patterns for:

- **Toast Notifications**: Transient success/error messages
- **Confirmation Dialogs**: Destructive action confirmations
- **Inline Errors**: Form field error display
- **Status Updates**: Status bar information
- **Loading States**: Progress and loading indicators

## Toast Notifications

### Using App.notify()

```python
# Built-in toast notification
self.app.notify("Task created successfully!")

# With severity
self.app.notify("Task deleted", severity="warning")
self.app.notify("Error: Invalid input", severity="error")
self.app.notify("Operation completed", severity="information")

# With title
self.app.notify(
    "Task has been permanently deleted.",
    title="Deleted",
    severity="warning",
)

# With timeout (milliseconds)
self.app.notify(
    "Changes saved",
    timeout=3,  # 3 seconds
)
```

### Notification Severities

| Severity | Color | Use Case |
|----------|-------|----------|
| `"information"` | Blue | General info, success |
| `"warning"` | Yellow | Caution, non-critical |
| `"error"` | Red | Errors, failures |

### Notification After Actions

```python
# After successful create
def _on_task_created(self, task: Task) -> None:
    """Handle task creation."""
    self.app.notify(
        f"Task '{task.title}' created",
        severity="information",
    )
    self._refresh_list()

# After delete with undo hint
def _on_task_deleted(self, task_title: str) -> None:
    """Handle task deletion."""
    self.app.notify(
        f"'{task_title}' deleted",
        severity="warning",
    )

# On error
def _on_error(self, error: Exception) -> None:
    """Handle errors."""
    self.app.notify(
        str(error),
        title="Error",
        severity="error",
    )
```

## Confirmation Dialogs

### Basic Confirm Pattern

```python
# src/todo/tui/modals/confirm.py
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Button, Label, Static
from textual.containers import Vertical, Horizontal


class ConfirmModal(ModalScreen[bool]):
    """
    Confirmation dialog for destructive actions.

    Usage:
        def delete_task(self) -> None:
            self.app.push_screen(
                ConfirmModal("Delete this task?"),
                callback=self._on_confirm_delete,
            )

        def _on_confirm_delete(self, confirmed: bool) -> None:
            if confirmed:
                self.do_delete()
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", priority=True),
        Binding("enter", "confirm", "Confirm"),
        Binding("y", "confirm", "Yes", show=False),
        Binding("n", "cancel", "No", show=False),
    ]

    DEFAULT_CSS = """
    ConfirmModal {
        align: center middle;
    }

    #confirm-dialog {
        background: $surface;
        border: solid $error;
        padding: 1 2;
        width: 50;
        height: auto;
    }

    #confirm-title {
        text-align: center;
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }

    #confirm-message {
        text-align: center;
        margin-bottom: 1;
    }

    .confirm-buttons {
        margin-top: 1;
        align: center middle;
    }

    .confirm-buttons Button {
        margin: 0 1;
    }
    """

    def __init__(
        self,
        message: str,
        title: str = "Confirm",
        confirm_label: str = "Delete",
        cancel_label: str = "Cancel",
    ) -> None:
        super().__init__()
        self.message = message
        self.title_text = title
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label(self.title_text, id="confirm-title")
            yield Static(self.message, id="confirm-message")

            with Horizontal(classes="confirm-buttons"):
                yield Button(self.cancel_label, id="cancel-btn")
                yield Button(self.confirm_label, variant="error", id="confirm-btn")

    def on_mount(self) -> None:
        """Focus cancel by default (safer)."""
        self.query_one("#cancel-btn").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(False)
        elif event.button.id == "confirm-btn":
            self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)
```

### Using Confirmation

```python
class TaskListView(ListView):
    """Task list with confirmation support."""

    def delete_selected(self) -> None:
        """Delete with confirmation."""
        task = self.get_selected_task()
        if not task:
            return

        self.app.push_screen(
            ConfirmModal(
                f"Delete '{task.title}'?",
                title="Delete Task",
            ),
            callback=lambda confirmed: self._do_delete(task.id) if confirmed else None,
        )

    def _do_delete(self, task_id: str) -> None:
        """Perform deletion after confirmation."""
        try:
            task = self.task_service.get_task(task_id)
            title = task.title
            self.task_service.delete_task(task_id)
            self.refresh_tasks()
            self.app.notify(f"'{title}' deleted", severity="warning")
        except Exception as e:
            self.app.notify(str(e), severity="error")
```

### Confirm Variants

```python
# Delete confirmation
ConfirmModal(
    f"Delete '{task.title}'?\n\nThis cannot be undone.",
    title="Delete Task",
    confirm_label="Delete",
)

# Clear all confirmation
ConfirmModal(
    "Clear all completed tasks?\n\nThis will delete all completed tasks.",
    title="Clear Completed",
    confirm_label="Clear All",
)

# Exit without saving
ConfirmModal(
    "You have unsaved changes.\n\nDiscard and exit?",
    title="Unsaved Changes",
    confirm_label="Discard",
    cancel_label="Go Back",
)
```

## Inline Error Display

### Error Widget Pattern

```python
# Inline error display in forms
class ErrorDisplay(Static):
    """Inline error message display."""

    DEFAULT_CSS = """
    ErrorDisplay {
        color: $error;
        margin-left: 1;
        text-style: italic;
        height: auto;
    }

    ErrorDisplay.hidden {
        display: none;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self.add_class("hidden")

    def show_error(self, message: str) -> None:
        """Show error message."""
        self.update(message)
        self.remove_class("hidden")

    def clear_error(self) -> None:
        """Clear error message."""
        self.update("")
        self.add_class("hidden")


# Usage in form
class AddTaskModal(ModalScreen):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Title:")
            yield Input(id="title-input")
            yield ErrorDisplay(id="title-error")

            yield Label("Description:")
            yield Input(id="desc-input")
            yield ErrorDisplay(id="desc-error")

    def validate_and_submit(self) -> None:
        title = self.query_one("#title-input", Input).value.strip()

        if not title:
            self.query_one("#title-error", ErrorDisplay).show_error(
                "Title is required"
            )
            self.query_one("#title-input").focus()
            return

        self.query_one("#title-error", ErrorDisplay).clear_error()
        # Continue with submission...
```

### Validation on Input Change

```python
class FormModal(ModalScreen):
    """Form with real-time validation."""

    def on_input_changed(self, event: Input.Changed) -> None:
        """Validate on input change."""
        if event.input.id == "title-input":
            self._validate_title(event.value)

    def _validate_title(self, value: str) -> bool:
        """Validate title field."""
        error_display = self.query_one("#title-error", ErrorDisplay)

        if not value.strip():
            error_display.show_error("Title cannot be empty")
            return False

        if len(value) > 200:
            error_display.show_error(
                f"Title too long ({len(value)}/200)"
            )
            return False

        error_display.clear_error()
        return True
```

## Status Bar Updates

### Status Bar Widget

```python
# src/todo/tui/components/status_bar.py
from textual.widgets import Static
from textual.reactive import reactive


class StatusBar(Static):
    """
    Status bar with task counts and messages.

    Updates reactively when state changes.
    """

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: $surface-darken-1;
        padding: 0 1;
        color: $text-muted;
    }

    StatusBar .status-message {
        color: $text;
    }

    StatusBar .status-error {
        color: $error;
    }

    StatusBar .status-success {
        color: $success;
    }
    """

    # Reactive counts
    total: reactive[int] = reactive(0)
    completed: reactive[int] = reactive(0)
    message: reactive[str] = reactive("")
    message_style: reactive[str] = reactive("")

    def render(self) -> str:
        """Render status bar content."""
        pending = self.total - self.completed

        parts = [
            f"[bold]{self.total}[/] tasks",
            f"[green]{self.completed}[/] done",
            f"[yellow]{pending}[/] pending",
        ]

        status = " • ".join(parts)

        if self.message:
            style = self.message_style or "dim"
            status += f" | [{style}]{self.message}[/]"

        return status

    def set_message(
        self,
        message: str,
        style: str = "",
        timeout: float = 3.0,
    ) -> None:
        """
        Set temporary message.

        Args:
            message: Message to display
            style: Rich style for message
            timeout: Seconds before clearing
        """
        self.message = message
        self.message_style = style

        if timeout > 0:
            self.set_timer(timeout, self.clear_message)

    def clear_message(self) -> None:
        """Clear message."""
        self.message = ""
        self.message_style = ""

    def update_counts(self, total: int, completed: int) -> None:
        """Update task counts."""
        self.total = total
        self.completed = completed
```

### Using Status Bar

```python
class MainScreen(Screen):
    """Main screen with status bar."""

    def compose(self) -> ComposeResult:
        yield TaskListView()
        yield StatusBar(id="status-bar")

    def on_mount(self) -> None:
        self._refresh_status()

    def _refresh_status(self) -> None:
        """Update status bar counts."""
        tasks = self.task_service.get_all_tasks()
        status_bar = self.query_one(StatusBar)
        status_bar.update_counts(
            total=len(tasks),
            completed=sum(1 for t in tasks if t.completed),
        )

    def show_status_message(self, message: str, style: str = "") -> None:
        """Show temporary status message."""
        self.query_one(StatusBar).set_message(message, style)

    # After actions
    def on_task_created(self, task: Task) -> None:
        self._refresh_status()
        self.show_status_message(f"Created: {task.title}", "green")

    def on_task_deleted(self, title: str) -> None:
        self._refresh_status()
        self.show_status_message(f"Deleted: {title}", "yellow")
```

## Loading States

### Loading Indicator

```python
from textual.widgets import LoadingIndicator, Static


class LoadingOverlay(Static):
    """
    Overlay shown during loading operations.

    Usage:
        async def long_operation(self):
            self.query_one(LoadingOverlay).show("Loading...")
            await self.do_work()
            self.query_one(LoadingOverlay).hide()
    """

    DEFAULT_CSS = """
    LoadingOverlay {
        display: none;
        layer: loading;
        width: 100%;
        height: 100%;
        align: center middle;
        background: $surface 80%;
    }

    LoadingOverlay.visible {
        display: block;
    }

    LoadingOverlay LoadingIndicator {
        width: auto;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield LoadingIndicator()
        yield Static("Loading...", id="loading-text")

    def show(self, message: str = "Loading...") -> None:
        """Show loading overlay."""
        self.query_one("#loading-text", Static).update(message)
        self.add_class("visible")

    def hide(self) -> None:
        """Hide loading overlay."""
        self.remove_class("visible")
```

### Progress Indication

```python
from textual.widgets import ProgressBar


class ProgressModal(ModalScreen):
    """Modal with progress bar."""

    DEFAULT_CSS = """
    #progress-dialog {
        background: $surface;
        border: solid $primary;
        padding: 1 2;
        width: 50;
    }
    """

    def __init__(self, title: str = "Processing...") -> None:
        super().__init__()
        self.title = title

    def compose(self) -> ComposeResult:
        with Vertical(id="progress-dialog"):
            yield Label(self.title)
            yield ProgressBar(id="progress")
            yield Static("", id="progress-status")

    def update_progress(self, progress: float, status: str = "") -> None:
        """
        Update progress.

        Args:
            progress: Value 0.0 to 1.0
            status: Status text
        """
        self.query_one("#progress", ProgressBar).update(progress=progress)
        if status:
            self.query_one("#progress-status", Static).update(status)
```

## Message Patterns

### Custom Messages for Feedback

```python
# src/todo/tui/messages.py
from textual.message import Message
from todo.models.task import Task


class TaskActionCompleted(Message):
    """Posted when a task action completes."""

    def __init__(
        self,
        action: str,
        task: Task | None = None,
        success: bool = True,
        message: str = "",
    ) -> None:
        self.action = action
        self.task = task
        self.success = success
        self.message = message
        super().__init__()


class ErrorOccurred(Message):
    """Posted when an error occurs."""

    def __init__(self, error: Exception, context: str = "") -> None:
        self.error = error
        self.context = context
        super().__init__()


# Handling in App
class TodoApp(App):
    def on_task_action_completed(self, event: TaskActionCompleted) -> None:
        """Handle task action completion."""
        if event.success:
            self.notify(
                event.message or f"Task {event.action}d",
                severity="information",
            )
        else:
            self.notify(
                event.message or f"Failed to {event.action}",
                severity="error",
            )

    def on_error_occurred(self, event: ErrorOccurred) -> None:
        """Handle errors."""
        context = f" ({event.context})" if event.context else ""
        self.notify(
            f"{event.error}{context}",
            title="Error",
            severity="error",
        )
```

## Testing Patterns

```python
# tests/tui/test_feedback.py
import pytest
from textual.testing import AppTester


class TestNotifications:
    """Tests for notification system."""

    async def test_success_notification(self, app_tester, task_service):
        """Success action shows notification."""
        await app_tester.press("a")
        await app_tester.type("Test task")
        await app_tester.press("ctrl+s")

        # Notification should appear
        # (Note: Testing notifications requires checking app state)

    async def test_error_notification(self, app_tester):
        """Error shows error notification."""
        await app_tester.press("a")
        await app_tester.press("ctrl+s")  # Submit empty

        # Error should be shown


class TestConfirmation:
    """Tests for confirmation dialogs."""

    async def test_delete_shows_confirm(self, app_tester, sample_task):
        """Delete action shows confirmation."""
        await app_tester.press("d")

        assert app_tester.app.query_one(ConfirmModal)

    async def test_escape_cancels_confirm(self, app_tester, sample_task):
        """Escape cancels confirmation."""
        await app_tester.press("d")
        await app_tester.press("escape")

        # Task should still exist
        assert len(app_tester.app.task_service.get_all_tasks()) == 1

    async def test_confirm_deletes(self, app_tester, sample_task):
        """Confirming deletes task."""
        await app_tester.press("d")
        await app_tester.press("enter")  # Confirm

        assert len(app_tester.app.task_service.get_all_tasks()) == 0


class TestStatusBar:
    """Tests for status bar."""

    async def test_counts_update(self, app_tester, task_service):
        """Status bar updates after action."""
        status = app_tester.app.query_one(StatusBar)

        # Add task
        await app_tester.press("a")
        await app_tester.type("Test")
        await app_tester.press("ctrl+s")

        assert status.total == 1
```

## Running Tests

```bash
# Run feedback tests
uv run pytest tests/tui/test_feedback.py -v

# Run notification tests
uv run pytest tests/tui/test_feedback.py -k "notification" -v
```

## Checklist

Before completing feedback implementation:
- [ ] Success actions show notifications
- [ ] Errors show clear messages
- [ ] Destructive actions require confirmation
- [ ] Form errors display inline
- [ ] Status bar updates reactively
- [ ] Loading states are visible
- [ ] Notifications auto-dismiss
- [ ] Tests verify feedback flow
