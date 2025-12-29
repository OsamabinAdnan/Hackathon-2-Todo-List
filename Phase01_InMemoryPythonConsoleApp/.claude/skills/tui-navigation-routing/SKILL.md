---
name: tui-navigation-routing
description: Implement screen management, keyboard bindings, focus handling, and navigation flows for Textual TUI applications. Use this skill when creating screens, managing screen stacks, implementing keyboard shortcuts, handling focus traversal, and building help screens. Covers App, Screen, and navigation patterns.
---

# TUI Navigation & Routing

Screen management, keyboard bindings, and navigation patterns for Textual applications.

## Overview

This skill provides patterns for:

- **App Structure**: Main application setup with bindings
- **Screen Management**: Push/pop screens, screen transitions
- **Keyboard Bindings**: Global and context-specific shortcuts
- **Focus Management**: Focus traversal, default focus
- **Help Screen**: Keyboard shortcut documentation

## App Structure

### Main Application

```python
# src/todo/tui/app.py
"""Main Textual TUI application."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer

from todo.services.task_service import TaskService
from todo.tui.screens.main import MainScreen


class TodoApp(App):
    """
    Todo List TUI Application.

    A full-featured terminal user interface for managing tasks.

    Attributes:
        task_service: TaskService instance for data operations
    """

    TITLE = "Todo App"
    SUB_TITLE = "Manage your tasks"
    CSS_PATH = "styles/app.tcss"

    # Global keyboard bindings
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("question_mark", "help", "Help"),
        Binding("a", "add_task", "Add Task"),
        Binding("slash", "search", "Search"),
    ]

    def __init__(self, task_service: TaskService | None = None) -> None:
        """
        Initialize the Todo App.

        Args:
            task_service: Optional TaskService for dependency injection.
                         Creates new instance if not provided.
        """
        super().__init__()
        self.task_service = task_service or TaskService()

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted - push initial screen."""
        self.push_screen(MainScreen(self.task_service))

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_help(self) -> None:
        """Show help screen."""
        from todo.tui.screens.help import HelpScreen
        self.push_screen(HelpScreen())

    def action_add_task(self) -> None:
        """Open add task modal."""
        from todo.tui.modals.add_task import AddTaskModal
        self.push_screen(AddTaskModal(self.task_service))

    def action_search(self) -> None:
        """Focus search input on main screen."""
        main_screen = self.screen
        if hasattr(main_screen, 'focus_search'):
            main_screen.focus_search()


def main() -> None:
    """Entry point for the TUI application."""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
```

### App Package Init

```python
# src/todo/tui/__init__.py
"""TUI package for Todo application."""

from todo.tui.app import TodoApp, main

__all__ = ["TodoApp", "main"]
```

## Screen Management

### Base Screen Pattern

```python
# src/todo/tui/screens/main.py
"""Main screen with task list."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Static
from textual.containers import Horizontal, Vertical

from todo.services.task_service import TaskService
from todo.tui.components.task_list import TaskListView
from todo.tui.components.sidebar import Sidebar
from todo.tui.components.status_bar import StatusBar


class MainScreen(Screen):
    """
    Main application screen.

    Contains sidebar, task list, and status bar.
    Primary interface for task management.
    """

    # Screen-specific bindings (extend app bindings)
    BINDINGS = [
        Binding("e", "edit_task", "Edit", show=True),
        Binding("d", "delete_task", "Delete", show=True),
        Binding("space", "toggle_complete", "Toggle"),
        Binding("p", "cycle_priority", "Priority"),
        Binding("t", "manage_tags", "Tags"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g", "go_top", "Top", show=False),
        Binding("G", "go_bottom", "Bottom", show=False),
    ]

    def __init__(self, task_service: TaskService) -> None:
        """Initialize with task service."""
        super().__init__()
        self.task_service = task_service

    def compose(self) -> ComposeResult:
        """Compose the main screen layout."""
        with Horizontal():
            yield Sidebar(id="sidebar")
            with Vertical(id="main-content"):
                yield TaskListView(self.task_service, id="task-list")
                yield StatusBar(self.task_service, id="status-bar")

    def on_mount(self) -> None:
        """Set initial focus when screen mounts."""
        self.query_one(TaskListView).focus()

    # Navigation actions
    def action_cursor_down(self) -> None:
        """Move to next task."""
        task_list = self.query_one(TaskListView)
        task_list.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move to previous task."""
        task_list = self.query_one(TaskListView)
        task_list.action_cursor_up()

    def action_go_top(self) -> None:
        """Go to first task."""
        task_list = self.query_one(TaskListView)
        task_list.index = 0

    def action_go_bottom(self) -> None:
        """Go to last task."""
        task_list = self.query_one(TaskListView)
        if task_list.children:
            task_list.index = len(task_list.children) - 1

    # Task actions (delegated to task list)
    def action_edit_task(self) -> None:
        """Edit the currently selected task."""
        self.query_one(TaskListView).edit_selected()

    def action_delete_task(self) -> None:
        """Delete the currently selected task."""
        self.query_one(TaskListView).delete_selected()

    def action_toggle_complete(self) -> None:
        """Toggle completion of selected task."""
        self.query_one(TaskListView).toggle_selected()

    def action_cycle_priority(self) -> None:
        """Cycle priority of selected task."""
        self.query_one(TaskListView).cycle_priority()

    def action_manage_tags(self) -> None:
        """Open tag management for selected task."""
        self.query_one(TaskListView).manage_tags()

    # Public methods
    def focus_search(self) -> None:
        """Focus the search input in sidebar."""
        sidebar = self.query_one(Sidebar)
        sidebar.focus_search()
```

