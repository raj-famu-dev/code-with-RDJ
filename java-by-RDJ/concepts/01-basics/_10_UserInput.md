# `_10_UserInput.java`

## Concept
Reading input from the console via `Scanner` — Strings, numbers, booleans, the classic buffer bug, and safe input validation.

## Full Line-by-Line Breakdown

### `import java.util.Scanner;`
Imports the `Scanner` class from Java's built-in `util` package. Anything not automatically available (like `String` or `System`) must be explicitly imported before it can be used.

### `public class _10_UserInput {`
Declares the class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is Scanner?

**`Scanner scanner = new Scanner(System.in);`**
Creates a new `Scanner` object, named `scanner`. `System.in` represents **standard input** — normally, whatever the user types on the keyboard. This line "connects" the Scanner to the keyboard so it can start reading whatever is typed.

---

### SECTION 2: Reading a String (Full Line)

**`System.out.print("Enter your name: ");`**
Note `.print` (not `.println`) — keeps the cursor on the same line after the prompt, so the user types right after the colon rather than on a new line.

**`String userName = scanner.nextLine();`**
`.nextLine()` waits for the user to type something and press Enter, then captures **everything** typed — including spaces — as one String.

**`System.out.println("Hello, " + userName + "!");`**
Prints a greeting using whatever the user entered.

---

### SECTION 3: Reading a Single Word (No Spaces)

**`String language = scanner.next();`**
`.next()` reads only up to the **next whitespace character** — if the user typed "Java Script" (with a space), `.next()` would only capture `"Java"`, stopping right before the space. This is fundamentally different from `.nextLine()`.

---

### SECTION 4: Reading Numbers

**`int age = scanner.nextInt();`**
`.nextInt()` waits for and reads an integer value specifically. If the user types something that isn't a valid integer, this will cause a crash (covered later in Section 8/9's validation).

**`double height = scanner.nextDouble();`**
Same idea, but reads a decimal number instead.

---

### SECTION 5: Reading a Boolean

**`boolean isStudent = scanner.nextBoolean();`**
`.nextBoolean()` only accepts the literal text `true` or `false` (case-insensitive) — anything else (like `"yes"`) throws an `InputMismatchException` at runtime, since Scanner doesn't understand any other interpretation of a boolean.

---

### SECTION 6: The Classic nextInt() + nextLine() Bug

**`int number = scanner.nextInt();`**
Reads an integer. Here's the subtle problem: when the user types a number and presses Enter, `.nextInt()` only consumes the **number itself** — the newline character (created by pressing Enter) is left sitting in the input buffer, unread.

**`scanner.nextLine();` (the fix, called immediately after)**
This call exists purely to **consume that leftover newline** — it reads and discards the empty leftover, clearing the buffer so the *next* real `.nextLine()` call works correctly. Without this line, the following `.nextLine()` would immediately return an empty String instead of waiting for the user to type a new sentence.

**`String sentence = scanner.nextLine();`**
Now this call works as intended, since the buffer was already cleared by the fix line above it — it properly waits for and captures the user's actual sentence.

---

### SECTION 7: Reading Multiple Values on One Line

**`int num1 = scanner.nextInt(); int num2 = scanner.nextInt(); int num3 = scanner.nextInt();`**
Three separate `.nextInt()` calls in a row. If the user types three numbers separated by spaces on a single line (e.g., `"5 10 15"`), Scanner correctly reads them one at a time across these three calls — it doesn't require each number to be on its own line.

**`System.out.println("Sum: " + (num1 + num2 + num3));`**
Adds the three captured values together and prints the result.

---

### SECTION 8: Validating Input With hasNextInt()

**`scanner.nextLine();` (clearing the buffer again)**
Same buffer-clearing fix as Section 6 — necessary again here because the previous `.nextInt()` calls in Section 7 left another leftover newline behind.

**`if (scanner.hasNextInt()) { ... } else { ... }`**
`.hasNextInt()` **checks** whether the next piece of input waiting to be read is actually a valid integer, **without consuming it**. This lets you safely test before committing to `.nextInt()`, avoiding a crash if the input turns out to be invalid.

**Inside the `if`:** `int favoriteNumber = scanner.nextInt();`
Only runs `.nextInt()` if the check confirmed it's safe to do so.

**Inside the `else`:** `scanner.next();`
If the input wasn't a valid integer, this line **consumes** the invalid token anyway (using the general-purpose `.next()`), so it doesn't get stuck in the buffer and cause problems on a future read.

---

### SECTION 9: Closing the Scanner

**`scanner.close();`**
Releases the system resources the Scanner was using — good practice once you're completely done reading input, especially in larger programs that might open many resources.

**The warning comment**
Explains that once `.close()` is called, the Scanner can **never** be used again — any further `.nextLine()`, `.nextInt()`, etc. calls would throw an exception. This is why `.close()` should only be called at the very end, after all input reading is finished.

## Key Rules / Gotchas Recap

- `.nextLine()` reads a full line including spaces; `.next()` stops at the first whitespace
- `.nextInt()`/`.nextDouble()` leave a leftover newline character in the buffer — always follow them with an extra `.nextLine()` if you're about to read a full line next
- `.nextBoolean()` only accepts the literal words `true`/`false` — anything else crashes with `InputMismatchException`
- Always validate with `.hasNextInt()` (or similar) before calling `.nextInt()` if the input isn't guaranteed to be valid — this prevents an unhandled crash
- Never call any Scanner method after `.close()` — it permanently disables further reads

## Why This Structure Exists

Nearly every interactive program needs to read user input at some point — `Scanner` is the standard, built-in way to do this in plain Java, and understanding its buffer quirks (Section 6) and validation patterns (Section 8) prevents the exact kind of runtime crash that's extremely common for beginners to hit firsthand.