# `_11_OutputFormating.java`

## Concept
Formatted console output — `println`/`print`/`err`, `printf` format specifiers, decimal precision, field width/alignment, `String.format()`, escape sequences, text blocks, and comma-formatted numbers.

## Full Line-by-Line Breakdown

### `public class _11_OutputFormating {`
Declares the class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: The Three Basic Print Methods

**`System.out.println("This prints text AND moves to a new line after");`**
Prints the text, then automatically moves the cursor to the next line.

**`System.out.print("This prints text but stays on the SAME line... ");`**
Prints the text **without** moving to a new line afterward — whatever prints next continues right where this left off.

**`System.out.print("...so this continues right after it");`**
Because the previous line used `.print()` (not `.println()`), this text appears immediately after it, on the same line.

**`System.out.println();` (empty)**
Called with no arguments — its only job is to move the cursor to the next line, since the two `.print()` calls above never did that themselves.

**`System.err.println("This prints to the ERROR stream...");`**
`System.err` is a **separate output stream** from `System.out`, specifically meant for error messages. Most IDEs (including IntelliJ) display `System.err` output in red, visually distinguishing it from regular output — useful for making warnings/errors stand out during debugging.

---

### SECTION 2: printf — Formatted Output

**`String name = "RDJ"; int age = 25; double salary = 55000.5;`**
Three variables to be inserted into a formatted string.

**`System.out.printf("Name: %s, Age: %d, Salary: %f%n", name, age, salary);`**
`printf` takes a **format string** containing placeholders, followed by the actual values to insert, in matching order:
| Placeholder | Meaning |
|---|---|
| `%s` | Insert a String value (here: `name`) |
| `%d` | Insert an integer value (here: `age`) |
| `%f` | Insert a floating-point value (here: `salary`) |
| `%n` | Insert a newline — the safer, OS-adaptive alternative to `\n` |

---

### SECTION 3: Common Format Specifiers

**`System.out.printf("String: %s%n", "Hello");`**
Demonstrates `%s` in isolation — inserts the String `"Hello"`.

**`System.out.printf("Integer: %d%n", 42);`**
Demonstrates `%d` — inserts the integer `42`.

**`System.out.printf("Float/Double: %f%n", 3.14159);`**
Demonstrates `%f` — inserts the decimal `3.14159`, though note it will show extra default decimal places (see Section 4).

**`System.out.printf("Character: %c%n", 'A');`**
`%c` — inserts a single character.

**`System.out.printf("Boolean: %b%n", true);`**
`%b` — inserts a boolean value as the text `true` or `false`.

**`System.out.printf("Percent literal: 100%%%n");`**
Since `%` normally starts a format specifier, printing an **actual** percent sign requires escaping it as `%%` — this prints `"Percent literal: 100%"`.

---

### SECTION 4: Controlling Decimal Precision

**`double pi = 3.14159265;`**
Value used throughout this section.

**`%f` (default)**
Shows **6 decimal places** by default, regardless of the original value's precision: `3.141593`.

**`%.2f`**
The number after the dot (`.2`) specifies exactly **2** digits after the decimal point: `3.14`.

**`%.4f`**
4 digits after the decimal: `3.1416` — note this **rounds** the value (the 5th digit was a `2`, so it rounds down here, but the key point emphasized is that it rounds rather than simply chopping off digits).

**`%.0f`**
0 digits after the decimal — effectively rounds to the nearest whole number: `3`.

---

### SECTION 5: Controlling Field Width (Alignment)

**`%10d`**
The `10` before `d` sets a **minimum width** of 10 characters for the output. Since `42` is only 2 digits, it gets padded with spaces on the **left** (right-aligned) to fill the remaining 8 characters: `[        42]`.

**`%-10d`**
The `-` **flips** the alignment to left-aligned instead — `42` appears first, followed by padding spaces to fill out to 10 characters: `[42        ]`.

**`%10s` / `%-10s`**
Same width and alignment rules, applied to a String (`"Hi"`) instead of a number — proving these formatting rules work identically across types.

---

### SECTION 6: Practical Example — Aligned Table Output

