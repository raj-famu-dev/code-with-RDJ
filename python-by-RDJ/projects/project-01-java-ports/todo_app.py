# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""To-do app: a Python port of project-02 (to-do manager with Task objects in a collection).

Core: Priority Enum, Task dataclass, TaskManager (dict keyed by id), pure
formatting. Interactive menu in run()/main(); the core never calls input().
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from enum import Enum


# ===== SECTION 1: Priority enum, errors, Task =====
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @classmethod
    def parse(cls, text: str) -> Priority:
        """'high', 'HIGH', ' High ' or '3' -> Priority.HIGH."""
        key = text.strip().upper()
        if key in cls.__members__:
            return cls[key]
        if key.isascii() and key.isdigit() and int(key) in {p.value for p in cls}:
            return cls(int(key))
        raise ValueError(f"Priority must be one of LOW, MEDIUM, HIGH (got {text.strip()!r}).")


class TaskNotFoundError(LookupError):
    """No task has that id."""


def parse_due(text: str) -> date | None:
    """'' or 'none' -> None; 'YYYY-MM-DD' -> date; anything else -> ValueError."""
    text = text.strip()
    if text == "" or text.lower() == "none":
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise ValueError(f"Due date must look like YYYY-MM-DD (got {text!r}).") from None


def _clean_title(title: str) -> str:
    title = title.strip()
    if not title:
        raise ValueError("Title cannot be blank.")
    return title


@dataclass(eq=False)  # eq=False: we define equality by id ourselves (see below)
class Task:
    id: int
    title: str
    priority: Priority = Priority.MEDIUM
    due: date | None = None
    done: bool = False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Task) and self.id == other.id

    def __hash__(self) -> int:  # id never changes, so hashing by it is safe on a mutable object
        return hash(self.id)

    def is_overdue(self, today: date) -> bool:
        return not self.done and self.due is not None and self.due < today


@dataclass(frozen=True)
class Summary:
    total: int
    done: int
    overdue: int
    by_priority: dict[Priority, int]


class _Unset:
    """Marker meaning 'argument not given' (None is a real value for due: 'no due date')."""

    def __repr__(self) -> str:
        return "UNSET"


UNSET = _Unset()


# ===== SECTION 2: TaskManager =====
class TaskManager:
    """Tasks live in a dict {id: Task}: lookup/edit/delete by id is O(1) and dicts keep
    insertion order, so listing is still in creation order. IDs come from a counter
    that only goes up, so a deleted id is never handed out again."""

    SORT_KEYS = ("priority", "due", "title")

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def __len__(self) -> int:
        return len(self._tasks)

    def add(self, title: str, priority: Priority = Priority.MEDIUM, due: date | None = None) -> Task:
        task = Task(self._next_id, _clean_title(title), priority, due)  # validate before consuming an id
        self._next_id += 1
        self._tasks[task.id] = task
        return task

    def get(self, task_id: int) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError:
            raise TaskNotFoundError(f"No task with id {task_id}.") from None

    def list_tasks(self, done: bool | None = None, priority: Priority | None = None) -> list[Task]:
        """Creation order, optionally filtered by status and/or priority."""
        return [t for t in self._tasks.values()
                if (done is None or t.done == done) and (priority is None or t.priority == priority)]

    def set_done(self, task_id: int, done: bool = True) -> Task:
        task = self.get(task_id)
        task.done = done
        return task

    def edit(self, task_id: int, *, title: str | _Unset = UNSET, priority: Priority | _Unset = UNSET,
             due: date | None | _Unset = UNSET) -> Task:
        task = self.get(task_id)
        new_title = _clean_title(title) if not isinstance(title, _Unset) else task.title  # validate first
        task.title = new_title
        if not isinstance(priority, _Unset):
            task.priority = priority
        if not isinstance(due, _Unset):
            task.due = due  # None clears the due date
        return task

    def delete(self, task_id: int) -> Task:
        self.get(task_id)
        return self._tasks.pop(task_id)

    def clear_done(self) -> int:
        """Delete every finished task. Iterates over a snapshot list: deleting from a dict
        while looping over it raises RuntimeError (Python's ConcurrentModificationException)."""
        finished = [tid for tid, t in self._tasks.items() if t.done]
        for tid in finished:
            del self._tasks[tid]
        return len(finished)

    def sorted_tasks(self, by: str) -> list[Task]:
        """A new sorted list. Ties always fall back to id, so order is deterministic."""
        tasks = list(self._tasks.values())
        if by == "priority":  # HIGH first
            return sorted(tasks, key=lambda t: (-t.priority.value, t.id))
        if by == "due":  # earliest first, tasks without a date last
            return sorted(tasks, key=lambda t: (t.due is None, t.due or date.min, t.id))
        if by == "title":
            return sorted(tasks, key=lambda t: (t.title.casefold(), t.id))
        raise ValueError(f"Sort by one of: {', '.join(self.SORT_KEYS)}.")

    def search(self, text: str) -> list[Task]:
        needle = text.strip().casefold()
        return [t for t in self._tasks.values() if needle in t.title.casefold()]

    def summary(self, today: date) -> Summary:
        tasks = list(self._tasks.values())
        return Summary(
            total=len(tasks),
            done=sum(t.done for t in tasks),
            overdue=sum(t.is_overdue(today) for t in tasks),
            by_priority={p: sum(t.priority is p for t in tasks) for p in Priority},
        )


