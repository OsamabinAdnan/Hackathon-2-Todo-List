---
name: tui-input-validation
description: Build input forms, modals, and user input validation for Textual TUI applications. Use this skill when creating modal dialogs, form inputs, validation feedback, input parsing, and guided prompts. Covers ModalScreen, Input widgets, Select widgets, and validation patterns.
---

# TUI Input & Validation

Modal dialogs, form inputs, and validation patterns for Textual applications.

## Overview

This skill provides patterns for:

- **Modal Dialogs**: Add/Edit/Confirm modal patterns
- **Input Widgets**: Text input, Select, date input
- **Validation**: Input validation with error display
- **Form Handling**: Multi-field forms with submission
- **Input Parsing**: Parsing dates, tags, priorities

## Modal Screen Pattern

### Base Modal Template

```python
# src/todo/tui/modals/base.py
"""Base modal patterns."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Static
from textual.containers import Container


class BaseModal(ModalScreen):
    """
    Base modal with common patterns.

    Provides escape handling and basic structure.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", priority=True),
    ]

    def action_cancel(self) -> None:
        """Cancel and close modal."""
        self.dismiss(None)
```

### Add Task Modal

```python
# src/todo/tui/modals/add_task.py
"""Add task modal dialog."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Input, Button, Label, Select, Static
from textual.containers import Vertical, Horizontal
from textual.validation import Length

from todo.services.task_service import TaskService
from todo.models.enums import Priority
from todo.models.exceptions import ValidationError


class AddTaskModal(ModalScreen[bool]):
    """
    Modal dialog for adding a new task.

    Returns True if task was created, None if cancelled.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", priority=True),
        Binding("ctrl+s", "submit", "Submit", show=False),
    ]

    CSS = """
    AddTaskModal {
        align: center middle;
    }

    #add-task-dialog {
        background: $surface;
        border: solid $primary;
        padding: 1 2;
        width: 60;
        height: auto;
        max-height: 80%;
    }

    #dialog-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    .field-label {
        margin-top: 1;
    }

    .error-message {
        color: $error;
        margin-left: 1;
    }

    #button-row {
        margin-top: 2;
        align: center middle;
    }

    #button-row Button {
        margin: 0 1;
    }
    """

    def __init__(self, task_service: TaskService) -> None:
        """
        Initialize with task service.

        Args:
            task_service: TaskService for creating tasks
        """
        super().__init__()
        self.task_service = task_service
        self._error: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Vertical(id="add-task-dialog"):
            yield Label("Add New Task", id="dialog-title")

            yield Label("Title:", classes="field-label")
            yield Input(
                placeholder="Enter task title...",
                id="title-input",
                validators=[Length(minimum=1, maximum=200)],
            )
            yield Static("", id="title-error", classes="error-message")

            yield Label("Description:", classes="field-label")
            yield Input(
                placeholder="Optional description...",
                id="desc-input",
            )

            yield Label("Priority:", classes="field-label")
            yield Select(
                [(p.value.title(), p.value) for p in Priority],
                value=Priority.MEDIUM.value,
                id="priority-select",
            )

            yield Label("Tags (comma-separated):", classes="field-label")
            yield Input(
                placeholder="work, urgent, home...",
                id="tags-input",
            )

            with Horizontal(id="button-row"):
                yield Button("Cancel", variant="default", id="cancel-btn")
                yield Button("Add Task", variant="primary", id="submit-btn")

    def on_mount(self) -> None:
        """Focus title input on mount."""
        self.query_one("#title-input").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.action_cancel()
        elif event.button.id == "submit-btn":
            self.action_submit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in inputs."""
        if event.input.id == "title-input":
            # Move to description
            self.query_one("#desc-input").focus()
        elif event.input.id == "desc-input":
            # Move to tags
            self.query_one("#tags-input").focus()
        elif event.input.id == "tags-input":
            # Submit form
            self.action_submit()

    def action_cancel(self) -> None:
        """Cancel and close modal."""
        self.dismiss(None)

    def action_submit(self) -> None:
        """Validate and submit the new task."""
        # Collect form data
        title = self.query_one("#title-input", Input).value.strip()
        description = self.query_one("#desc-input", Input).value.strip()
        priority_value = self.query_one("#priority-select", Select).value
        tags_text = self.query_one("#tags-input", Input).value.strip()

        # Validate title
        if not title:
            self._show_error("title-error", "Title is required")
            self.query_one("#title-input").focus()
            return

        if len(title) > 200:
            self._show_error("title-error", "Title cannot exceed 200 characters")
            self.query_one("#title-input").focus()
            return

        # Clear any previous errors
        self._show_error("title-error", "")

        # Parse tags
        tags = self._parse_tags(tags_text)

        try:
            # Create task
            task = self.task_service.add_task(title, description)

            # Set priority if changed
            if priority_value and priority_value != Priority.MEDIUM.value:
                priority = Priority.from_string(str(priority_value))
                self.task_service.set_priority(task.id, priority)

            # Add tags
            for tag in tags:
                self.task_service.add_tag(task.id, tag)

            # Success - dismiss with True
            self.dismiss(True)

        except ValidationError as e:
            self._show_error("title-error", str(e))

    def _show_error(self, error_id: str, message: str) -> None:
        """Display error message."""
        error_widget = self.query_one(f"#{error_id}", Static)
        error_widget.update(message)

    def _parse_tags(self, tags_text: str) -> list[str]:
        """Parse comma-separated tags."""
        if not tags_text:
            return []
        return [
            tag.strip().lower()
            for tag in tags_text.split(",")
            if tag.strip()
        ]
```

