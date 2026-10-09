# `_5_ControlFlow.java`

## Concept
Conditional branching — `if`, `if-else`, `if-else if-else`, nested `if`, `switch` (traditional and modern), and the ternary operator as a control-flow shortcut.

## Full Line-by-Line Breakdown

### `public class _5_ControlFlow {`
Declares the class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: If Statement

**`int temperature = 35;`**
Value being tested.

**`if (temperature > 30) { ... }`**
Checks the condition `temperature > 30`. Since `35 > 30` is `true`, the code inside the braces runs, printing `"It's hot outside."` If the condition were `false`, this block would simply be skipped — there's no alternative path here.

---

### SECTION 2: If-Else Statement

**`int age = 16;`**
Value being tested.

**`if (age >= 18) { ... } else { ... }`**
Since `16 >= 18` is `false`, the `if` block is skipped and the `else` block runs instead, printing `"You cannot vote yet."` The `else` provides a guaranteed alternative path when the condition fails.

---

### SECTION 3: If-Else If-Else Chain

**`int score = 72;`**
Value being tested against multiple thresholds.

**`if (score >= 90) ... else if (score >= 80) ... else if (score >= 70) ... else if (score >= 60) ... else ...`**
Java checks each condition **top to bottom** and stops at the **first** one that's `true`. Since `72 >= 70` is the first matching condition (it already failed `>= 90` and `>= 80`), `"Grade: C"` prints. Even though `72 >= 60` is *also* technically true, that branch never runs — only one branch in the whole chain ever executes.

---

### SECTION 4: Nested If Statements

**`boolean hasTicket = true;` / `int visitorAge = 25;`**
Two conditions to check in combination.

**Outer `if (hasTicket) { ... } else { ... }`**
First checks if a ticket exists at all.

**Inner `if (visitorAge >= 18) { ... } else { ... }`**
Only runs if the outer condition (`hasTicket`) was `true` — this is what makes it "nested." Since both `hasTicket` is `true` and `visitorAge >= 18` is `true`, `"Entry allowed: Adult with ticket."` prints.

---

### SECTION 5: Logical Operators in Conditions

**`boolean isWeekend = true;` / `boolean isHoliday = false;`**
Two conditions to combine instead of nesting.

**`if (isWeekend || isHoliday) { ... } else { ... }`**
Using `||` (OR) means only **one** of the two needs to be `true`. Since `isWeekend` is `true`, the whole condition is `true`, and `"No work today!"` prints — this achieves the same result as a nested `if`, but more concisely.

**`int accountBalance = 500;` / `boolean isVerified = true;`**
Two conditions requiring both to be true.

**`if (accountBalance > 0 && isVerified) { ... } else { ... }`**
Using `&&` (AND) means **both** conditions must be `true`. Since `500 > 0` and `isVerified` are both `true`, `"Transaction approved."` prints.

---

### SECTION 6: Switch Statement (Traditional Style)

**`int dayNumber = 3;` / `String dayName;`**
The value to check, and a variable to hold the result.

**`switch (dayNumber) { case 1: ... break; case 2: ... break; ... }`**
Compares `dayNumber` against each `case` value in order. When it finds a match (`case 3:`), it runs that case's code (`dayName = "Wednesday";`) and then hits `break;`, which exits the switch immediately — preventing it from continuing into the next case.

**`default: dayName = "Invalid day number"; break;`**
Runs only if `dayNumber` didn't match any of the listed cases — the switch's fallback option.

**`System.out.println("Day: " + dayName);`**
Prints the result: `"Day: Wednesday"`.

**The fall-through explanation comment**
Demonstrates what happens if `break` is forgotten: execution doesn't stop at the matching case, it keeps running into every case **below** it too, regardless of whether they match. This is why traditional `switch` is considered error-prone — it's easy to forget a `break` and silently create bugs.

---

### SECTION 7: Switch Expression (Modern Style, Java 14+)

**`int monthNumber = 4;`**
Value being checked.

**`String season = switch (monthNumber) { case 12, 1, 2 -> "Winter"; ... };`**
The modern arrow-based switch. Key differences from the traditional version:
- Multiple values can share one case, separated by commas (`case 12, 1, 2`)
- The arrow (`->`) means "if this matches, the result is this value" — no `break` needed, and no fall-through risk at all
- The entire `switch` expression can be **directly assigned** to a variable (`String season = switch(...) {...};`), rather than needing a separate variable declared beforehand and reassigned inside each case

Since `monthNumber` is `4`, it matches `case 3, 4, 5`, so `season` becomes `"Spring"`.

---

### SECTION 8: Ternary as a Control Flow Shortcut

**`int number = 15;`**
Value being tested.

**`String parity = (number % 2 == 0) ? "Even" : "Odd";`**
A compact one-line if-else (recap from Operators): checks if `number % 2 == 0` (i.e., divisible by 2 with no remainder). Since `15 % 2` is `1` (not `0`), the condition is `false`, so `parity` becomes `"Odd"`.

---

### SECTION 9: Common Pitfalls to Avoid

**`int pitfallValue = 10;`**
Value used to demonstrate a classic bug.

**`if (pitfallValue == 10) { ... }`**
Correctly uses `==` (comparison) rather than `=` (assignment). The comment explains that writing `if (pitfallValue = 10)` by mistake would actually be a **compile error** in Java — unlike some other languages, Java requires an `if` condition to evaluate to a `boolean`, and a plain assignment doesn't produce one. This is a built-in safety net against a very common typo bug.

**`int x = 5;`**
**`if (x > 0) { ... } else { ... }`**
Demonstrates always using `{ }` braces, even for single-line if/else bodies. The comment explains this avoids the "dangling else" problem — a subtle bug where adding a second line to an if-block *without* braces can accidentally attach that new line to the wrong branch, since Java (without braces) only treats the very next single statement as belonging to the `if`.

## Key Rules / Gotchas Recap

- In an if-else-if chain, only **one** branch ever runs — the first one that matches, even if later conditions would also technically be true
- Traditional `switch` requires `break` on every case, or execution **falls through** into the next case regardless of a match — a very common beginner bug
- The modern arrow-style `switch` expression eliminates fall-through entirely and can be assigned directly to a variable
- Java protects against the `=` vs `==` typo — an accidental assignment inside an `if` condition won't even compile
- Always use `{ }` braces on if/else blocks, even single-line ones, to avoid the "dangling else" ambiguity

## Why This Structure Exists

Conditional branching is how a program makes decisions — nearly every non-trivial piece of logic depends on correctly choosing between different paths based on some condition, whether that's a simple `if`, a multi-way `switch`, or a compact ternary.