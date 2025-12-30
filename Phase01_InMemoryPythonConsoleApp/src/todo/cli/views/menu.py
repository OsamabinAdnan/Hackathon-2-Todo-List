"""Interactive menu system for the Todo CLI application."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.table import Table
from datetime import date

from todo.models.task import Task, Priority
from todo.services.task_service import TaskService, get_task_service

console = Console()


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
    """Parse shorthand or case-insensitive priority input. Returns None for 'ALL'."""
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
    return None


def handle_add_task(service: TaskService) -> None:
    """Handle the Add Task menu option."""
    console.print("\n[bold italic green]Add New Task[/bold italic green]")
    title = Prompt.ask("[bold]Enter task title (1-100 chars)[/bold]").strip()
    if not title:
        console.print("[red]Title cannot be empty.[/red]")
        return

    description = Prompt.ask("[bold]Enter description (optional)[/bold]").strip()

    # Priority with shorthand support
    priority_input = Prompt.ask(
        "[bold]Select priority (n)one | (l)ow  | (m)edium | (h)igh[/bold]"
    )
    priority = parse_priority_input(priority_input)

    tags_str = Prompt.ask("[bold]Enter tags (comma-separated)[/bold]").strip()

    # Due date with validation
    due_date = None
    while True:
        due_str = Prompt.ask("[bold]Enter due date (YYYY-MM-DD, optional)[/bold]").strip()
        if not due_str:
            break
        try:
            parsed_date = date.fromisoformat(due_str)
            if parsed_date < date.today():
                console.print("[red]Error: Due date cannot be in the past.[/red]")
                continue
            due_date = parsed_date
            break
        except ValueError:
            console.print("[red]Error: Invalid date format. Use YYYY-MM-DD.[/red]")

    try:
        tags = {tag.strip() for tag in tags_str.split(",")} if tags_str else set()

        task = service.add_task(
            title=title,
            description=description,
            priority=priority,
            tags=tags,
            due_date=due_date
        )
        console.print(f"[green]Task added! Project: {task.id}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def handle_list_tasks(service: TaskService) -> None:
    """Handle listing all tasks without prompts (Default Level 1 style)."""
    tasks = service.get_all_tasks()
    from todo.cli.views.formatters import format_task_list
    format_task_list(tasks, console, title="All Tasks")


def parse_status_input(status_str: str) -> bool | None:
    """Parse status filter input with shorthand support."""
    val = status_str.strip().lower()
    if val in ("d", "done", "complete", "completed"):
        return True
    if val in ("t", "todo", "incomplete", "pending"):
        return False
    return None  # "all" or empty


def handle_filter_tasks(service: TaskService) -> None:
    """Handle filtering tasks by metadata."""
    console.print("\n[bold]Filtering Options[/bold]")

    # Status filter with shorthand
    status_input = Prompt.ask(
        "[bold]Filter by status (a)ll | (t)odo | (d)one (Press Enter for all)[/bold]"
    ).strip()
    is_completed = parse_status_input(status_input) if status_input else None

    # Priority filter with shorthand - ensuring ALL returns None
    priority_input = Prompt.ask(
        "[bold]Filter by priority (a)ll | (n)one | (l)ow | (m)edium | (h)igh (Press Enter for all)[/bold]"
    ).strip()
    p_enum = parse_priority_input(priority_input) if priority_input else None

    # Tags filter
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
    """Parse sort input with shorthand support."""
    val = sort_str.strip().lower()
    if val in ("cd", "created", "date", "created_date"):
        return "date"
    if val in ("p", "priority", "pri"):
        return "priority"
    if val in ("t", "title", "name"):
        return "title"
    if val in ("dd", "due", "due_date", "deadline"):
        return "due_date"
    return "date"


def handle_sort_tasks(service: TaskService) -> None:
    """Handle sorting the task list."""
    console.print("\n[bold]Sorting Options[/bold]")
    sort_input = Prompt.ask(
        "[bold]Sort by created-date(cd) | priority(p) | title(t) | due-date(dd)[/bold]"
    )
    sort_by = parse_sort_input(sort_input)

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
        new_pri_input = Prompt.ask(
            "[bold]New priority (n)one|(l)ow|(m)edium|(h)igh[/bold]",
            default=task.priority.name
        )
        new_priority = parse_priority_input(new_pri_input)

        service.update_task(
            task_id,
            title=new_title,
            description=new_desc,
            priority=new_priority
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
    """Handle toggle."""
    try:
        task_id = int(Prompt.ask("[bold]Enter task ID to toggle[/bold]").strip())
        task = service.toggle_task_completion(task_id)
        status = "complete" if task.completed else "incomplete"
        console.print(f"[green]Task {task_id} is now {status}.[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def show_help() -> None:
    """Display comprehensive help information."""
    help_text = Text()
    help_text.append("Todo CLI Application - Help Guide\n\n", style="bold yellow")

    help_text.append("Available Commands:\n\n", style="bold white")

    help_text.append("Interactive Menu:\n", style="bold green")
    help_text.append("  uv run main.py         - Launch interactive menu (default)\n\n", style="dim")

    help_text.append("Direct CLI Commands:\n", style="bold green")
    help_text.append("  uv run main.py add <title> --priority <p> --tags <tags> --due <date>\n", style="dim")
    help_text.append("    Example: uv run main.py add \"Buy milk\" --priority high --tags \"grocery\"\n\n", style="dim")

    help_text.append("  uv run main.py list [--status todo|done] [--priority h|m|l] [--sort priority|date|title]\n", style="dim")
    help_text.append("    Example: uv run main.py list --status todo --sort priority\n\n", style="dim")

    help_text.append("  uv run main.py search <keyword> [--priority <p>]\n", style="dim")
    help_text.append("    Example: uv run main.py search \"milk\"\n\n", style="dim")

    help_text.append("  uv run main.py update <id> --title <t> --priority <p>\n", style="dim")
    help_text.append("  uv run main.py delete <id>\n", style="dim")
    help_text.append("  uv run main.py toggle <id>\n\n", style="dim")

    help_text.append("Priority Shortcuts:\n", style="bold green")
    help_text.append("  n = NONE, l = LOW, m = MEDIUM, h = HIGH\n\n", style="dim")

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

        console.print("\n[dim]Press Enter to return to menu...[/dim]")
        input()
