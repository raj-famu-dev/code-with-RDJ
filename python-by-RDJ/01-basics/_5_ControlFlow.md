# `_5_ControlFlow.py`

## Concept
Conditional branching using indentation instead of braces, plus `match-case` as Python's modern switch replacement — with no fall-through risk at all.

## The Full Code

```python
temperature = 35
if temperature > 30:
    print("It's hot outside.")

age = 16
if age >= 18:
    print("You can vote.")
else:
    print("You cannot vote yet.")

score = 72
if score >= 90:
    print("Grade: A")
elif score >= 80:
    print("Grade: B")
elif score >= 70:
    print("Grade: C")
elif score >= 60:
    print("Grade: D")
else:
    print("Grade: F")

has_ticket = True
visitor_age = 25
if has_ticket:
    if visitor_age >= 18:
        print("Entry allowed: Adult with ticket.")
    else:
        print("Entry denied: Minor, even with ticket.")
else:
    print("Entry denied: No ticket.")

day_number = 3
match day_number:
    case 1:
        day_name = "Monday"
    case 2:
        day_name = "Tuesday"
    case 3:
        day_name = "Wednesday"
    case _:
        day_name = "Invalid day number"

month_number = 4
match month_number:
    case 12 | 1 | 2:
        season = "Winter"
    case 3 | 4 | 5:
        season = "Spring"
    case _:
        season = "Invalid month"

number = 15
parity = "Even" if number % 2 == 0 else "Odd"

pitfall_value = 10
if pitfall_value == 10:
    print("Correct comparison works.")
```

## Line-by-Line Breakdown

### `if temperature > 30:`
Note the **colon** at the end — every `if`/`elif`/`else`/`match`/`case` line must end with one; forgetting it is a `SyntaxError`. Parentheses around the condition are optional (Python allows them, but they're not required the way Java's `if (condition)` demands them).

### `print("It's hot outside.")` (indented below the `if`)
This line belongs to the `if` block **purely because of its indentation level** — there are no curly braces anywhere in Python. This is not cosmetic formatting; indentation **is** the actual block-defining syntax.

### `elif score >= 80:`
Python's single-word equivalent of Java's `else if`. The chain behaves identically otherwise: Java checks conditions top to bottom, running only the first one that's true.

### Nested `if` inside `if` (the ticket/age example)
Nesting works through **additional indentation levels** — the inner `if`/`else` is indented one level further than the outer one. No braces to count, just consistent indentation (standard convention is 4 spaces per level).

### `match day_number:` / `case 1:` / `case _:`
Python's modern replacement for Java's switch (available since Python 3.10). `case _:` is the default/fallback case — the underscore means "match anything not already matched above." **No `break` statement exists or is needed anywhere** — Python's `match-case` can never fall through to the next case, which eliminates the single most common bug category from Java's traditional switch entirely.

### `case 12 | 1 | 2:`
The `|` symbol lets one case match multiple values — conceptually the same idea as Java's modern `case 12, 1, 2 ->` syntax, just using a different symbol (pipe instead of comma).

### `parity = "Even" if number % 2 == 0 else "Odd"`
Recap of the ternary-style expression from Topic 3, shown here as a control-flow shortcut for simple two-way branches.

### `if pitfall_value == 10:`
Demonstrates the correct comparison operator. The comment in the original code explains what happens if you accidentally write `=` instead of `==` inside a condition: in Python, this is an outright **`SyntaxError`** — the language's grammar doesn't even permit an assignment expression to appear where a condition is expected, so the mistake can't silently compile at all (compare this to Java, where the same mistake is caught as a *type* error — assignment doesn't evaluate to boolean — rather than a *grammar* error).

## Key Differences From Java

| Concept | Java | Python |
|---|---|---|
| Block definition | Curly braces `{ }` | **Indentation itself** — not cosmetic, it's the actual syntax |
| Condition syntax | `if (condition) { }` — parentheses required | `if condition:` — colon required, parentheses optional |
| "else if" | `else if` | `elif` |
| Switch | Traditional `switch`/`case`/`break`, or modern arrow-style | `match`/`case` (3.10+), or if-elif chains for older code |
| Switch fall-through | A real risk if `break` is forgotten | **Cannot happen at all** |
| Multiple values per case | `case 1, 2, 3 ->` | `case 1 \| 2 \| 3:` |
| Default case | `default ->` | `case _:` |
| `=` vs `==` typo | Compile error (assignment isn't boolean) | **Syntax error** — grammar forbids `=` in a condition entirely |
| Most common structural bug | Mismatched/missing braces | `IndentationError` from mixed tabs/spaces or wrong indent level |

## Key Rules / Gotchas Recap

- Indentation defines every block in Python — two lines with different indentation are structurally different code, not just differently formatted
- `match-case` never falls through — there is no `break` to forget, unlike Java's traditional switch
- Only one branch of an if-elif-else chain ever runs, same as Java — the first true condition wins and the rest are skipped

## Why This Structure Exists

Conditional branching is how a program makes decisions, and Python's design choice to use indentation as actual syntax (rather than optional, cosmetic braces) forces visually consistent code by construction — you cannot write deeply nested, badly formatted logic the way Java technically allows, since inconsistent indentation simply won't run.