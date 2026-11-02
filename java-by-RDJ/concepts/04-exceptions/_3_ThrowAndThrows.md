# `_3_ThrowAndThrows.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
`throw` (no s) **creates** an exception right here. `throws` (with s) **declares** that a method may pass a checked exception to its caller. An uncaught exception travels up the call stack until something catches it.

## Full Line-by-Line Breakdown

### The helper methods
- `validateAge`: `throw new IllegalArgumentException(...)` for a negative age. Unchecked, so no `throws`.
- `loadData() throws IOException`: throws a checked exception, which **must** be declared.
- `methodA` → `methodB` → `methodC`: three stacked methods. `C` throws `IllegalStateException`; `C` and `B` have only `finally`; `A` catches.
- `rethrowExample`: catches an `IOException`, logs, then `throw e;` passes the **same** exception on.

### SECTION 1: `throw`
Rejecting invalid input early with a clear message: `Caught: Age cannot be negative: -5`.

### SECTION 2: `throws`
Calling `loadData()` without handling it is a compile error, so it is wrapped in `try`/`catch`. Output: `Caught: disk not ready`.

### SECTION 3: Travelling up the call stack
```
methodA: calling B
methodB: calling C
methodC: about to fail
methodC: finally runs while the exception travels up
methodB: finally runs too
methodA: caught it -> something broke in C
```
After `C` throws, the rest of `C` and the rest of `B` are **skipped** (`"methodB: this line is skipped"` never prints), but each `finally` still runs on the way up. `A` finally catches it, and `main` carries on normally.

### SECTION 4: Reading a stack trace
`getStackTrace()` lists the call chain, **innermost first**. `[0]` is `methodC` (where it was thrown); `[1]` is `main` (who called it). Output: `Thrown inside method: methodC, called from: main`.

### SECTION 5: Rethrowing
Catch to do something (log, clean up), then `throw e;` so the caller still learns about it. Rethrow the original; do not hide it.

### SECTION 6: Where to catch
Catch where you can do something useful (retry, show a message, use a default). If you cannot, let it propagate. Catching too early and doing nothing hides bugs.

## Key Rules / Gotchas Recap
- `throw` is an action; `throws` is a declaration
- An exception skips the rest of the method, but `finally` blocks still run on the way up
- Stack traces list the innermost call first

## Why This Structure Exists
The call stack is how Java finds a handler. Understanding that an exception leaves methods one by one explains why `finally` exists and why catching at the right level matters.
