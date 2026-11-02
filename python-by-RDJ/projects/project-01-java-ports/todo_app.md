# `todo_app.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A to-do manager where each task is an object (a dataclass) kept in a collection, ported from the project-02 spec. Tasks have a title, a `Priority` enum (`LOW`, `MEDIUM`, `HIGH`), an optional due date and a done flag. You can add, list with filters, mark done or not done, edit, delete, sort three ways, search by title, and get a summary. The core (`TaskManager`) has no `input()`; today's date is passed in, so "overdue" is testable.

## Full Line-by-Line Breakdown

### SECTION 1: Priority enum, errors, Task
- `Priority(Enum)` with values 1, 2, 3. `Priority.parse` accepts names in any case (`" high "`) or the numbers 1-3 and raises `ValueError` otherwise. `cls.__members__` is the dict of names to members.
- `TaskNotFoundError(LookupError)` is the "unknown id" error.
- `parse_due("")` or `"none"` returns `None`; `"2026-06-15"` becomes a `date` via `date.fromisoformat`; bad text (`2026-02-30`, `31/12/2026`) raises `ValueError` with a clear message.
- `Task` is a `@dataclass(eq=False)` with `__eq__` and `__hash__` written by hand to use only `id` (the Java requirement for `equals`/`hashCode`). Default dataclass equality compares every field, so a task would stop equalling itself after an edit, and a mutable dataclass with `eq=True` is unhashable. Hashing by `id` is safe because `id` never changes.
- `is_overdue(today)` is true only if the task is not done, has a due date, and the date is strictly before today (due today is not overdue).
- `UNSET` is a sentinel object. In `edit`, `due=None` means "clear the due date" while `due=UNSET` means "leave it alone"; plain `None` cannot carry both meanings.

### SECTION 2: TaskManager
- Storage is `dict[int, Task]` keyed by id. Justification: every operation the spec asks for by id (get, edit, delete, mark done) is O(1), and dicts keep insertion order so listing is still in creation order. A list would need a linear scan for each id lookup.
- IDs come from `_next_id`, a counter that only increases, so a deleted id is never reused (tested). `add` validates the title before consuming an id, so a rejected add does not burn one.
- `edit` validates the new title before changing anything, so a blank title leaves the task untouched (tested).
- `clear_done` iterates over a snapshot list `[tid for ... if t.done]` and then deletes. Deleting from a dict while looping over it raises `RuntimeError: dictionary changed size during iteration` (Python's `ConcurrentModificationException`); a test demonstrates that, and another shows `clear_done` avoids it.
- `sorted_tasks(by)` returns a new list and never reorders storage. Keys are tuples: priority is `(-priority.value, id)` so HIGH is first; due is `(due is None, due or date.min, id)` so undated tasks go last (this is the `Comparator.thenComparing` idea); title uses `casefold()`. Every key ends in `id`, so equal priorities have a deterministic order (the spec question: "same priority" ties are broken by creation order).
- `search` is a case-insensitive substring test on the title. `summary(today)` returns a frozen `Summary` with total, done, overdue and a count per priority.

### SECTION 3: formatting
`format_tasks` builds an aligned table with f-string width specs and appends `OVERDUE` to late rows. `format_summary` prints the counts.

### SECTION 4: interactive layer
`run(read, write, today)` handles the menu. All `ValueError` and `TaskNotFoundError` are caught in one place and printed as `Error: ...`, so no bad input crashes it. When editing, a blank answer means "keep", and `none` for the date means "clear".

Real output from a piped run with `today` being the real current date (menu banner lines removed for length; exit code 0). The script was: add "Pay rent" HIGH due 2020-01-01; add "Read book" due 2099-12-31; blank title; bad priority; a blank menu choice (shown as invalid option); mark done 1; mark done 9; delete 42; list open tasks; sort by title; search "BOOK"; summary.

```text
Choose an option: Title: Priority (LOW/MEDIUM/HIGH, blank = MEDIUM): Due date YYYY-MM-DD (blank = none): Added task 1: Pay rent

Choose an option: Title: Priority (LOW/MEDIUM/HIGH, blank = MEDIUM): Due date YYYY-MM-DD (blank = none): Added task 2: Read book

Choose an option: Title: Priority (LOW/MEDIUM/HIGH, blank = MEDIUM): Due date YYYY-MM-DD (blank = none): Error: Title cannot be blank.

Choose an option: Title: Priority (LOW/MEDIUM/HIGH, blank = MEDIUM): Error: Priority must be one of LOW, MEDIUM, HIGH (got 'urgent').

Choose an option: Invalid option.

Choose an option: Task id: Task 1 marked done.

Choose an option: Task id: Error: No task with id 9.

Choose an option: Task id: Error: No task with id 42.

Choose an option: Status filter (all/done/open): Priority filter (blank = all):  ID  Done  Title                    Priority  Due       
--------------------------------------------------------
  2  [ ]   Read book                MEDIUM    2099-12-31

Choose an option: Sort by (priority/due/title):  ID  Done  Title                    Priority  Due       
--------------------------------------------------------
  1  [x]   Pay rent                 HIGH      2020-01-01
  2  [ ]   Read book                MEDIUM    2099-12-31

Choose an option: Search text:  ID  Done  Title                    Priority  Due       
--------------------------------------------------------
  2  [ ]   Read book                MEDIUM    2099-12-31

Choose an option: Total: 2 | Done: 1 | Overdue: 0
By priority -> LOW: 0, MEDIUM: 1, HIGH: 1

Choose an option: Goodbye!
```
(My script was slightly misaligned with the prompts: a leftover blank line became the invalid option and the `3`/`9` entries became ids. The output above is exactly what ran. The tests in `test_todo_app.py` cover the full add / edit / delete / overdue flow with a fixed date.)

## Key Differences From Java

| Java | Python |
|---|---|
| `enum Priority { LOW, MEDIUM, HIGH }` | `class Priority(Enum)`, members have `.name` and `.value` |
| `equals` + `hashCode` overrides | `__eq__` + `__hash__` (or `@dataclass(frozen=True)`) |
| `toString()` | `__repr__` (the dataclass generates one) |
| `Comparator.comparing(...).thenComparing(...)` | `sorted(key=lambda t: (a, b, c))` with tuples |
| `ConcurrentModificationException` on remove-in-loop | `RuntimeError` for dicts; iterate a snapshot list |
| `Optional<LocalDate>` / `null` due date | `date \| None` |
| `Map<Integer, Task>` | plain `dict` (ordered since Python 3.7) |

## Key Rules / Gotchas Recap
- A default `@dataclass` compares all fields and (if mutable) is unhashable; define identity-based `__eq__`/`__hash__` for entities.
- Use a sentinel (`UNSET`) when `None` is a meaningful value.
- Never modify a dict or list while iterating it; build the list of keys first.
- `sorted()` is stable and returns a new list; `list.sort()` mutates in place.
- Tuple sort keys give multi-level ordering; `None` cannot be compared with a date, so put an `is None` flag first.
- Pass "today" into functions that depend on it, so tests do not depend on the calendar.

## Why This Structure Exists
Entities with stable ids, a manager that owns the collection, and pure sort/filter functions are the same shape as a REST resource layer (this is what project-07 will need) and as most automation tooling that tracks jobs or findings.
