# `_7_FinallyGotchas.java`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`finally` is simple until `return` or `throw` appear inside it. This file reproduces five surprising behaviours so you recognize them.

## Full Line-by-Line Breakdown

### Gotcha 1: `finally` runs even after `return`
`returnInTry()` prints `try: about to return`, then `finally: runs BEFORE the method actually returns`, and only then does the caller get `value from try`.

### Gotcha 2: the primitive return value is fixed early
```java
int x = 1;
try { return x; } finally { x = 99; }
```
Result: `1`, not `99`. The value is remembered at the `return`; changing the variable afterwards does not change what is returned.

### Gotcha 3: a mutable object can still change
```java
StringBuilder sb = new StringBuilder("hello");
try { return sb; } finally { sb.append(" (changed in finally)"); }
```
The **reference** was remembered, but it points to an object that `finally` modifies, so the caller sees `hello (changed in finally)`.

### Gotcha 4: `return` in `finally` swallows an exception
`throw new IllegalStateException("important error")` is thrown, then discarded when `finally` returns normally. Output: `finally wins, exception vanished`. A real error disappears without a trace. The compiler flags this with `javac -Xlint:finally` ("finally clause cannot complete normally"); the file uses `@SuppressWarnings("finally")` only to keep the demo quiet.

### Gotcha 5: an exception in `finally` replaces the original
The caller sees `problem from finally`; `original problem` is lost. (`try-with-resources`, from `_5`, avoids this by suppressing instead.)

### The one thing that skips `finally`
`System.exit(0)` stops the JVM immediately, so `finally` does not run (also a JVM crash or a killed process). Not run in the file because it would end the program.

### How to use `finally` well
Keep it short and only for cleanup; never `return` or `throw` from it; prefer `try-with-resources` for closing resources.

## Key Rules / Gotchas Recap
- `finally` runs even after `return`, **before** the method actually returns
- Primitive return values are fixed at the `return`; object contents are not
- `return`/`throw` inside `finally` hides or replaces the real error

## Why This Structure Exists
`finally` guarantees cleanup, which is powerful. Knowing exactly where that guarantee ends keeps it from silently hiding failures.
