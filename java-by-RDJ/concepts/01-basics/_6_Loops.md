# `_6_Loops.java`

## Concept
Repetition — `for`, `while`, `do-while`, nested loops, `break`/`continue`, for-each, infinite loops, and labeled breaks.

## Full Line-by-Line Breakdown

### `public class _6_Loops {`
Declares the class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: For Loop

**`for (int i = 1; i <= 5; i++) { System.out.println("For loop iteration: " + i); }`**

| Part | Meaning |
|---|---|
| `int i = 1` | **Initialization** — runs exactly once, before the loop starts |
| `i <= 5` | **Condition** — checked before every iteration; loop stops the moment this is `false` |
| `i++` | **Update** — runs after every iteration's body finishes |

Prints `"For loop iteration: 1"` through `"For loop iteration: 5"`, since `i` starts at `1` and stops once it exceeds `5`.

---

### SECTION 2: While Loop

**`int count = 1;`**
Starting value, declared **outside** the loop (unlike `for`, which declares its counter inline).

**`while (count <= 5) { ... count++; }`**
Checks the condition **before** each iteration. Since `count` starts at `1`, it runs, printing the count, then `count++` manually increases it. This repeats until `count` becomes `6`, at which point `6 <= 5` is `false` and the loop stops.

**The comment about manual updating**
Warns that `count++` must be written by hand inside a `while` loop — unlike `for`, there's no built-in "update" slot, so forgetting this line means `count` never changes and the loop never ends.

---

### SECTION 3: Do-While Loop

**`int attempts = 10;`**
Starting value — deliberately set high to prove a point.

**`do { ... attempts++; } while (attempts < 5);`**
The body runs **first**, unconditionally, then the condition is checked **after**. Since the body prints and increments `attempts` to `11` before the condition is ever tested, and `11 < 5` is `false`, the loop stops after exactly **one** run — but critically, it still ran that one time despite the condition being false from the very start. This is the defining difference from a regular `while` loop, which would have skipped the body entirely.

---

### SECTION 4: Nested Loops

**`for (int row = 1; row <= 3; row++) { for (int col = 1; col <= 3; col++) { ... } }`**
A loop **inside** another loop. For every single iteration of the outer loop (`row`), the entire inner loop (`col`) runs completely from start to finish before the outer loop advances.

**`System.out.println(row + " x " + col + " = " + (row * col));`**
Prints each multiplication combination — e.g., `"1 x 1 = 1"`, `"1 x 2 = 2"`, all the way through `row = 3`.

**The comment about total executions**
Confirms the math: outer loop runs 3 times, and for each of those, the inner loop runs 3 times — `3 × 3 = 9` total print statements.

---

### SECTION 5: Break Statement

**`for (int i = 1; i <= 10; i++) { if (i == 6) { break; } System.out.println(...); }`**
Normally this loop would print `1` through `10`. But when `i` reaches `6`, the `break;` statement **immediately exits the entire loop**, skipping everything after it — including the print statement for that iteration and every iteration that would have followed. Result: only `1` through `5` print.

---

### SECTION 6: Continue Statement

**`for (int i = 1; i <= 10; i++) { if (i % 2 == 0) { continue; } System.out.println(...); }`**
`continue` behaves differently from `break` — it only skips the **rest of the current iteration**, then the loop **keeps going** to the next one. Here, whenever `i` is even (`i % 2 == 0`), the print statement is skipped for that specific iteration, but the loop doesn't stop — it just moves on to check the next `i`. Result: only odd numbers (`1, 3, 5, 7, 9`) get printed.

---

### SECTION 7: Enhanced For Loop (For-Each)

**`int[] numbers = {10, 20, 30, 40, 50};`**
An array of integers.

**`for (int num : numbers) { System.out.println("For-each value: " + num); }`**
Reads as "for each `num` in `numbers`." Automatically walks through every element of the array in order, assigning each one to `num` in turn — no manual index tracking (`i`) needed at all.

**`String[] names = {"Alice", "Bob", "Charlie"};`**
An array of Strings.

**`for (String name : names) { System.out.println("Name: " + name); }`**
Same pattern, applied to Strings instead of ints — proves for-each works with any array type.

---

### SECTION 8: Infinite Loops

**`int safetyCounter = 0;`**
Starting counter.

**`while (true) { ... safetyCounter++; if (safetyCounter >= 3) { break; } }`**
`while (true)` means the condition is **always** true — this loop would genuinely never stop on its own. The only reason it terminates here is the `if (safetyCounter >= 3) { break; }` inside it, which manually forces an exit once the counter hits `3`. This is a deliberate, controlled infinite-loop pattern — safe **only because** a break condition exists inside it.

**The commented-out "mistake" example**
Shows what an **accidental** infinite loop looks like: a `while (mistake <= 5)` loop that never increments `mistake` inside its body. Since the condition never becomes `false`, this would run forever if actually executed — left commented out specifically so it doesn't crash the program when run.

---

### SECTION 9: Labeled Loops

**`outerLoop:` (the label, placed directly before the outer `for` loop)**
Gives this specific loop a name (`outerLoop`) so it can be referenced directly from inside a nested loop.

**`for (int i = 1; i <= 3; i++) { for (int j = 1; j <= 3; j++) { if (i == 2 && j == 2) { break outerLoop; } ... } }`**
Normally, a plain `break` inside the inner loop would only stop the **inner** loop, and the outer loop would continue on to its next iteration. But `break outerLoop;` specifically targets the labeled outer loop, exiting **both** loops entirely the moment `i == 2 && j == 2` becomes true.

**The comment explaining the contrast**
Clarifies that without the label, a plain `break` here would only kill the inner loop — the outer loop would still continue running all the way to `i = 3`.

---

### SECTION 10: Choosing the Right Loop
No code here — just a decision guide summarizing when each loop type fits best: `for` for known iteration counts, `while` for condition-based repetition of unknown length, `do-while` when the body must run at least once regardless, and `for-each` for simply walking through every element of an array or collection.

## Key Rules / Gotchas Recap

- `for` bundles initialization, condition, and update into one line; `while` and `do-while` require the update to be written manually inside the body
- `do-while` guarantees at least one execution, even if the condition is false from the start — the opposite of `while`, which may run zero times
- `break` exits the loop entirely; `continue` only skips the current iteration and moves on
- For-each loops give you the value directly, but no index — use a regular indexed `for` loop if you need to track position
- An intentional `while (true)` infinite loop is only safe because of a `break` condition inside it; forgetting to update a loop's condition variable is the most common cause of an *accidental* infinite loop
- A labeled `break` (e.g., `break outerLoop;`) is required to exit an outer loop from inside a nested one — a plain `break` only ever affects the innermost loop

## Why This Structure Exists

Loops are how a program processes collections, repeats calculations, or waits for a condition to change — nearly everything from array traversal to real-world data processing depends on choosing the right loop type and controlling it correctly with `break`/`continue`.