# `_6_ExceptionsAndCustomErrors.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
An exception is Python's way of reporting that something went wrong and unwinding the call stack until some `except` block handles it. `try/except/else/finally` lets you separate the risky step, the error handling, the "it worked" path and the always-run cleanup. You define your own exception classes (a small hierarchy under one base class) so callers can catch your errors precisely, and `raise ... from ...` preserves the original cause. Python **has no checked exceptions**: nothing forces anyone to catch anything.

## Full Line-by-Line Breakdown

### SECTION 1: try / except / else / finally
`try` holds the risky code. `except ZeroDivisionError` runs only if that error occurs. `else` runs **only if no exception happened**; put code there that should not be protected by the `except` (so you do not accidentally catch errors from it). `finally` **always** runs, even when the function returns inside `try` or `except`. In the output, `divide(6, 3)` shows `else` then `finally`; `divide(1, 0)` shows `except` then `finally`, and still returns `None`.

```text
=== SECTION 1: try / except / else / finally ===
divide(6, 3):
  else ran: no error
  finally ran
 -> 2.0
divide(1, 0):
  except ran: division by zero
  finally ran
 -> None

```

### SECTION 2: multiple except clauses and order
Python checks `except` clauses top to bottom and runs the **first** that matches, so put specific exceptions before general ones. A tuple (`except (TypeError, KeyError)`) handles several types the same way. `int("abc")` raises `ValueError`; `int(None)` raises `TypeError`. `FileNotFoundError` is a subclass of `OSError`, so `except OSError` catches it. A bare `except:` also catches `KeyboardInterrupt` and `SystemExit`; prefer `except Exception`.

```text
=== SECTION 2: multiple except clauses and order ===
parsed: 42
ValueError: invalid literal for int() with base 10: 'abc'
TypeError/KeyError: TypeError
FileNotFoundError is a subclass of OSError: True
bare `except:` also catches KeyboardInterrupt; prefer `except Exception`.

```

### SECTION 3: custom exception hierarchy
`AppError(Exception)` is the root of your own errors; `ConfigError` extends it and adds a `path` attribute; `ConfigMissingError` and `ConfigCorruptError` are specific kinds. A caller can catch the exact subclass, or the parent `ConfigError`, or everything with `AppError`. The loop raises two exceptions and shows the specific handler catching one while the parent handler catches the other. The method resolution order (`__mro__`) shows the inheritance chain.

```text
=== SECTION 3: custom exception hierarchy ===
missing handler: no file | path = a.json
generic config handler: bad json | path = None
MRO: ['ConfigMissingError', 'ConfigError', 'AppError', 'Exception', 'BaseException', 'object']

```

### SECTION 4: raise ... from (exception chaining)
Inside `load_config`, low-level errors (`FileNotFoundError`, `JSONDecodeError`) are translated into domain errors with `raise ConfigMissingError(...) from e`. The original stays attached as `__cause__`, so the traceback shows both. `raise ... from None` hides the original on purpose. A bare `raise` inside an `except` block re-raises the same exception unchanged.

```text
=== SECTION 4: raise ... from (exception chaining) ===
caught: ConfigMissingError - config file not found
  __cause__: FileNotFoundError
  __suppress_context__: True
raise from None -> __cause__: None
Bare `raise` inside except re-raises the SAME exception unchanged.

```

### SECTION 5: EAFP vs LBYL
**LBYL** ("Look Before You Leap") checks first (`if "b" in d`). **EAFP** ("Easier to Ask Forgiveness than Permission") just tries and catches the failure. Python style prefers EAFP, especially for files: between `path.exists()` and `open()` another process could create or delete the file (a race condition), whereas a single `open()` plus `except FileNotFoundError` has no gap. For dictionaries, `d.get("b", 0)` is the shortest form.

```text
=== SECTION 5: EAFP vs LBYL ===
LBYL: 0
EAFP: 0
dict.get is the shortest: 0
LBYL file race: exists() -> False (file could appear/vanish before open!)
EAFP: just try it; no race window between check and use

```

### SECTION 6: missing, empty and corrupt files
A realistic loader meets five situations: a good file, a missing file, an empty file, a corrupt file and a path that is a directory. The code classifies each into the right custom error (or lets `IsADirectoryError`, an `OSError`, be reported separately). Notice that an empty file counts as corrupt because empty text is not valid JSON.

```text
=== SECTION 6: missing, empty and corrupt files ===
good.json     -> OK {'port': 8080}
missing.json  -> MISSING  (config file not found)
empty.json    -> CORRUPT  (invalid JSON: Expecting value)
corrupt.json  -> CORRUPT  (invalid JSON: Expecting value)
dir.json      -> OS ERROR (IsADirectoryError)

```

### SECTION 7: finally for cleanup; assert is not validation
`finally` guarantees cleanup (here closing a file) while the exception continues to propagate. The `with` statement is exactly this pattern packaged. Finally, `assert` statements are removed when Python runs with `-O`, so never use them to validate user input; raise `ValueError` or a custom error.

```text
=== SECTION 7: finally for cleanup; assert is not validation ===
  finally: file closed = True
propagated: fail midway
`with` is just try/finally packaged (see _1_OpenAndWithStatement).
Use `raise ValueError` for input checks, not `assert`: python -O strips asserts.

```

### SECTION 8: ExceptionGroup (3.11+), a brief look
`ExceptionGroup` bundles several exceptions (used by `asyncio` task groups), and `except*` handles each type from the group separately. You will rarely write these by hand early on, but you will meet them in modern async code.

```text
=== SECTION 8: ExceptionGroup (3.11+), a brief look ===
except* ValueError got: ['ValueError']
except* TypeError got: ['TypeError']

temp dir removed: True
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Checked exceptions | `IOException` etc. must be caught or declared with `throws` | **None.** All exceptions are unchecked; no `throws` clause exists |
| Syntax | `try { } catch (A \| B e) { } finally { }` | `try: ... except (A, B) as e: ... else: ... finally: ...` |
| `else` clause | Does not exist | Runs only when `try` raised nothing |
| Cleanup | try-with-resources (`AutoCloseable`) | `with` statement (context manager) |
| Throw | `throw new IllegalStateException("x")` | `raise ValueError("x")` |
| Chaining | `new AppException("msg", cause)` or `initCause` | `raise AppError("msg") from cause` |
| Custom exception | `class MyEx extends Exception` (checked) or `RuntimeException` | `class MyError(Exception)`; there is no checked variant |
| Base of everything | `Throwable` -> `Exception` / `Error` | `BaseException` -> `Exception` (and `KeyboardInterrupt`, `SystemExit`) |
| Philosophy | LBYL is common; checked exceptions document failure modes in signatures | EAFP is idiomatic; document errors in docstrings and types |
| Multiple errors | Suppressed exceptions in try-with-resources | `ExceptionGroup` / `except*` (3.11+) |

## Key Rules / Gotchas Recap

- Catch specific exceptions first; avoid bare `except:` and avoid swallowing errors silently.
- Put only the risky line in `try`; use `else` for the follow-up code.
- `finally` always runs; do not `return` from it (that would hide errors).
- Derive custom errors from one `AppError` base so callers can catch the whole family.
- Use `raise ... from e` when translating errors, and `from None` only deliberately.
- Prefer EAFP for files; checking `exists()` first leaves a race condition.
- Use real exceptions for validation, not `assert`.

## Why This Structure Exists
Programs that process files, network data or model output constantly meet missing, empty or malformed input. A clear exception hierarchy lets you show the user a useful message, retry, or fail safely, which is also the foundation of security tooling that must survive hostile input without crashing.