### Help Screen Pattern

```python
# src/todo/tui/screens/help.py
"""Help screen with keyboard shortcuts."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Static, DataTable
from textual.containers import Container


SHORTCUTS = [
    ("General", [
        ("q", "Quit application"),
        ("?", "Show this help"),
        ("a", "Add new task"),
        ("/", "Search/filter tasks"),
    ]),
    ("Task Actions", [
        ("e", "Edit selected task"),
        ("d", "Delete selected task"),
        ("Space", "Toggle complete"),
        ("p", "Cycle priority"),
        ("t", "Manage tags"),
    ]),
    ("Navigation", [
        ("j / Down", "Next task"),
        ("k / Up", "Previous task"),
        ("g", "Go to first task"),
        ("G", "Go to last task"),
    ]),
    ("Modals", [
        ("Enter", "Confirm / Submit"),
        ("Escape", "Cancel / Close"),
        ("Tab", "Next field"),
        ("Shift+Tab", "Previous field"),
    ]),
]


class HelpScreen(Screen):
    """
    Help screen displaying keyboard shortcuts.

    Dismisses on any key press.
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("question_mark", "dismiss", "Close", show=False),
        Binding("q", "dismiss", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        with Container(id="help-container"):
            yield Static("Keyboard Shortcuts", id="help-title")

            for section, shortcuts in SHORTCUTS:
                yield Static(f"\n[bold]{section}[/bold]", classes="help-section")
                table = DataTable(id=f"help-{section.lower().replace(' ', '-')}")
                table.add_columns("Key", "Action")
                for key, action in shortcuts:
                    table.add_row(key, action)
                yield table

            yield Static(
                "\nPress [bold]Escape[/bold] or [bold]?[/bold] to close",
                id="help-footer"
            )

    def action_dismiss(self) -> None:
        """Close the help screen."""
        self.app.pop_screen()

    def on_key(self) -> None:
        """Dismiss on any key press."""
        self.app.pop_screen()
```

## Screen Stack Navigation

### Pushing Screens

```python
# Push modal screen (returns to previous on dismiss)
self.app.push_screen(AddTaskModal(self.task_service))

# Push with callback on dismiss
def on_result(result: bool) -> None:
    if result:
        self.refresh_list()

self.app.push_screen(ConfirmModal("Delete task?"), on_result)

# Replace current screen (no stack)
self.app.switch_screen(OtherScreen())
```

### Popping Screens

```python
# From within a screen/modal
self.app.pop_screen()  # Return to previous screen

# With result value
self.dismiss(True)  # For ModalScreen with callback
```

### Screen Transitions

```python
# Query current screen
current = self.app.screen

# Check screen type
if isinstance(self.app.screen, MainScreen):
    self.app.screen.refresh_tasks()

# Check screen name
if self.app.screen.name == "main":
    ...
```

## Keyboard Bindings

### Binding Definition

```python
from textual.binding import Binding

BINDINGS = [
    # Basic: (key, action, description)
    Binding("q", "quit", "Quit"),

    # With priority (overrides other bindings)
    Binding("escape", "cancel", "Cancel", priority=True),

    # Hidden from footer
    Binding("j", "down", "Down", show=False),

    # With key display override
    Binding("question_mark", "help", "Help", key_display="?"),
]
```

### Special Keys

| Key String | Actual Key |
|------------|------------|
| `"escape"` | Escape |
| `"enter"` | Enter |
| `"space"` | Spacebar |
| `"tab"` | Tab |
| `"backspace"` | Backspace |
| `"delete"` | Delete |
| `"up"` | Arrow Up |
| `"down"` | Arrow Down |
| `"left"` | Arrow Left |
| `"right"` | Arrow Right |
| `"home"` | Home |
| `"end"` | End |
| `"pageup"` | Page Up |
| `"pagedown"` | Page Down |
| `"question_mark"` | ? |
| `"slash"` | / |
| `"ctrl+c"` | Ctrl+C |
| `"ctrl+z"` | Ctrl+Z |

### Action Methods

```python
class MyScreen(Screen):
    BINDINGS = [
        Binding("x", "do_something", "Do Something"),
    ]

    def action_do_something(self) -> None:
        """Handler for 'x' key press."""
        # Action name must match: action_{name}
        self.notify("Did something!")

    # Action with parameter
    BINDINGS = [
        Binding("1", "set_priority(1)", "Low"),
        Binding("2", "set_priority(2)", "Medium"),
    ]

    def action_set_priority(self, level: int) -> None:
        """Set priority level."""
        self.current_priority = level
```

