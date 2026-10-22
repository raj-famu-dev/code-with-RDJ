# `_1_HelloWorld.py`

## Concept
Program structure and output — and the complete absence of any required class or entry-point method, which is the single biggest structural difference from Java right from line one.

## The Full Code

```python
# ============================================
# TOPIC 1: HELLO WORLD & PROGRAM STRUCTURE
# Unlike Java, Python has NO required class or main() method.
# Code runs top-to-bottom, directly, the moment the file executes.
# ============================================

print("Hello, RDJ is coding in Python!")


# ============================================
# THE if __name__ == "__main__": PATTERN
# This IS something like Java's main() - but it's a CONVENTION,
# not a requirement.
# ============================================

def greet():
    print("This only runs when the file is executed directly.")

if __name__ == "__main__":
    greet()
```

## Line-by-Line Breakdown

### `print("Hello, RDJ is coding in Python!")`
This line runs **immediately**, the moment the file is executed — there's no class wrapper, no method signature, nothing surrounding it at all. `print()` is a built-in function, always available, requiring no import.

### `def greet():`
Declares a function named `greet`, using the `def` keyword. No return type, no access modifier, no class required to contain it.

### `print("This only runs when the file is executed directly.")`
The body of `greet()` — simply prints a message. Indentation (not braces) marks this as belonging to the function.

### `if __name__ == "__main__":`
`__name__` is a special, automatically-set variable every Python file has. When you run this file **directly** (e.g., `python _1_HelloWorld.py`), Python sets `__name__` to the string `"__main__"`. If this same file is instead **imported** by another Python file, `__name__` is set to the module's own name instead (e.g., `"_1_HelloWorld"`).

### `greet()`
Calls the function — but only if the `if` condition above was true, meaning only when this file was run directly.

## Why `if __name__ == "__main__":` Exists At All

Python files can serve two purposes: a standalone script you run directly, or a reusable module that other files `import` for its functions/classes. The `if __name__ == "__main__":` guard lets a single file do both safely — if someone imports this file just to reuse `greet()`, the `greet()` call at the bottom won't accidentally fire; it only runs when **this exact file** is the one being executed.

## Key Differences From Java

| Concept | Java | Python |
|---|---|---|
| Required entry point | `public class X { public static void main(String[] args) {} }` — mandatory | None — code runs top to bottom from the top of the file |
| File-to-class name matching | File name must match the public class name | No such requirement — no class needed at all |
| Statement termination | Semicolons | Line breaks |
| Closest equivalent to `main()` | N/A — it's mandatory | `if __name__ == "__main__":` — optional, used only when a file might be imported elsewhere |
| Printing | `System.out.println("text");` | `print("text")` |

## Key Rules / Gotchas Recap

- Python code executes top-to-bottom immediately — there's no "waiting" for a special method to be called first
- `if __name__ == "__main__":` is a **convention**, not a language requirement — small scripts often skip it entirely
- Functions can exist completely standalone, with no class required to hold them — something Java never allows

## Why This Structure Exists

Java enforces a mandatory entry point so the JVM always knows exactly where to begin execution, regardless of how large the codebase grows. Python trades that enforced structure for simplicity — small scripts can be a single `print()` statement with zero ceremony, while the `if __name__ == "__main__":` pattern exists purely as an opt-in safeguard for files that might later be reused as importable modules.