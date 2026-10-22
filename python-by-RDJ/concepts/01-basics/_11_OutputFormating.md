# `_11_OutputFormatting.py`

## Concept
f-strings as Python's modern formatting standard — embedding expressions directly, plus three generations of formatting history, raw strings, and the debug-printing shortcut Java has no equivalent for.

## The Full Code

```python
print("This prints text AND moves to a new line after")
print("This stays on the same line...", end="")
print(" ...so this continues right after it")
print()

import sys
print("This prints to the ERROR stream", file=sys.stderr)

name = "RDJ"
age = 25
salary = 55000.5
print(f"Name: {name}, Age: {age}, Salary: {salary}")
print(f"Next year you'll be {age + 1}")
print(f"Uppercase name: {name.upper()}")

pi = 3.14159265
print(f"Default: {pi}")
print(f"2 decimals: {pi:.2f}")
print(f"4 decimals: {pi:.4f}")
print(f"0 decimals: {pi:.0f}")

print(f"[{42:10d}]")
print(f"[{42:<10d}]")
print(f"[{'Hi':10s}]")
print(f"[{'Hi':>10s}]")
print(f"[{'Hi':^10s}]")

items = ["Apple", "Bread", "Milk"]
prices = [1.50, 3.25, 2.10]
print(f"{'Item':<10} {'Price':>10}")
for item, price in zip(items, prices):
    print(f"{item:<10} {price:>10.2f}")

formatted_message = "Hello {}, you are {} years old.".format(name, age)

old_style = "Name: %s, Age: %d" % (name, age)

print("Newline example:\nThis is on a new line")
print("Backslash example: C:\\Users\\RDJ")
raw_path = r"C:\Users\RDJ"

text_block = """This spans multiple lines.
No escape characters needed at all."""

large_number = 1234567
print(f"With commas: {large_number:,}")
large_money = 9876543.21
print(f"Money with commas: ${large_money:,.2f}")

x = 42
print(f"{x=}")
print(f"{age + 1=}")
```

## Line-by-Line Breakdown

### `print("...", end="")`
`end` is a hidden parameter on `print()`, defaulting to `"\n"` (a newline) — that's why every normal `print()` call lands on its own line. Setting `end=""` suppresses that, keeping the cursor on the same line, similar in effect to Java's `System.out.print()`.

### `print("...", file=sys.stderr)`
Redirects output to the error stream, conceptually matching Java's `System.err.println()` — but requires `import sys` first, since this isn't automatically available the way Java's `System.err` is.

### `print(f"Name: {name}, Age: {age}, Salary: {salary}")`
**f-strings** — the `f` immediately before the opening quote marks this as a formatted string literal. Anything inside `{ }` is evaluated and embedded directly into the output.

### `print(f"Next year you'll be {age + 1}")`
f-strings can embed **any expression**, not just bare variables — arithmetic, method calls, anything that evaluates to a value. `print(f"Uppercase name: {name.upper()}")` on the next line does the same thing with a method call instead of arithmetic. Java's `printf` has no equivalent capability — it can only insert pre-computed values, never evaluate expressions inline.

### `print(f"Default: {pi}")` → shows the full value, not rounded to 6 decimals
A genuine difference from Java: `%f` in Java's `printf` **always** defaults to showing 6 decimal places. Python's f-strings show the **full actual precision** of the float unless you explicitly specify otherwise.

### `f"{pi:.2f}"`, `f"{pi:.4f}"`, `f"{pi:.0f}"`
The format specification goes after a colon, inside the same braces. `.2f` means exactly 2 decimal places, rounding (not truncating) the value — same rounding rule as Java's `%.2f`.

### `f"[{42:10d}]"` / `f"[{42:<10d}]"`
Field width and alignment: a bare number (`10d`) defaults to right-aligned for numeric types; `<` forces left alignment.

### `f"[{'Hi':^10s}]"`
The `^` alignment symbol **centers** the text within the given width — Java's `printf` has **no centering option whatsoever**; this is purely a Python capability.

### `for item, price in zip(items, prices):`
`zip()` pairs up two lists element-by-element for iteration — `items[0]` with `prices[0]`, `items[1]` with `prices[1]`, and so on. This has no direct Java equivalent; Java would require manual indexing across both arrays with a shared loop counter.

### `"Hello {}, you are {} years old.".format(name, age)`
The **older** `.format()` method — still seen in existing Python code written before f-strings became standard (Python 3.6+). Functionally similar to f-strings but more verbose, since the values are passed separately rather than embedded inline.

### `"Name: %s, Age: %d" % (name, age)`
The **oldest** formatting style, using `%`-specifiers — genuinely the closest historical cousin to Java's `printf` syntax, since `%s` and `%d` work almost identically. Considered outdated Python style today, but worth recognizing when reading older code.

### `raw_path = r"C:\Users\RDJ"`
A **raw string**, marked with an `r` prefix immediately before the quote. This disables **all** escape sequence processing — backslashes are treated as literal characters rather than the start of an escape code. Java has no equivalent literal syntax at all; achieving the same effect in Java requires manually doubling every backslash.

### `text_block = """..."""`
Triple-quoted strings (recap from Topic 8) used here specifically for multi-line formatted output — Python's long-standing answer to what Java only gained recently via text blocks.

### `f"{large_number:,}"` / `f"${large_money:,.2f}"`
The comma flag inside the format specifier inserts thousands-separators automatically, and can be combined with decimal precision in the same specifier — same comma-formatting concept as Java's `printf`, just placed differently in the syntax.

### `print(f"{x=}")` → prints `x=42`
**The `=` specifier (Python 3.8+) has no Java equivalent at all.** It prints both the expression's literal text **and** its evaluated value in one go — genuinely useful for quick debugging without manually writing out `print("x =", x)` every time. `f"{age + 1=}"` works the same way even with a full expression, not just a bare variable name.

## Key Differences From Java

| Concept | Java | Python |
|---|---|---|
| Modern formatting | `printf` / `String.format` | f-strings — embed any expression directly |
| Default decimal display | `%f` always shows 6 decimals | Shows full actual precision unless specified |
| Centering text | **No option at all** | `{'text':^10}` |
| Error stream | `System.err.println()` — built in | `print(..., file=sys.stderr)` — needs `import sys` |
| Formatting history | Only `printf`, no legacy styles | Three generations: `%`-formatting → `.format()` → f-strings |
| Raw strings | Doesn't exist | `r"C:\Users\RDJ"` |
| Debug printing (expression + value) | Manual — write it yourself | `f"{x=}"` does it automatically |
| Pairing two lists for iteration | Manual indexing | `zip(list1, list2)` |

## Key Rules / Gotchas Recap

- f-strings show a float's full precision by default — unlike Java's `%f`, which always shows exactly 6 decimals unless told otherwise
- Always prefer f-strings for new code — the older `%`-style and `.format()` exist only to be recognized in legacy code, not written fresh
- `zip()` is the idiomatic way to loop through two sequences together — don't reach for manual indexing if you don't have to

## Why This Structure Exists

Python's formatting approach has evolved across three distinct eras, each coexisting in real-world code you'll encounter — but f-strings consolidate the best of all of them into one readable, expression-embedding syntax that genuinely exceeds what Java's `printf` can do, at the cost of needing to recognize two older, less intuitive styles when reading code written before 2018 or so.