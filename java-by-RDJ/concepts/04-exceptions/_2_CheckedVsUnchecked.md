# `_2_CheckedVsUnchecked.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
Java splits exceptions into **checked** (the compiler forces you to handle or declare them) and **unchecked** (it does not). `Error` is a third kind: JVM-level trouble not meant to be handled.

## Full Line-by-Line Breakdown

### The helper methods
- `readFirstLine(String) throws IOException`: a checked exception **must** be declared. It uses `Files.readAllLines`.
- `parseAge(String)`: calls `Integer.parseInt`, which can throw the unchecked `NumberFormatException`, so no `throws` is needed.
- `recurseForever`: calls itself with no end, to cause a `StackOverflowError` safely.

### SECTION 1: The family tree
```
Throwable
  Error                    (OutOfMemoryError, StackOverflowError)
  Exception
    IOException, ...       CHECKED
    RuntimeException       UNCHECKED
      NullPointerException, IllegalArgumentException, ...
```
Two `isAssignableFrom` checks print `true`: `IOException` is a checked `Exception` (it is not under `RuntimeException`), and `NumberFormatException` is unchecked.

### SECTION 2: What the compiler enforces
Calling `readFirstLine(...)` without handling it is a compile error (`unreported exception IOException`). So the call is wrapped in `try`/`catch (IOException e)`. Output: `Caught checked IOException: NoSuchFileException` (a subclass of `IOException`).

### SECTION 3: Unchecked exceptions
The compiler stays quiet. These usually signal a **bug** in the calling code, so you fix the code rather than writing a handler for every one. Output: `NumberFormatException: For input string: "twenty"` and a caught `NullPointerException`.

### SECTION 4: `Error`
`StackOverflowError` is caught only to **show** that it is an `Error`, not an `Exception`. Real code should not try to recover from errors.

### SECTION 5: Why the line is drawn here
- **Checked:** failures outside the program's control where the caller can plausibly recover (file missing, network down). The compiler makes you think about them.
- **Unchecked:** programming mistakes. Forcing a `try`/`catch` on every call would bury the code.
Many modern libraries prefer unchecked exceptions because `throws` clauses spread through every layer.

### SECTION 6: Quick test
`FileNotFoundException` → checked (extends `IOException`); `ClassCastException` → unchecked; `Exception` itself → checked; `RuntimeException` itself → unchecked.

## Key Rules / Gotchas Recap
- Checked = `Exception` and subclasses **except** the `RuntimeException` branch
- Unchecked = `RuntimeException` and subclasses, plus `Error`
- Catch-or-declare applies only to checked exceptions

## Why This Structure Exists
The split encodes a design opinion: some failures are expected conditions the caller should plan for, others are bugs. Knowing which is which tells you whether to write a handler or fix the code.
