---
name: tui-output-styling
description: Create widgets, style components with TCSS, and structure output displays for Textual TUI applications. Use this skill when building reusable widgets, styling with Textual CSS, creating data tables, lists, and maintaining visual consistency across the application.
---

# TUI Output & Styling

Widgets, component styling, and visual patterns for Textual applications.

## Overview

This skill provides patterns for:

- **Widget Creation**: Static, Custom widgets, Containers
- **TCSS Styling**: Textual CSS patterns and variables
- **Data Display**: DataTable, ListView, structured output
- **Layouts**: Horizontal, Vertical, Grid layouts
- **Visual Consistency**: Theme variables, component classes

## Widget Patterns

### Task List View

```python
# src/todo/tui/components/task_list.py
"""Task list widget."""

from textual.app import ComposeResult
from textual.widgets import ListView, ListItem, Static
from textual.message import Message

from todo.services.task_service import TaskService
from todo.models.task import Task
from todo.tui.components.task_item import TaskItem


class TaskListView(ListView):
    """
    Scrollable list of tasks.

    Displays tasks with selection support and keyboard navigation.
    Emits messages when tasks are selected or actions performed.
    """

    class TaskSelected(Message):
        """Message sent when a task is selected."""

        def __init__(self, task: Task) -> None:
            self.task = task
            super().__init__()

    class TaskActionRequested(Message):
        """Message sent when action requested on task."""

        def __init__(self, task: Task, action: str) -> None:
            self.task = task
            self.action = action
            super().__init__()

    def __init__(self, task_service: TaskService, **kwargs) -> None:
        """
        Initialize with task service.

        Args:
            task_service: TaskService for data operations
        """
        super().__init__(**kwargs)
        self.task_service = task_service

    def compose(self) -> ComposeResult:
        """Compose the task list."""
        tasks = self.task_service.get_all_tasks()

        if not tasks:
            yield ListItem(
                Static(
                    "[dim]No tasks yet. Press 'a' to add one![/dim]",
                    classes="empty-placeholder",
                )
            )
            return

        for task in tasks:
            yield ListItem(TaskItem(task))

    def refresh_tasks(self) -> None:
        """Refresh the task list from service."""
        self.clear()
        tasks = self.task_service.get_all_tasks()

        if not tasks:
            self.append(
                ListItem(
                    Static(
                        "[dim]No tasks yet. Press 'a' to add one![/dim]",
                        classes="empty-placeholder",
                    )
                )
            )
            return

        for task in tasks:
            self.append(ListItem(TaskItem(task)))

    def get_selected_task(self) -> Task | None:
        """Get the currently selected task."""
        if self.highlighted_child is None:
            return None

        try:
            task_item = self.highlighted_child.query_one(TaskItem)
            return task_item.task
        except Exception:
            return None

    def delete_selected(self) -> None:
        """Request deletion of selected task."""
        task = self.get_selected_task()
        if task:
            self.post_message(self.TaskActionRequested(task, "delete"))

    def edit_selected(self) -> None:
        """Request edit of selected task."""
        task = self.get_selected_task()
        if task:
            self.post_message(self.TaskActionRequested(task, "edit"))

    def toggle_selected(self) -> None:
        """Toggle completion of selected task."""
        task = self.get_selected_task()
        if task:
            if task.completed:
                self.task_service.mark_incomplete(task.id)
            else:
                self.task_service.mark_complete(task.id)
            self.refresh_tasks()

    def cycle_priority(self) -> None:
        """Cycle priority of selected task."""
        task = self.get_selected_task()
        if task:
            from todo.models.enums import Priority

            priorities = list(Priority)
            current_idx = priorities.index(task.priority)
            next_idx = (current_idx + 1) % len(priorities)
            self.task_service.set_priority(task.id, priorities[next_idx])
            self.refresh_tasks()

    def manage_tags(self) -> None:
        """Open tag management for selected task."""
        task = self.get_selected_task()
        if task:
            self.post_message(self.TaskActionRequested(task, "tags"))
```

### Task Item Widget