# ===== SECTION 3: formatting =====
def format_tasks(tasks: list[Task], today: date | None = None) -> str:
    if not tasks:
        return "No tasks to show."
    lines = [f"{'ID':>3}  {'Done':<4}  {'Title':<24} {'Priority':<8}  {'Due':<10}", "-" * 56]
    for t in tasks:
        due = t.due.isoformat() if t.due else "-"
        flag = "  OVERDUE" if today and t.is_overdue(today) else ""
        lines.append(f"{t.id:>3}  {'[x]' if t.done else '[ ]':<4}  {t.title:<24} "
                     f"{t.priority.name:<8}  {due:<10}{flag}")
    return "\n".join(lines)


def format_summary(s: Summary) -> str:
    per = ", ".join(f"{p.name}: {n}" for p, n in s.by_priority.items())
    return f"Total: {s.total} | Done: {s.done} | Overdue: {s.overdue}\nBy priority -> {per}"


# ===== SECTION 4: interactive layer =====
Reader = Callable[[str], str]
Writer = Callable[[str], None]

MENU = """\
===== TO-DO MANAGER =====
1. Add task          2. List tasks (filter)   3. Mark done
4. Mark not done     5. Edit task             6. Delete task
7. Sort              8. Search                9. Summary
0. Exit"""


def _read_id(read: Reader) -> int:
    text = read("Task id: ").strip()
    if not (text.isascii() and text.isdigit()):
        raise ValueError("Task id must be a whole number.")
    return int(text)


def run(read: Reader = input, write: Writer = print, today: date | None = None,
        manager: TaskManager | None = None) -> TaskManager:
    mgr = manager if manager is not None else TaskManager()
    today = today or date.today()
    while True:
        write(MENU)
        choice = read("Choose an option: ").strip()
        try:
            if choice == "0":
                write("Goodbye!")
                return mgr
            elif choice == "1":
                title = read("Title: ")
                prio_text = read("Priority (LOW/MEDIUM/HIGH, blank = MEDIUM): ")
                priority = Priority.parse(prio_text) if prio_text.strip() else Priority.MEDIUM
                due = parse_due(read("Due date YYYY-MM-DD (blank = none): "))
                task = mgr.add(title, priority, due)
                write(f"Added task {task.id}: {task.title}")
            elif choice == "2":
                status = read("Status filter (all/done/open): ").strip().lower() or "all"
                if status not in ("all", "done", "open"):
                    raise ValueError("Status must be all, done or open.")
                prio_text = read("Priority filter (blank = all): ")
                prio = Priority.parse(prio_text) if prio_text.strip() else None
                done = {"all": None, "done": True, "open": False}[status]
                write(format_tasks(mgr.list_tasks(done, prio), today))
            elif choice in ("3", "4"):
                task = mgr.set_done(_read_id(read), choice == "3")
                write(f"Task {task.id} marked {'done' if task.done else 'not done'}.")
            elif choice == "5":
                task = mgr.get(_read_id(read))
                title = read(f"New title (blank = keep '{task.title}'): ")
                prio_text = read("New priority (blank = keep): ")
                due_text = read("New due date (blank = keep, 'none' = clear): ")
                mgr.edit(
                    task.id,
                    title=title if title.strip() else UNSET,
                    priority=Priority.parse(prio_text) if prio_text.strip() else UNSET,
                    due=parse_due(due_text) if due_text.strip() else UNSET,
                )
                write(f"Task {task.id} updated.")
            elif choice == "6":
                task = mgr.delete(_read_id(read))
                write(f"Deleted task {task.id}: {task.title}")
            elif choice == "7":
                write(format_tasks(mgr.sorted_tasks(read("Sort by (priority/due/title): ").strip().lower()), today))
            elif choice == "8":
                write(format_tasks(mgr.search(read("Search text: ")), today))
            elif choice == "9":
                write(format_summary(mgr.summary(today)))
            else:
                write("Invalid option.")
        except (ValueError, TaskNotFoundError) as err:
            write(f"Error: {err}")
        write("")


def main() -> None:
    try:
        run()
    except EOFError:
        print("\nInput ended. Goodbye!")


if __name__ == "__main__":
    main()