### Edit Task Modal

```python
# src/todo/tui/modals/edit_task.py
"""Edit task modal dialog."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Input, Button, Label, Select, Static, Checkbox
from textual.containers import Vertical, Horizontal

from todo.services.task_service import TaskService
from todo.models.task import Task
from todo.models.enums import Priority
from todo.models.exceptions import ValidationError


class EditTaskModal(ModalScreen[bool]):
    """Modal for editing an existing task."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", priority=True),
        Binding("ctrl+s", "submit", "Save", show=False),
    ]

    CSS = """
    EditTaskModal {
        align: center middle;
    }

    #edit-task-dialog {
        background: $surface;
        border: solid $primary;
        padding: 1 2;
        width: 60;
        height: auto;
    }
    """

    def __init__(self, task_service: TaskService, task: Task) -> None:
        """
        Initialize with task to edit.

        Args:
            task_service: TaskService for updating tasks
            task: Task instance to edit
        """
        super().__init__()
        self.task_service = task_service
        self.task = task

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Vertical(id="edit-task-dialog"):
            yield Label("Edit Task", id="dialog-title")

            yield Label("Title:", classes="field-label")
            yield Input(
                value=self.task.title,
                placeholder="Enter task title...",
                id="title-input",
            )
            yield Static("", id="title-error", classes="error-message")

            yield Label("Description:", classes="field-label")
            yield Input(
                value=self.task.description or "",
                placeholder="Optional description...",
                id="desc-input",
            )

            yield Label("Priority:", classes="field-label")
            yield Select(
                [(p.value.title(), p.value) for p in Priority],
                value=self.task.priority.value,
                id="priority-select",
            )

            yield Label("Tags (comma-separated):", classes="field-label")
            yield Input(
                value=", ".join(self.task.tags),
                placeholder="work, urgent, home...",
                id="tags-input",
            )

            yield Checkbox("Completed", value=self.task.completed, id="completed-check")

            with Horizontal(id="button-row"):
                yield Button("Cancel", variant="default", id="cancel-btn")
                yield Button("Save Changes", variant="primary", id="submit-btn")

    def on_mount(self) -> None:
        """Focus title input on mount."""
        self.query_one("#title-input").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.action_cancel()
        elif event.button.id == "submit-btn":
            self.action_submit()

    def action_cancel(self) -> None:
        """Cancel and close modal."""
        self.dismiss(None)

    def action_submit(self) -> None:
        """Validate and save changes."""
        title = self.query_one("#title-input", Input).value.strip()
        description = self.query_one("#desc-input", Input).value.strip()
        priority_value = self.query_one("#priority-select", Select).value
        tags_text = self.query_one("#tags-input", Input).value.strip()
        completed = self.query_one("#completed-check", Checkbox).value

        # Validate
        if not title:
            self._show_error("title-error", "Title is required")
            return

        try:
            # Update task
            self.task_service.update_task(
                self.task.id,
                title=title,
                description=description,
            )

            # Update priority
            priority = Priority.from_string(str(priority_value))
            self.task_service.set_priority(self.task.id, priority)

            # Update tags
            self._update_tags(tags_text)

            # Update completion
            if completed and not self.task.completed:
                self.task_service.mark_complete(self.task.id)
            elif not completed and self.task.completed:
                self.task_service.mark_incomplete(self.task.id)

            self.dismiss(True)

        except ValidationError as e:
            self._show_error("title-error", str(e))

    def _show_error(self, error_id: str, message: str) -> None:
        """Display error message."""
        self.query_one(f"#{error_id}", Static).update(message)

    def _update_tags(self, tags_text: str) -> None:
        """Update task tags."""
        new_tags = set(
            tag.strip().lower()
            for tag in tags_text.split(",")
            if tag.strip()
        )
        current_tags = set(self.task.tags)

        # Remove old tags
        for tag in current_tags - new_tags:
            self.task_service.remove_tag(self.task.id, tag)

        # Add new tags
        for tag in new_tags - current_tags:
            self.task_service.add_tag(self.task.id, tag)
```