```python
# src/todo/tui/components/task_item.py
"""Individual task item widget."""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Horizontal

from todo.models.task import Task
from todo.models.enums import Priority


PRIORITY_STYLES = {
    Priority.LOW: ("green", "L"),
    Priority.MEDIUM: ("yellow", "M"),
    Priority.HIGH: ("red", "H"),
    Priority.CRITICAL: ("red bold", "!"),
}


class TaskItem(Static):
    """
    Single task item display.

    Shows checkbox, title, priority badge, and tags.
    Applies styling based on completion and priority.
    """

    def __init__(self, task: Task) -> None:
        """
        Initialize with task data.

        Args:
            task: Task instance to display
        """
        super().__init__()
        self.task = task

        # Set classes for styling
        if task.completed:
            self.add_class("completed")
        else:
            self.add_class("pending")

        self.add_class(f"priority-{task.priority.value}")

    def compose(self) -> ComposeResult:
        """Compose the task item layout."""
        yield Static(self._render_task())

    def _render_task(self) -> str:
        """Render task as Rich markup string."""
        # Checkbox
        checkbox = "[green]✓[/]" if self.task.completed else "○"

        # Title with strikethrough if completed
        if self.task.completed:
            title = f"[dim strike]{self.task.title}[/]"
        else:
            title = self.task.title

        # Priority badge
        style, letter = PRIORITY_STYLES.get(
            self.task.priority,
            ("white", "?"),
        )
        priority_badge = f"[{style}][{letter}][/]"

        # Tags
        if self.task.tags:
            tags = " ".join(f"[cyan]#{tag}[/]" for tag in self.task.tags[:3])
            if len(self.task.tags) > 3:
                tags += f" [dim]+{len(self.task.tags) - 3}[/]"
        else:
            tags = ""

        # Due date indicator
        due_indicator = ""
        if self.task.due_date:
            from datetime import date

            if self.task.due_date.date() < date.today():
                due_indicator = " [red bold]OVERDUE[/]"
            elif self.task.due_date.date() == date.today():
                due_indicator = " [yellow]TODAY[/]"

        return f"{checkbox} {title} {priority_badge} {tags}{due_indicator}"
```

### Sidebar Widget

```python
# src/todo/tui/components/sidebar.py
"""Sidebar with filters and search."""

from textual.app import ComposeResult
from textual.widgets import Static, Input, RadioSet, RadioButton
from textual.containers import Vertical
from textual.message import Message


class Sidebar(Static):
    """
    Sidebar with search and filter options.

    Contains search input, priority filter, and tag filter.
    Emits messages when filters change.
    """

    class FilterChanged(Message):
        """Message sent when filters change."""

        def __init__(
            self,
            search_query: str = "",
            priority_filter: str | None = None,
            show_completed: bool = True,
        ) -> None:
            self.search_query = search_query
            self.priority_filter = priority_filter
            self.show_completed = show_completed
            super().__init__()

    def compose(self) -> ComposeResult:
        """Compose sidebar layout."""
        with Vertical(id="sidebar-content"):
            yield Static("[bold]Search[/]", classes="sidebar-header")
            yield Input(
                placeholder="Search tasks...",
                id="search-input",
            )

            yield Static("[bold]Priority[/]", classes="sidebar-header")
            with RadioSet(id="priority-filter"):
                yield RadioButton("All", id="priority-all", value=True)
                yield RadioButton("High", id="priority-high")
                yield RadioButton("Medium", id="priority-medium")
                yield RadioButton("Low", id="priority-low")

            yield Static("[bold]Status[/]", classes="sidebar-header")
            with RadioSet(id="status-filter"):
                yield RadioButton("All", id="status-all", value=True)
                yield RadioButton("Active", id="status-active")
                yield RadioButton("Completed", id="status-completed")

    def focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input").focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self._emit_filter_change()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle filter radio changes."""
        self._emit_filter_change()

    def _emit_filter_change(self) -> None:
        """Emit filter changed message."""
        search = self.query_one("#search-input", Input).value
        priority_set = self.query_one("#priority-filter", RadioSet)
        status_set = self.query_one("#status-filter", RadioSet)

        # Get priority filter
        priority_filter = None
        if priority_set.pressed_button:
            btn_id = priority_set.pressed_button.id
            if btn_id != "priority-all":
                priority_filter = btn_id.replace("priority-", "")

        # Get show_completed
        show_completed = True
        if status_set.pressed_button:
            btn_id = status_set.pressed_button.id
            if btn_id == "status-active":
                show_completed = False

        self.post_message(
            self.FilterChanged(
                search_query=search,
                priority_filter=priority_filter,
                show_completed=show_completed,
            )
        )
```