## Focus Management

### Setting Focus

```python
# Focus specific widget
self.query_one("#search-input").focus()

# Focus first focusable child
self.query_one(TaskListView).focus()

# Focus on mount
def on_mount(self) -> None:
    self.query_one("#title-input").focus()
```

### Focus Traversal

```python
# Default: Tab moves to next focusable widget
# Shift+Tab moves to previous

# Customize focus order with can_focus
class MyWidget(Static):
    can_focus = True  # Make widget focusable

# Disable focus
class DisplayWidget(Static):
    can_focus = False

# Check focus
if self.query_one("#input").has_focus:
    ...
```

### Focus Events

```python
from textual.events import Focus, Blur

class MyWidget(Static):
    def on_focus(self, event: Focus) -> None:
        """Called when widget receives focus."""
        self.add_class("focused")

    def on_blur(self, event: Blur) -> None:
        """Called when widget loses focus."""
        self.remove_class("focused")
```

## Navigation Patterns

### Vim-Style Navigation

```python
class TaskListView(ListView):
    """Task list with vim-style navigation."""

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g", "first", "First", show=False),
        Binding("G", "last", "Last", show=False),
        Binding("ctrl+d", "page_down", "Page Down", show=False),
        Binding("ctrl+u", "page_up", "Page Up", show=False),
    ]

    def action_first(self) -> None:
        """Go to first item."""
        self.index = 0

    def action_last(self) -> None:
        """Go to last item."""
        if self._nodes:
            self.index = len(self._nodes) - 1

    def action_page_down(self) -> None:
        """Move down half a page."""
        self.index = min(self.index + 10, len(self._nodes) - 1)

    def action_page_up(self) -> None:
        """Move up half a page."""
        self.index = max(self.index - 10, 0)
```

### Modal Navigation

```python
class MyModal(ModalScreen):
    """Modal with navigation between inputs."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "submit", "Submit"),
        Binding("tab", "focus_next", "Next", show=False),
        Binding("shift+tab", "focus_previous", "Prev", show=False),
    ]

    def action_cancel(self) -> None:
        """Cancel and close modal."""
        self.dismiss(None)

    def action_submit(self) -> None:
        """Submit form data."""
        data = self.collect_form_data()
        self.dismiss(data)
```

## Testing Patterns

### Navigation Tests

```python
# tests/tui/test_navigation.py
import pytest
from textual.testing import AppTester
from todo.tui.app import TodoApp


@pytest.fixture
async def app_tester(task_service):
    """App tester fixture."""
    app = TodoApp(task_service=task_service)
    async with AppTester.run_test(app) as tester:
        yield tester


class TestAppNavigation:
    """Test application navigation."""

    async def test_help_screen_opens(self, app_tester):
        """? key opens help screen."""
        await app_tester.press("question_mark")

        assert isinstance(app_tester.app.screen, HelpScreen)

    async def test_help_screen_closes(self, app_tester):
        """Escape closes help screen."""
        await app_tester.press("question_mark")
        await app_tester.press("escape")

        assert isinstance(app_tester.app.screen, MainScreen)

    async def test_quit_exits_app(self, app_tester):
        """q key exits application."""
        await app_tester.press("q")

        assert app_tester.app.return_code == 0


class TestTaskListNavigation:
    """Test task list navigation."""

    async def test_vim_down_navigation(self, app_tester, sample_tasks):
        """j key moves down."""
        task_list = app_tester.app.query_one(TaskListView)
        initial = task_list.index

        await app_tester.press("j")

        assert task_list.index == initial + 1

    async def test_vim_up_navigation(self, app_tester, sample_tasks):
        """k key moves up."""
        task_list = app_tester.app.query_one(TaskListView)
        await app_tester.press("j")  # Move down first

        await app_tester.press("k")

        assert task_list.index == 0

    async def test_go_to_bottom(self, app_tester, sample_tasks):
        """G key goes to last task."""
        task_list = app_tester.app.query_one(TaskListView)

        await app_tester.press("G")

        assert task_list.index == len(sample_tasks) - 1
```

## Running Tests

```bash
# Run navigation tests
uv run pytest tests/tui/test_navigation.py -v

# Run with async output
uv run pytest tests/tui/test_navigation.py -v -s

# Run specific test class
uv run pytest tests/tui/test_navigation.py::TestAppNavigation -v
```

## Checklist

Before completing navigation implementation:
- [ ] App has global keyboard bindings
- [ ] Screens have context-specific bindings
- [ ] Help screen documents all shortcuts
- [ ] Focus is set correctly on screen mount
- [ ] Vim-style navigation works (j/k/g/G)
- [ ] Escape closes modals/screens
- [ ] Tab traverses form fields
- [ ] Screen stack works correctly
- [ ] Tests cover navigation flows
