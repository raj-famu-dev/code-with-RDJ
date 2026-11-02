# `grade_manager.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A menu-driven console app that stores students with three subject scores (Math, Physics, Biology), shows a table, searches by name ignoring case, and prints class statistics. It is a port of `StudentGradeManager.java` (project-04). The important change is structural: the logic (a `Student` dataclass, a `GradeBook`, pure formatting functions) never calls `input()`, so pytest can test it directly, and only a thin `run()`/`main()` layer talks to the keyboard.

**Known Java defect, fixed here:** the Java table header and the search output print `Science` and `English`, but the program actually asks for and stores Math, Physics and Biology. The Python port uses `SUBJECTS = ("Math", "Physics", "Biology")` as the single source for prompts, table header and search output, so they cannot drift apart (a test asserts `Science`/`English` never appear). The Java method typo `viewAllStrudents` is not carried over either.

## Full Line-by-Line Breakdown

### SECTION 1: data model
- `SUBJECTS` and `MAX_STUDENTS = 50` are module-level constants (Java: `static final`). Parallel arrays (`names[]`, `scores[][]`, `studentCount`) are replaced by `list[Student]`; the list's own length is the count, so there is no counter to forget to update.
- `assign_grade(average)` is the same if/else chain: 90 A, 80 B, 70 C, 60 D, else F.
- `@dataclass(frozen=True) class Student` holds `name` and a `scores` tuple. `frozen=True` makes it immutable, like a Java `record`. `__post_init__` runs right after the generated constructor and validates: trimmed name must not be blank, there must be 3 scores, each an `int` from 0 to 100 (`bool` is rejected because `True` is technically an `int` in Python). A student with bad data can never exist. Because the class is frozen, the trimmed name is stored with `object.__setattr__`, the standard escape hatch inside `__post_init__`.
- `average` is a property: `sum(scores) / len(scores)`. In Python `/` is always true division, so Java's `(double)sum / length` cast is not needed. `grade` is another property built on it.
- `ClassStats` bundles the results of the statistics (count, class average, top, bottom).
- `GradeBook.add` checks capacity first (raises `GradeBookFullError`), then builds the `Student` (which validates), and only then appends. A failed add stores nothing (tested).
- `GradeBook.find` compares `casefold()`ed names (Python's `equalsIgnoreCase`, slightly more thorough for non-English letters) and returns the first match, or `None`.
- `GradeBook.statistics` uses strict `>` and `<` like the Java loop, so on a tie the earliest student is reported. It returns `None` for an empty book.

### SECTION 2: validation of raw text
- `parse_score(text)` returns an int or raises `ValueError` carrying the exact user-facing message: `That's not a number.` or `Score must be between 0 and 100.` A regex `[+-]?\d+` (ASCII only) decides "is it an integer". Why not just `int(text)`? Because Python's `int("1_0")` is `10` and `int("٣")` accepts non-ASCII digits, while Java's `nextInt` would not; and `"85.5"` must be "not a number" as in Java.
- `parse_menu_choice` returns the number or `-1` ("invalid"), the same signal the Java code used.

### SECTION 3: formatting
`format_table`, `format_student` and `format_statistics` return strings instead of printing. f-string specs replace `printf`: `{name:<15}` left-aligns in 15 columns, `{score:>8d}` right-aligns an int in 8, `{avg:>10.2f}` is `%10.2f`. Because they return text, tests can check them.

### SECTION 4: interactive layer
- `read` and `write` are parameters (defaulting to `input` and `print`). Tests pass a fake `read` from a list and collect output.
- `read_valid_score` loops until `parse_score` succeeds, printing the error message each time (Java's `while(true)` + `hasNextInt` dance, without any scanner buffer problems).
- `add_student`, `search_student` and the `run` loop follow the Java menu exactly: the menu prints, a choice is read, `if/elif` routes (Python's `match` would also work), option 5 prints `Goodbye!` and returns.
- `main()` catches `EOFError`, which is what `input()` raises when piped input runs out, so the program exits cleanly instead of printing a traceback.

Real output from `printf '1\nAda\n90\n80\n70\n1\nLin\nabc\n150\n60\n70\n80\n1\n   \n2\n3\nada\n3\nzed\n4\nfoo\n5\n' | python3 grade_manager.py` (the repeated menu banner lines are removed here for length; piped input is not echoed, so you only see prompts):

```text
Choose an option (1-5): Enter student name: Enter Math score (0-100): Enter Physics score (0-100): Enter Biology score (0-100): Student 'Ada' added successfully.

Choose an option (1-5): Enter student name: Enter Math score (0-100): That's not a number.
Enter Math score (0-100): Score must be between 0 and 100.
Enter Math score (0-100): Enter Physics score (0-100): Enter Biology score (0-100): Student 'Lin' added successfully.

Choose an option (1-5): Enter student name: name cannot be empty. Student not added.

Choose an option (1-5): Name                Math  Physics  Biology    Average
-------------------------------------------------------
Ada                   90       80       70      80.00
Lin                   60       70       80      70.00

Choose an option (1-5): Enter name to search: --- Student Found ---
Name: Ada
Math: 90 | Physics: 80 | Biology: 70
Average: 80.00 | Grade: B

Choose an option (1-5): Enter name to search: No student found with that name.

Choose an option (1-5): --- Class Statistics ---
Total students: 2
Class average: 75.00 (Grade: C)
Top performer: Ada (80.00)
Needs support: Lin (70.00)

Choose an option (1-5): Invalid Option. Try again!

Choose an option (1-5): Goodbye!
```
Exit code was 0. Note the header now says Physics and Biology.

## Key Differences From Java

| Java | Python |
|---|---|
| Parallel arrays `names[]`, `scores[][]`, `studentCount` | `list[Student]` of a frozen `@dataclass` |
| `static final int MAX_STUDENTS` | module constant `MAX_STUDENTS` (convention only, not enforced) |
| `Scanner` + `hasNextInt` + `nextLine()` buffer fix | `input()` returns a whole line; no leftover newline problem |
| `(double) sum / n` cast | `/` is always true division |
| `printf("%-15s %8d")` | f-string `{x:<15}` / `{n:>8d}` |
| `equalsIgnoreCase` | `casefold()` on both sides |
| `switch` with `default` | `if/elif/else` |
| `System.err.println` for the invalid option | printed on the same output stream here (simplification) |
| `char grade` | one-letter `str` |

## Key Rules / Gotchas Recap
- Validate in the data class (`__post_init__`), so invalid objects cannot exist, and also parse raw text separately.
- `int("1_0") == 10` and `bool` is an `int`: do not trust `int()` alone for "is this a whole number".
- A frozen dataclass cannot assign in `__post_init__`; use `object.__setattr__` once to store a cleaned value.
- Strict `>`/`<` means ties go to the first student.
- `%.2f`-style rounding on the floats is Python's (round-half-even on the binary value); the averages here are `n/3` so no `.xx5` ties occur per student, but a class average could in theory differ from Java's HALF_UP on an exact tie.
- `input()` raises `EOFError` at end of piped input: catch it in `main()`.

## Why This Structure Exists
Separating a testable core from a thin interactive shell is how real tools are built (a CLI and a web API can then share the same core), and it is what lets 41 pytest tests cover this app without typing anything.