### Status Bar Widget

```python
# src/todo/tui/components/status_bar.py
"""Status bar widget."""

from textual.widgets import Static
from textual.reactive import reactive

from todo.services.task_service import TaskService


class StatusBar(Static):
    """
    Status bar showing task counts and filter info.

    Updates reactively when task counts change.
    """

    total_count: reactive[int] = reactive(0)
    completed_count: reactive[int] = reactive(0)
    filter_info: reactive[str] = reactive("")

    def __init__(self, task_service: TaskService, **kwargs) -> None:
        """
        Initialize with task service.

        Args:
            task_service: TaskService for getting counts
        """
        super().__init__(**kwargs)
        self.task_service = task_service

    def on_mount(self) -> None:
        """Update counts on mount."""
        self.refresh_counts()

    def refresh_counts(self) -> None:
        """Refresh task counts from service."""
        tasks = self.task_service.get_all_tasks()
        self.total_count = len(tasks)
        self.completed_count = sum(1 for t in tasks if t.completed)

    def watch_total_count(self, count: int) -> None:
        """React to total count changes."""
        self._update_display()

    def watch_completed_count(self, count: int) -> None:
        """React to completed count changes."""
        self._update_display()

    def watch_filter_info(self, info: str) -> None:
        """React to filter info changes."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the status bar text."""
        pending = self.total_count - self.completed_count

        parts = [
            f"[bold]{self.total_count}[/] tasks",
            f"[green]{self.completed_count}[/] done",
            f"[yellow]{pending}[/] pending",
        ]

        if self.filter_info:
            parts.append(f"[dim]| {self.filter_info}[/]")

        self.update(" • ".join(parts))
```

## TCSS Styling

### Main Stylesheet

```css
/* src/todo/tui/styles/app.tcss */

/* ===== Variables ===== */
/* Using Textual's built-in theme variables */

/* ===== App Layout ===== */
Screen {
    background: $surface;
}

/* ===== Sidebar ===== */
#sidebar {
    width: 28;
    background: $surface;
    border-right: solid $primary;
    padding: 1;
}

#sidebar-content {
    height: 100%;
}

.sidebar-header {
    margin-top: 1;
    margin-bottom: 0;
    text-style: bold;
    color: $text;
}

#search-input {
    margin-bottom: 1;
}

RadioSet {
    margin-bottom: 1;
}

/* ===== Main Content ===== */
#main-content {
    width: 1fr;
}

#task-list {
    height: 1fr;
    border: none;
}

#status-bar {
    height: 1;
    background: $surface-darken-1;
    padding: 0 1;
    color: $text-muted;
}

/* ===== Task Items ===== */
TaskItem {
    padding: 0 1;
    height: 1;
}

TaskItem:hover {
    background: $surface-lighten-1;
}

TaskItem.completed {
    color: $text-muted;
}

TaskItem.pending {
    color: $text;
}

TaskItem.priority-high {
    border-left: solid red 2;
}

TaskItem.priority-critical {
    border-left: solid red 3;
    background: $error-darken-3;
}

/* ===== Empty State ===== */
.empty-placeholder {
    text-align: center;
    padding: 2;
    color: $text-muted;
}

/* ===== List Selection ===== */
ListView > ListItem.--highlight {
    background: $accent;
}

ListView:focus > ListItem.--highlight {
    background: $accent;
}
```

### Component Stylesheet

```css
/* src/todo/tui/styles/components.tcss */

/* ===== Modal Dialogs ===== */
ModalScreen {
    align: center middle;
}

.modal-dialog {
    background: $surface;
    border: solid $primary;
    padding: 1 2;
    width: 60;
    max-width: 90%;
    height: auto;
    max-height: 80%;
}

.modal-title {
    text-align: center;
    text-style: bold;
    margin-bottom: 1;
    color: $text;
}

.field-label {
    margin-top: 1;
    color: $text-muted;
}

.error-message {
    color: $error;
    margin-left: 1;
    text-style: italic;
}

.button-row {
    margin-top: 2;
    align: center middle;
}

.button-row Button {
    margin: 0 1;
}

/* ===== Confirmation Dialog ===== */
.confirm-dialog {
    background: $surface;
    border: solid $error;
    padding: 1 2;
    width: 50;
}

.confirm-title {
    text-align: center;
    text-style: bold;
    color: $error;
}

.confirm-message {
    text-align: center;
    margin: 1 0;
}

/* ===== Help Screen ===== */
#help-container {
    width: 70;
    height: auto;
    max-height: 90%;
    background: $surface;
    border: solid $primary;
    padding: 1 2;
}

#help-title {
    text-align: center;
    text-style: bold;
    margin-bottom: 1;
}

.help-section {
    margin-top: 1;
    color: $accent;
}

#help-footer {
    text-align: center;
    margin-top: 1;
    color: $text-muted;
}
```

