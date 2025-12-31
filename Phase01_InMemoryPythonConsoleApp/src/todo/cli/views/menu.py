"""Interactive menu system for the Todo CLI application."""

import sys
import msvcrt  # Windows-specific for key reading
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.table import Table
from datetime import date, datetime, time

from todo.models.task import Task, Priority, Recurrence
from todo.services.task_service import TaskService, get_task_service, check_reminders
from todo.cli.views.formatters import display_reminders

console = Console()


def parse_datetime_input(value: str) -> datetime | None:
    """Parse datetime from various formats.

    Formats accepted:
    - "YYYY-MM-DD HH:MM" (e.g., "2025-01-15 14:30")
    - "YYYY-MM-DD" (e.g., "2025-01-15") - defaults to 00:00
    - "YYYY-MM-DDTHH:MM" (ISO format)

    Returns:
        datetime if valid, None if empty/invalid
    """
    if not value or not value.strip():
        return None

    value = value.strip()

    # Try full datetime format "YYYY-MM-DD HH:MM"
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        pass

    # Try ISO format with T separator "YYYY-MM-DDTHH:MM"
    try:
        return datetime.strptime(value.replace("T", " "), "%Y-%m-%d %H:%M")
    except ValueError:
        pass

    # Try date-only format "YYYY-MM-DD"
    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d")
        return parsed_date
    except ValueError:
        pass

    return None


def validate_future_datetime(dt: datetime) -> bool:
    """Validate that datetime is in the future (with small tolerance).

    Returns:
        True if datetime is in the future, False otherwise
    """
    # Allow 1 second tolerance for timing variations
    return dt > datetime.now()


def parse_recurrence_input(value: str) -> Recurrence:
    """Parse recurrence from string with shorthand support. Raises ValueError for invalid input.

    Shortcuts: n=none, d=daily, w=weekly, m=monthly
    """
    value = value.strip().lower()
    shortcuts = {"n": "NONE", "d": "DAILY", "w": "WEEKLY", "m": "MONTHLY"}
    if value in shortcuts:
        value = shortcuts[value]
    result = Recurrence.from_str(value)
    if result == Recurrence.NONE and value not in ("", "none"):
        # Only NONE is valid if the input wasn't empty or "none"
        # But from_str returns NONE for invalid inputs too, so check if input was valid
        valid_inputs = {"none", "daily", "weekly", "monthly", "n", "d", "w", "m"}
        if value.lower() not in valid_inputs:
            raise ValueError(f"Invalid recurrence: '{value}'. Use n, d, w, m or none, daily, weekly, monthly.")
    return result


def display_menu() -> None:
    """Display the main menu options."""
    menu_text = Text()
    menu_text.append("Todo - Manage your tasks\n\n", style="bold yellow")
    menu_text.append("1. ", style="bold")
    menu_text.append("Add Task - Create with priority & tags\n")
    menu_text.append("2. ", style="bold")
    menu_text.append("List Tasks - Show all tasks (no filters)\n")
    menu_text.append("3. ", style="bold")
    menu_text.append("Filter Tasks - Filter by status, priority, or tags\n")
    menu_text.append("4. ", style="bold")
    menu_text.append("Sort Tasks - Reorder by date, priority, or title\n")
    menu_text.append("5. ", style="bold")
    menu_text.append("Search Tasks - Find by keyword in title/description\n")
    menu_text.append("6. ", style="bold")
    menu_text.append("Update Task - Edit details & attributes\n")
    menu_text.append("7. ", style="bold")
    menu_text.append("Delete Task - Remove task permanently\n")
    menu_text.append("8. ", style="bold")
    menu_text.append("Toggle Status - Mark complete/incomplete\n")
    menu_text.append("9. ", style="bold")
    menu_text.append("Quit - Exit application\n")
    menu_text.append("0. ", style="bold")
    menu_text.append("Help - View all available commands\n")

    panel = Panel(
        menu_text,
        title="[bold]Todo Application[/bold]",
        border_style="blue",
    )
    console.print(panel)