### Confirm Modal

```python
# src/todo/tui/modals/confirm.py
"""Confirmation modal dialog."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.binding import Binding
from textual.widgets import Button, Label, Static
from textual.containers import Vertical, Horizontal


class ConfirmModal(ModalScreen[bool]):
    """
    Confirmation dialog for destructive actions.

    Returns True if confirmed, False/None if cancelled.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", priority=True),
        Binding("enter", "confirm", "Confirm", priority=True),
        Binding("y", "confirm", "Yes", show=False),
        Binding("n", "cancel", "No", show=False),
    ]

    CSS = """
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

    #button-row {
        margin-top: 1;
        align: center middle;
    }

    #button-row Button {
        margin: 0 1;
    }
    """

    def __init__(
        self,
        message: str,
        title: str = "Confirm",
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
    ) -> None:
        """
        Initialize confirmation modal.

        Args:
            message: Message to display
            title: Dialog title
            confirm_label: Text for confirm button
            cancel_label: Text for cancel button
        """
        super().__init__()
        self.message = message
        self.title_text = title
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label

    def compose(self) -> ComposeResult:
        """Compose the confirmation dialog."""
        with Vertical(id="confirm-dialog"):
            yield Label(self.title_text, id="confirm-title")
            yield Static(self.message, id="confirm-message")

            with Horizontal(id="button-row"):
                yield Button(
                    self.cancel_label,
                    variant="default",
                    id="cancel-btn",
                )
                yield Button(
                    self.confirm_label,
                    variant="error",
                    id="confirm-btn",
                )

    def on_mount(self) -> None:
        """Focus cancel button by default (safer)."""
        self.query_one("#cancel-btn").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.action_cancel()
        elif event.button.id == "confirm-btn":
            self.action_confirm()

    def action_cancel(self) -> None:
        """Cancel action."""
        self.dismiss(False)

    def action_confirm(self) -> None:
        """Confirm action."""
        self.dismiss(True)
```

## Input Validation Patterns

### Textual Validators

```python
from textual.validation import Length, Number, Regex

# Length validation
Input(
    validators=[Length(minimum=1, maximum=200)],
    id="title-input",
)

# Number validation
Input(
    validators=[Number(minimum=0, maximum=100)],
    id="quantity-input",
)

# Regex validation
Input(
    validators=[Regex(r"^\d{4}-\d{2}-\d{2}$", failure_description="Use YYYY-MM-DD format")],
    id="date-input",
)

# Multiple validators
Input(
    validators=[
        Length(minimum=1, failure_description="Required"),
        Regex(r"^[a-z0-9-]+$", failure_description="Only lowercase, numbers, hyphens"),
    ],
    id="tag-input",
)
```

### Custom Validators

```python
from textual.validation import Validator, ValidationResult

class NonEmptyValidator(Validator):
    """Validate that input is not empty or whitespace."""

    def validate(self, value: str) -> ValidationResult:
        """Check if value is non-empty."""
        if not value.strip():
            return self.failure("This field is required")
        return self.success()


class TagValidator(Validator):
    """Validate tag format."""

    def validate(self, value: str) -> ValidationResult:
        """Check tag format."""
        if not value:
            return self.success()  # Tags are optional

        for tag in value.split(","):
            tag = tag.strip()
            if tag and not tag.replace("-", "").replace("_", "").isalnum():
                return self.failure(f"Invalid tag: {tag}")

        return self.success()
```

### Validation Events

```python
class MyModal(ModalScreen):
    """Modal with validation handling."""

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes with validation."""
        if not event.validation_result.is_valid:
            # Show first failure message
            failures = event.validation_result.failure_descriptions
            self._show_error(f"{event.input.id}-error", failures[0])
        else:
            self._show_error(f"{event.input.id}-error", "")

    def _show_error(self, error_id: str, message: str) -> None:
        """Update error display."""
        try:
            self.query_one(f"#{error_id}", Static).update(message)
        except Exception:
            pass  # Error widget might not exist
```

## Input Parsing Patterns

### Date Parsing