**`String[] items = {"Apple", "Bread", "Milk"}; double[] prices = {1.50, 3.25, 2.10};`**
Two parallel arrays representing a simple item list and their prices.

**`System.out.printf("%-10s %10s%n", "Item", "Price");`**
Prints a header row: `"Item"` left-aligned in a 10-character field, then `"Price"` right-aligned in another 10-character field — creating clean column headers.

**`System.out.printf("%-10s %10s%n", "----", "-----");`**
A visual divider row, using dashes in the same column widths as the header.

**`for (int i = 0; i < items.length; i++) { System.out.printf("%-10s %10.2f%n", items[i], prices[i]); }`**
Loops through both arrays together (using a shared index `i`), printing each item name (left-aligned) alongside its price (right-aligned, formatted to exactly 2 decimal places) — combining **width** and **precision** control together in one format string.

---

### SECTION 7: String.format()

**`String formattedMessage = String.format("Hello %s, you are %d years old.", name, age);`**
`String.format()` uses the **exact same** placeholder rules as `printf`, but instead of printing directly to the console, it **returns** the formatted result as a `String` — which is then stored in `formattedMessage` and printed separately afterward.

**`String receiptLine = String.format("%-15s $%8.2f", "Coffee", 4.5);`**
Another example combining width, a literal `$` character, and decimal precision, producing something like `"Coffee          $    4.50"` — useful for building formatted text you want to reuse, log, or send elsewhere rather than print immediately.

---

### SECTION 8: Escape Sequences

**`"Newline example:\nThis is on a new line"`**
`\n` forces a line break **inside** a single String, splitting the output across two lines even though it's one `println` call.

**`"Tab example:\tThis is tabbed over"`**
`\t` inserts a tab-width space, shifting the following text over.

**`"Quote example: \"This is in quotes\""`**
Since double quotes normally mark the start/end of a String, printing an **actual** quote character requires escaping it with `\"`.

**`"Backslash example: C:\\Users\\RDJ"`**
Since a single backslash normally starts an escape sequence, printing an **actual** backslash character requires writing two of them (`\\`), which Java interprets as one literal backslash.

**The comment about `\n` vs `%n`**
Clarifies that `\n` always means a plain line-feed character specifically, while `%n` (used earlier in `printf`) adapts to whatever the operating system's actual newline convention is — a distinction that matters more when writing to files across different operating systems than it does for simple console output.

---

### SECTION 9: Text Blocks (Java 15+)

**`String textBlock = """ ... """;`**
The triple-quote syntax marks a **text block** — a way to write multi-line String content directly, with real line breaks in the source code, instead of manually inserting `\n` at every line break.

**The `\\n` inside the text block's own content**
This is intentionally escaped as `\\n` so that it prints as the literal two characters `\` and `n` in the output (as an example within the text itself), rather than being interpreted as an actual line break.

---

### SECTION 10: Number Formatting With Commas

**`int largeNumber = 1234567; System.out.printf("With commas: %,d%n", largeNumber);`**
The comma (`,`) flag inside the format specifier (`%,d`) automatically inserts thousand-separator commas into the number: `1,234,567`.

**`double largeMoney = 9876543.21; System.out.printf("Money with commas: $%,.2f%n", largeMoney);`**
Combines the comma flag **and** decimal precision together in one specifier: `$9,876,543.21` — commas for readability, plus exactly 2 decimal places for currency formatting.

## Key Rules / Gotchas Recap

- `%.2f` **rounds**, it does not simply cut off extra digits
- A positive width number (`%10s`) right-aligns; a negative one (`%-10s`) left-aligns
- `%n` is the safer, OS-adaptive newline inside `printf`/`String.format`, versus `\n` which is always a plain line-feed
- `String.format()` behaves identically to `printf` but **returns** a String instead of printing directly — useful for storing or reusing formatted text
- Text blocks (`"""`) avoid needing manual `\n` characters for genuinely multi-line content

## Why This Structure Exists

Raw `println` concatenation becomes messy and error-prone once you need aligned columns, controlled decimal places, or large-number readability — `printf`-style formatting is the standard, precise way to control exactly how output looks, which becomes essential once you're building anything resembling a real report, receipt, or table of data.