def get_menu_choice(max_option: int = 9) -> int:
    """Get and validate menu choice."""
    while True:
        try:
            choice = Prompt.ask(f"[bold cyan]Enter option (0-{max_option})[/bold cyan]")
            choice_int = int(choice)
            if 0 <= choice_int <= max_option:
                return choice_int
            console.print(f"[red]Invalid option. Please enter 0-{max_option}.[/red]")
        except ValueError:
            console.print(f"[red]Please enter a valid number (0-{max_option}).[/red]")


def parse_priority_input(priority_str: str) -> Priority | None:
    """Parse shorthand or case-insensitive priority input. Returns None for 'ALL', raises ValueError for invalid."""
    val = priority_str.strip().lower()
    if val in ("a", "all", ""):
        return None
    if val in ("h", "high"):
        return Priority.HIGH
    if val in ("m", "medium", "med"):
        return Priority.MEDIUM
    if val in ("l", "low"):
        return Priority.LOW
    if val in ("n", "none"):
        return Priority.NONE
    raise ValueError(f"Invalid priority: '{priority_str}'. Use a, l, m, h, n or all, low, medium, high, none.")


def handle_add_task(service: TaskService) -> None:
    """Handle the Add Task menu option."""
    console.print("\n[bold italic green]Add New Task[/bold italic green]")
    title = Prompt.ask("[bold]Enter task title (1-100 chars)[/bold]").strip()
    if not title:
        console.print("[red]Title cannot be empty.[/red]")
        return

    description = Prompt.ask("[bold]Enter description (optional)[/bold]").strip()

    # Priority with validation
    while True:
        priority_input = Prompt.ask(
            "[bold]Select priority (n)one | (l)ow | (m)edium | (h)igh[/bold]"
        ).strip()
        try:
            priority = parse_priority_input(priority_input) if priority_input else Priority.NONE
            break
        except ValueError as e:
            console.print(f"[red]{e}[/red]")

    tags_str = Prompt.ask("[bold]Enter tags (comma-separated)[/bold]").strip()

    # Due date/time with validation
    due_date = None
    while True:
        due_str = Prompt.ask(
            "[bold]Enter due date/time (YYYY-MM-DD or YYYY-MM-DD HH:MM, optional)[/bold]"
        ).strip()
        if not due_str:
            break
        parsed = parse_datetime_input(due_str)
        if parsed is None:
            console.print("[red]Error: Invalid format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM[/red]")
            continue
        if parsed < datetime.now():
            console.print("[red]Error: Due date cannot be in the past.[/red]")
            continue
        due_date = parsed.date() if parsed.time() == time(0, 0, 0) else parsed
        break

    # Recurrence pattern with validation
    while True:
        recurrence_input = Prompt.ask(
            "[bold]Recurring task? (n)one | (d)aily | (w)eekly | (m)onthly[/bold]"
        ).strip()
        try:
            recurrence = parse_recurrence_input(recurrence_input) if recurrence_input else Recurrence.NONE
            break
        except ValueError as e:
            console.print(f"[red]{e}[/red]")

    # Validate: recurring tasks must have due date
    if recurrence != Recurrence.NONE and due_date is None:
        console.print("[red]Error: Recurring tasks must have a due date. Please set a due date first.[/red]")
        return

    try:
        tags = {tag.strip() for tag in tags_str.split(",")} if tags_str else set()

        task = service.add_task_with_recurrence(
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date,
            recurrence=recurrence
        )

        # Show recurrence info
        if recurrence != Recurrence.NONE:
            console.print(f"[green]Task added! ID: {task.id} - {task.title}[/green]")
            console.print(f"[cyan]Recurrence: {recurrence.name} - Task will auto-reschedule when completed[/cyan]")
        else:
            console.print(f"[green]Task added! ID: {task.id} - {task.title}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_list_tasks(service: TaskService) -> None:
    """Handle listing all tasks without prompts (Default Level 1 style)."""
    tasks = service.get_all_tasks()
    from todo.cli.views.formatters import format_task_list
    format_task_list(tasks, console, title="All Tasks")


def parse_status_input(status_str: str) -> bool | None:
    """Parse status filter input with shorthand support. Raises ValueError for invalid input."""
    val = status_str.strip().lower()
    if val in ("d", "done", "complete", "completed"):
        return True
    if val in ("t", "todo", "incomplete", "pending"):
        return False
    if val in ("a", "all", ""):
        return None  # "all" or empty
    raise ValueError(f"Invalid status: '{status_str}'. Use a, t, d or all, todo, done.")


def handle_filter_tasks(service: TaskService) -> None:
    """Handle filtering tasks by metadata with input validation."""
    console.print("\n[bold]Filtering Options[/bold]")

    # Status filter with validation
    while True:
        status_input = Prompt.ask(
            "[bold]Filter by status (a)ll | (t)odo | (d)one (Press Enter for all)[/bold]"
        ).strip()
        try:
            is_completed = parse_status_input(status_input) if status_input else None
            break
        except ValueError as e:
            console.print(f"[red]{e}[/red]")

    # Priority filter with validation
    while True:
        priority_input = Prompt.ask(
            "[bold]Filter by priority (a)ll | (n)one | (l)ow | (m)edium | (h)igh (Press Enter for all)[/bold]"
        ).strip()
        try:
            p_enum = parse_priority_input(priority_input) if priority_input else None
            break
        except ValueError as e:
            console.print(f"[red]{e}[/red]")

    # Tags filter (no validation needed - just skip if empty)
    tags_input = Prompt.ask(
        "[bold]Filter by tags (comma-separated, Press Enter to skip)[/bold]"
    ).strip()
    tag_set = {tag.strip().lower() for tag in tags_input.split(",") if tag.strip()} if tags_input else None

    # Apply smart sorting: if priority filter is set, sort by due_date; otherwise by priority
    default_sort = "due_date" if p_enum else "priority"
    result = service.search_tasks(status=is_completed, priority=p_enum, tags=tag_set, sort_by=default_sort)
    from todo.cli.views.formatters import format_task_list
    format_task_list(result.tasks, console, title="Filtered Tasks")


def parse_sort_input(sort_str: str) -> str:
    """Parse sort input with shorthand support. Raises ValueError for invalid input."""
    val = sort_str.strip().lower()
    if val in ("cd", "created", "date", "created_date"):
        return "date"
    if val in ("p", "priority", "pri"):
        return "priority"
    if val in ("t", "title", "name"):
        return "title"
    if val in ("dd", "due", "due_date", "deadline"):
        return "due_date"
    if val == "":
        return "date"  # Default for empty input
    raise ValueError(f"Invalid sort option: '{sort_str}'. Use cd, p, t, dd or created, priority, title, due_date.")


def handle_sort_tasks(service: TaskService) -> None:
    """Handle sorting the task list with input validation."""
    console.print("\n[bold]Sorting Options[/bold]")

    while True:
        sort_input = Prompt.ask(
            "[bold]Sort by created-date(cd) | priority(p) | title(t) | due-date(dd)[/bold]"
        ).strip()
        try:
            sort_by = parse_sort_input(sort_input)
            break
        except ValueError as e:
            console.print(f"[red]{e}[/red]")

    result = service.search_tasks(sort_by=sort_by)
    from todo.cli.views.formatters import format_task_list
    format_task_list(result.tasks, console, title=f"Tasks sorted by {sort_by}")


def handle_search_tasks(service: TaskService) -> None:
    """Handle keyword search."""
    keyword = Prompt.ask("[bold]Enter search keyword[/bold]").strip()
    if not keyword:
        return

    result = service.search_tasks(keyword=keyword)
    from todo.cli.views.formatters import format_task_list
    format_task_list(result.tasks, console, title=f"Results for '{keyword}'")


def handle_update_task(service: TaskService) -> None:
    """Handle updates."""
    try:
        task_id = int(Prompt.ask("[bold]Enter task ID to update[/bold]").strip())
        task = service.get_task(task_id)

        console.print(f"[yellow]Updating: {task.title}[/yellow]")
        new_title = Prompt.ask("[bold]New title[/bold]", default=task.title)
        new_desc = Prompt.ask("[bold]New description[/bold]", default=task.description)

        # Priority with validation
        while True:
            new_pri_input = Prompt.ask(
                "[bold]New priority (n)one|(l)ow|(m)edium|(h)igh (press Enter to keep)[/bold]",
                default=task.priority.name
            ).strip()
            if not new_pri_input:
                new_priority = task.priority
                break
            try:
                new_priority = parse_priority_input(new_pri_input)
                break
            except ValueError as e:
                console.print(f"[red]{e}[/red]")

        # Update due date/time
        due_date = None
        due_str = Prompt.ask(
            "[bold]New due date/time (YYYY-MM-DD or YYYY-MM-DD HH:MM, press Enter to keep)[/bold]",
            default=""
        ).strip()
        if due_str:
            parsed = parse_datetime_input(due_str)
            if parsed is None:
                console.print("[red]Error: Invalid format. Keeping existing due date.[/red]")
            elif parsed < datetime.now():
                console.print("[red]Error: Due date cannot be in the past. Keeping existing due date.[/red]")
            else:
                due_date = parsed.date() if parsed.time() == time(0, 0, 0) else parsed

        # Update recurrence with validation
        while True:
            recur_str = Prompt.ask(
                "[bold]Recurring? (n)one|(d)aily|(w)eekly|(m)onthly (press Enter to keep)[/bold]",
                default=task.recurrence.name
            ).strip()
            if not recur_str:
                new_recurrence = task.recurrence
                break
            try:
                new_recurrence = parse_recurrence_input(recur_str)
                break
            except ValueError as e:
                console.print(f"[red]{e}[/red]")

        # Validate: if setting recurrence, need due date
        if new_recurrence != Recurrence.NONE and due_date is None and task.due_date is None:
            console.print("[red]Error: Recurring tasks must have a due date. Keeping existing settings.[/red]")
            return

        service.update_task_with_recurrence(
            task_id,
            title=new_title,
            description=new_desc,
            priority=new_priority,
            due_date=due_date,
            recurrence=new_recurrence
        )
        console.print(f"[green]Task {task_id} updated![/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_delete_task(service: TaskService) -> None:
    """Handle deletion."""
    try:
        task_id = int(Prompt.ask("[bold red]Enter task ID to DELETE[/bold red]").strip())
        service.delete_task(task_id)
        console.print(f"[green]Task {task_id} deleted.[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_toggle_task(service: TaskService) -> None:
    """Handle toggle with recurring task support."""
    try:
        task_id = int(Prompt.ask("[bold]Enter task ID to toggle[/bold]").strip())

        # Get the task to check if it's being completed and is recurring
        task = service.get_task(task_id)
        is_completing = not task.completed  # Will be marked complete
        is_recurring = task.recurrence.value > 0 and task.due_date is not None

        if is_completing and is_recurring:
            # Use complete_task for recurring tasks to auto-reschedule
            from todo.services.task_service import complete_task
            completed, new_task = complete_task(task_id)
            console.print(f"[green]Task {task_id} marked complete.[/green]")
            if new_task:
                console.print(f"[cyan]New recurring instance created: {new_task.id} - {new_task.title}[/cyan]")
        else:
            # Use regular toggle for non-recurring or marking incomplete
            task = service.toggle_task_completion(task_id)
            status = "complete" if task.completed else "incomplete"
            console.print(f"[green]Task {task_id} is now {status}.[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def wait_for_enter() -> None:
    """Wait for user to press Enter key only, ignoring all other input without echo."""
    if sys.platform == "win32":
        # Windows: Use msvcrt to read keys without echo
        while True:
            key = msvcrt.getch()
            # Check if Enter key (0x0D is carriage return, 0x0A is line feed)
            if key in (b'\r', b'\n'):
                break
            # Ignore all other keys silently (no echo)
    else:
        # Unix/Linux/Mac: Use termios to disable echo
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                key = sys.stdin.read(1)
                if key in ('\r', '\n'):
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def show_help() -> None:
    """Display comprehensive help information."""
    help_text = Text()
    help_text.append("Todo CLI Application - Help Guide\n\n", style="bold yellow")

    help_text.append("Available Commands:\n\n", style="bold white")

    help_text.append("Interactive Menu:\n", style="bold green")
    help_text.append("  uv run main.py         - Launch interactive menu (default)\n\n", style="dim")

    help_text.append("Direct CLI Commands:\n", style="bold green")
    help_text.append("  uv run main.py add <title> --priority <p> --tags <tags> --due <datetime> --recurring <pattern>\n", style="dim")
    help_text.append("    Example: uv run main.py add \"Buy milk\" --priority high --tags \"grocery\"\n", style="dim")
    help_text.append("    Example: uv run main.py add \"Team Meeting\" --due \"2025-01-15 14:30\" --recurring weekly\n\n", style="dim")

    help_text.append("  uv run main.py list [--status todo|done] [--priority h|m|l] [--sort priority|date|title|due_date]\n", style="dim")
    help_text.append("    Example: uv run main.py list --status todo --sort priority\n\n", style="dim")

    help_text.append("  uv run main.py search <keyword> [--priority <p>]\n", style="dim")
    help_text.append("    Example: uv run main.py search \"milk\"\n\n", style="dim")

    help_text.append("  uv run main.py update <id> --title <t> --priority <p> --due <datetime> --recurring <pattern>\n", style="dim")
    help_text.append("  uv run main.py delete <id>\n", style="dim")
    help_text.append("  uv run main.py toggle <id>    - Completes recurring tasks and auto-reschedules\n\n", style="dim")

    help_text.append("Level 3 Features:\n", style="bold cyan")
    help_text.append("  🔁 Recurring Tasks: Create tasks that automatically reschedule when completed\n", style="dim")
    help_text.append("     Patterns: NONE (n), DAILY (d), WEEKLY (w), MONTHLY (m)\n", style="dim")
    help_text.append("     Note: Recurring tasks require a due date\n\n", style="dim")

    help_text.append("  📅 DateTime Precision: Set specific due dates and times\n", style="dim")
    help_text.append("     Formats: \"YYYY-MM-DD HH:MM\" (e.g., \"2025-01-15 14:30\")\n", style="dim")
    help_text.append("              \"YYYY-MM-DD\" (defaults to 00:00)\n", style="dim")
    help_text.append("     Past datetimes are rejected\n\n", style="dim")

    help_text.append("  ⏰ Smart Reminders: Automatic notifications for time-sensitive tasks\n", style="dim")
    help_text.append("     Overdue: Tasks past their due datetime (red styling ⚠️)\n", style="dim")
    help_text.append("     Due Soon: Tasks due within 60 minutes (yellow styling)\n", style="dim")
    help_text.append("     Note: Date-only tasks (00:00 time) excluded from reminders\n\n", style="dim")

    help_text.append("Priority Shortcuts:\n", style="bold green")
    help_text.append("  n = NONE, l = LOW, m = MEDIUM, h = HIGH\n\n", style="dim")

    help_text.append("Recurrence Shortcuts:\n", style="bold green")
    help_text.append("  n = NONE, d = DAILY, w = WEEKLY, m = MONTHLY\n\n", style="dim")

    help_text.append("Sort Shortcuts:\n", style="bold green")
    help_text.append("  cd = Created Date, p = Priority, t = Title, dd = Due Date\n\n", style="dim")

    help_text.append("Status Shortcuts:\n", style="bold green")
    help_text.append("  a = ALL, t = TODO, d = DONE\n\n", style="dim")

    panel = Panel(help_text, title="[bold]Help & Documentation[/bold]", border_style="cyan")
    console.print(panel)


def run_menu() -> None:
    """Main menu loop."""
    service = get_task_service()

    while True:
        display_menu()
        choice = get_menu_choice(max_option=9)

        if choice == 0:
            show_help()
        elif choice == 1:
            handle_add_task(service)
        elif choice == 2:
            handle_list_tasks(service)
        elif choice == 3:
            handle_filter_tasks(service)
        elif choice == 4:
            handle_sort_tasks(service)
        elif choice == 5:
            handle_search_tasks(service)
        elif choice == 6:
            handle_update_task(service)
        elif choice == 7:
            handle_delete_task(service)
        elif choice == 8:
            handle_toggle_task(service)
        elif choice == 9:
            console.print("\n[bold cyan]Goodbye![/bold cyan]")
            break

        # Show reminders after action
        reminder_result = check_reminders()
        display_reminders(reminder_result)

        console.print("\n[dim]Press Enter to return to menu...[/dim]")
        wait_for_enter()