```python
from datetime import datetime, date

def parse_date_input(value: str) -> date | None:
    """
    Parse flexible date input.

    Supports:
    - YYYY-MM-DD
    - MM/DD/YYYY
    - today, tomorrow
    - +N (N days from now)

    Returns:
        Parsed date or None if invalid
    """
    value = value.strip().lower()

    if not value:
        return None

    # Relative dates
    if value == "today":
        return date.today()
    if value == "tomorrow":
        return date.today() + timedelta(days=1)

    # +N days
    if value.startswith("+") and value[1:].isdigit():
        days = int(value[1:])
        return date.today() + timedelta(days=days)

    # ISO format: YYYY-MM-DD
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        pass

    # US format: MM/DD/YYYY
    try:
        return datetime.strptime(value, "%m/%d/%Y").date()
    except ValueError:
        pass

    return None
```

### Priority Parsing

```python
def parse_priority_input(value: str) -> Priority:
    """
    Parse priority from various formats.

    Supports:
    - Full names: low, medium, high, critical
    - Single letters: l, m, h, c
    - Numbers: 1, 2, 3, 4

    Returns:
        Priority enum value
    """
    value = value.strip().lower()

    # Full names
    name_map = {
        "low": Priority.LOW,
        "medium": Priority.MEDIUM,
        "high": Priority.HIGH,
        "critical": Priority.CRITICAL,
    }
    if value in name_map:
        return name_map[value]

    # Single letters
    letter_map = {"l": Priority.LOW, "m": Priority.MEDIUM, "h": Priority.HIGH, "c": Priority.CRITICAL}
    if value in letter_map:
        return letter_map[value]

    # Numbers
    number_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH, "4": Priority.CRITICAL}
    if value in number_map:
        return number_map[value]

    # Default
    return Priority.MEDIUM
```

## Testing Patterns

### Modal Tests

```python
# tests/tui/test_modals.py
import pytest
from textual.testing import AppTester
from todo.tui.app import TodoApp
from todo.tui.modals.add_task import AddTaskModal


@pytest.fixture
async def app_tester(task_service):
    """App tester fixture."""
    app = TodoApp(task_service=task_service)
    async with AppTester.run_test(app) as tester:
        yield tester


class TestAddTaskModal:
    """Tests for AddTaskModal."""

    async def test_modal_opens(self, app_tester):
        """'a' key opens add task modal."""
        await app_tester.press("a")

        assert app_tester.app.query_one(AddTaskModal)

    async def test_modal_closes_on_escape(self, app_tester):
        """Escape closes modal."""
        await app_tester.press("a")
        await app_tester.press("escape")

        assert len(app_tester.app.query(AddTaskModal)) == 0

    async def test_empty_title_shows_error(self, app_tester):
        """Empty title shows validation error."""
        await app_tester.press("a")
        await app_tester.press("ctrl+s")  # Submit empty

        error = app_tester.app.query_one("#title-error", Static)
        assert "required" in error.renderable.lower()

    async def test_valid_task_creates(self, app_tester, task_service):
        """Valid input creates task."""
        await app_tester.press("a")
        await app_tester.type("Test task")
        await app_tester.press("ctrl+s")

        assert len(task_service.get_all_tasks()) == 1
        assert task_service.get_all_tasks()[0].title == "Test task"

    async def test_tab_navigation(self, app_tester):
        """Tab moves between fields."""
        await app_tester.press("a")

        # Should start on title
        assert app_tester.app.query_one("#title-input").has_focus

        await app_tester.press("tab")
        assert app_tester.app.query_one("#desc-input").has_focus


class TestConfirmModal:
    """Tests for ConfirmModal."""

    async def test_cancel_returns_false(self, app_tester):
        """Cancel button returns False."""
        # Setup: trigger delete which shows confirm
        # ... (implementation specific)
        pass

    async def test_y_key_confirms(self, app_tester):
        """'y' key confirms action."""
        pass

    async def test_n_key_cancels(self, app_tester):
        """'n' key cancels action."""
        pass
```

## Running Tests

```bash
# Run modal tests
uv run pytest tests/tui/test_modals.py -v

# Run validation tests
uv run pytest tests/tui/test_modals.py -k "validation" -v
```

## Checklist

Before completing input/validation implementation:
- [ ] Modal has escape to cancel
- [ ] Form fields have proper validation
- [ ] Validation errors display clearly
- [ ] Tab navigates between fields
- [ ] Enter submits from last field
- [ ] Focus starts on first input
- [ ] Invalid input doesn't crash
- [ ] Tests cover validation cases
