# `_5_TryWithResources.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
`try-with-resources` closes anything that implements `AutoCloseable` automatically when the block ends, whether it finished normally or threw.

## Full Line-by-Line Breakdown

### The `Resource` class
Implements `AutoCloseable`. The constructor prints `open <name>`; `use(boolean fail)` prints `using <name>` and optionally throws `IllegalStateException`; `close()` prints `close <name>` and optionally throws `IllegalArgumentException` (when `failOnClose` is true).

### SECTION 1: The old way
```java
Resource old = null;
try { old = new Resource(...); old.use(false); }
finally { if (old != null) old.close(); }
```
Easy to get wrong: you must remember the `finally`, the null check, and that `close()` itself can throw.

### SECTION 2: Automatic closing
```java
try (Resource r = new Resource("file", false)) { r.use(false); }
```
Output order: `open`, `using`, `close`.

### SECTION 3: Close happens even when the body throws
The body throws, but `close db-connection` is printed **before** the `catch` runs. The `catch` message says the resource was already closed.

### SECTION 4: Several resources close in reverse order
Opened `A` then `B`; closed `B` then `A` (last opened, first closed, like stacking plates).

### SECTION 5: Suppressed exceptions
The body throws **and** `close()` throws. The exception you catch is the body's (`primary: body failed using fragile`); the close failure is attached to it: `suppressed: [java.lang.IllegalArgumentException: close failed for fragile]`, readable via `e.getSuppressed()`. With the old `finally` style, the close failure would **replace** the original and hide the real cause.

### SECTION 6: Scope
The variable exists only inside the `try` block (it is effectively final) and is already closed when `catch` or `finally` run. The commented-out line would not compile.

### SECTION 7: What you will use it for
Files, streams, database connections, sockets. It appears again in `07-file-io` and `10-jdbc-sql`.

## Key Rules / Gotchas Recap
- Resources close in **reverse** order of declaration
- If both the body and `close()` throw, the body's exception wins and the other is **suppressed**
- Prefer it to a manual `finally` for anything that must be released

## Why This Structure Exists
Forgetting to close a file or connection leaks resources, and writing the close logic by hand is error-prone. The language feature makes the safe way the short way.
