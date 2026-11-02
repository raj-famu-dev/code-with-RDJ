# `_1_ExceptionHandlingBasics.java`

> Walkthrough drafted with Claude from your existing code. Check it against your own understanding and rewrite it in your own words.

## Concept
An exception is an unexpected event that disrupts normal program flow. Without handling, it crashes the program. `try`/`catch`/`finally` lets the program respond instead of dying.

## Full Line-by-Line Breakdown

### SECTION 1–2: What an exception is, and the crash it prevents
`int result = 10 / 0;` would throw `ArithmeticException: / by zero` and stop the program, so the next line would never run. It is commented out so the rest of the file can run.

### SECTION 3: Basic `try`-`catch`
```java
try { int result = 10 / 0; ... }
catch (ArithmeticException e) { System.out.println("Caught an error: " + e.getMessage()); }
```
Control jumps from the failing line straight to `catch`. Output: `Caught an error: / by zero`, then `Program continues running normally after the catch!`

### SECTION 4: `try`-`catch`-`finally`
`numbers[5]` on a 3-element array throws `ArrayIndexOutOfBoundsException`. The `finally` block runs whether or not an error happened: `Finally block: this always runs, error or not.` Used for cleanup (closing files, connections).

### SECTION 5: Multiple `catch` blocks
Calling `.length()` on a `null` string throws `NullPointerException`. Java checks the `catch` blocks top to bottom and uses the **first match**, so the `NullPointerException` block runs. Order matters: specific types must come **before** general ones like `Exception`; reversing them is a compile error because the specific one becomes unreachable. (In this run the message also names the variable, e.g. `Cannot invoke "String.length()" because "<local1>" is null`; the variable name appears as `text` if you compile with `javac -g`.)

### SECTION 6: Multi-catch
`catch (ArithmeticException | ArrayIndexOutOfBoundsException e)` handles several types the **same** way in one block. With `choice = 2`, the array branch runs and the output is `Caught one of two possible errors: Index 10 out of bounds for length 2`.

### SECTION 7: Checked vs unchecked (preview)
Unchecked (`RuntimeException` and subclasses) need no handling; checked ones (like `IOException`) must be caught or declared with `throws`. Covered fully in `_2_CheckedVsUnchecked`.

### SECTION 8: `throw` vs `throws` (preview)
```java
static void checkAge(int age) {
    if (age < 18) throw new IllegalArgumentException("Age must be 18 or older, got: " + age);
}
```
`throw` actually triggers an exception. `checkAge(15)` produces `Validation failed: Age must be 18 or older, got: 15`; `checkAge(25)` prints `Age 25 is valid.`

### SECTION 9: `getMessage()` vs `printStackTrace()`
`getMessage()` is a short description. `printStackTrace()` shows the full chain of calls and the line number where it happened (`at _1_ExceptionHandlingBasics.main(...:133)`), which is what you read when debugging.

### SECTION 10: Real-world connection
The `Scanner.nextBoolean()` crash from `_10_UserInput` is now handled: wrapping it in `try`-`catch (InputMismatchException)` prints a friendly message instead of crashing. This section **reads from the keyboard**, so run the file interactively (or pipe input in).

## Key Rules / Gotchas Recap
- Put risky code in `try`; handle the failure in `catch`; use `finally` for cleanup that must always happen
- Specific `catch` blocks first, general ones last
- Multi-catch (`A | B`) is for types you handle identically
- Always read the stack trace from the top: that is where the problem was thrown

## Why This Structure Exists
Programs deal with input and conditions they cannot fully control. Exceptions separate "the normal path" from "the failure path", so the normal code stays readable and failures are handled in one place.