## Layout Patterns

### Horizontal Split

```python
from textual.containers import Horizontal, Vertical

def compose(self) -> ComposeResult:
    """Two-column layout."""
    with Horizontal():
        yield Sidebar(id="sidebar")  # Fixed width in CSS
        yield MainContent(id="main")  # Takes remaining space (1fr)
```

### Vertical Sections

```python
def compose(self) -> ComposeResult:
    """Stacked sections."""
    with Vertical():
        yield Header()              # Auto height
        yield TaskListView()        # Flex: 1fr
        yield StatusBar()           # Fixed height: 1
```

### Grid Layout

```python
from textual.containers import Grid

def compose(self) -> ComposeResult:
    """Grid layout."""
    with Grid(id="grid"):
        yield Widget1()
        yield Widget2()
        yield Widget3()
        yield Widget4()

# CSS
"""
#grid {
    grid-size: 2 2;  /* 2 columns, 2 rows */
    grid-gutter: 1;
}
"""
```

## DataTable Pattern

```python
from textual.widgets import DataTable

class TaskTable(DataTable):
    """Task display using DataTable."""

    def on_mount(self) -> None:
        """Set up columns."""
        self.add_columns("Status", "Title", "Priority", "Due Date")
        self.cursor_type = "row"

    def load_tasks(self, tasks: list[Task]) -> None:
        """Load tasks into table."""
        self.clear()
        for task in tasks:
            status = "✓" if task.completed else "○"
            due = task.due_date.strftime("%Y-%m-%d") if task.due_date else "-"
            self.add_row(
                status,
                task.title,
                task.priority.value,
                due,
                key=task.id,
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        task_id = event.row_key.value
        self.post_message(TaskSelected(task_id))
```

## Testing Patterns

```python
# tests/tui/test_components.py
import pytest
from textual.testing import AppTester
from todo.tui.app import TodoApp


class TestTaskItem:
    """Tests for TaskItem widget."""

    async def test_completed_task_styling(self, app_tester, task_service):
        """Completed task has correct class."""
        task = task_service.add_task("Test")
        task_service.mark_complete(task.id)

        # Refresh list
        app_tester.app.query_one(TaskListView).refresh_tasks()

        task_item = app_tester.app.query_one(TaskItem)
        assert "completed" in task_item.classes

    async def test_priority_indicator(self, app_tester, task_service):
        """High priority shows indicator."""
        from todo.models.enums import Priority

        task = task_service.add_task("Test")
        task_service.set_priority(task.id, Priority.HIGH)

        app_tester.app.query_one(TaskListView).refresh_tasks()

        task_item = app_tester.app.query_one(TaskItem)
        assert "priority-high" in task_item.classes


class TestStatusBar:
    """Tests for StatusBar widget."""

    async def test_counts_update(self, app_tester, task_service):
        """Status bar shows correct counts."""
        task_service.add_task("Task 1")
        task_service.add_task("Task 2")

        status_bar = app_tester.app.query_one(StatusBar)
        status_bar.refresh_counts()

        assert status_bar.total_count == 2
        assert status_bar.completed_count == 0
```

## Running Tests

```bash
# Run component tests
uv run pytest tests/tui/test_components.py -v

# Run styling tests
uv run pytest tests/tui/test_components.py -k "styling" -v
```

## Checklist

Before completing styling implementation:
- [ ] Widgets use semantic class names
- [ ] TCSS uses theme variables
- [ ] Layouts are responsive
- [ ] Completed items are visually distinct
- [ ] Priority indicators are visible
- [ ] Empty states have helpful messages
- [ ] Focus states are visible
- [ ] Tests verify styling classes
