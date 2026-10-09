# `_8_Strings.java`

## Concept
String immutability, String Pool behavior, and the full range of common String methods — plus StringBuilder for efficient mutable string building.

## Full Line-by-Line Breakdown

### `public class _8_Strings {`
Declares the class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is A String?
No executable code beyond two declarations — just the conceptual framing:

**`String greeting = "Hello";` / `String name = "RDJ";`**
Two basic String variables, used later in Section 3. The comments establish the core fact this entire file builds on: a String is an **object** (reference type), not a primitive, and it's **immutable** — its content can never change after creation.

---

### SECTION 2: Creating Strings

**`String str1 = "Java";`**
A **String literal**. Java stores literals in a special memory area called the **String Pool** — if another literal with identical text already exists there, Java reuses it instead of creating a new object.

**`String str2 = new String("Java");`**
Using `new` **forces** the creation of a genuinely new object in regular memory, bypassing the String Pool entirely — even though the text is identical to `str1`.

**`str1 == str2`**
Since `==` compares **references** (memory addresses) for objects, not content, this returns `false` — `str1` points to the pooled literal, `str2` points to a separate object, even though both contain `"Java"`.

**`str1.equals(str2)`**
Returns `true` — `.equals()` compares actual **content**, correctly recognizing both Strings hold the same text regardless of where they live in memory. This is why `.equals()` should always be used for String comparison, never `==`.

---

### SECTION 3: String Concatenation

**`String fullGreeting = greeting + ", " + name + "!";`**
Joins multiple Strings together using `+`. Produces `"Hello, RDJ!"`.

**`String message = "Java"; message += " is"; message += " powerful";`**
Each `+=` appends more text. Important: since Strings are immutable, each `+=` doesn't actually modify the original — it creates a **new** String and reassigns `message` to point to it.

**`int age = 25; String combined = "Age: " + age;`**
Concatenating a String with an `int` automatically converts the number into text — `combined` becomes `"Age: 25"`.

---

### SECTION 4: String Immutability

**`String original = "Hello";`**
The starting String.

**`String modified = original.concat(" World");`**
`.concat()` does **not** change `original` — it returns a **brand-new** String (`"Hello World"`) and stores it in `modified`.

**The two `println` lines**
Prove the point directly: `original` still prints `"Hello"` (completely unchanged), while `modified` holds the new combined text. This is the core mechanic behind every "String modification" — nothing ever mutates in place.

---

### SECTION 5: Common String Methods

**`String sample = "  Java Programming  ";`**
A String with extra whitespace on both ends, used to demonstrate several methods.

**`sample.length()`**
Returns the total character count, **including** the leading/trailing spaces.

**`sample.trim()`**
Returns a new String with leading and trailing whitespace removed (but not whitespace in the *middle*, like the space between "Java" and "Programming").

**`sample.trim().toUpperCase()`**
Method chaining — first trims, then converts the trimmed result to uppercase. Since Strings are immutable, chaining like this works by passing each method's returned new String into the next method call.

**`sample.trim().toLowerCase()`**
Same idea, converting to lowercase instead.

**`word.charAt(0)` / `word.charAt(3)`**
Returns the single character at a given index. For `"Java"`: index `0` is `'J'`, index `3` is `'a'` (the last letter).

**`sentence.indexOf("Java")`**
Returns the position where `"Java"` **starts** within the sentence. For `"I love Java programming"`, that's index `7`.

**`sentence.indexOf("Python")`**
Returns `-1` because `"Python"` doesn't exist anywhere in the sentence — `-1` is the universal "not found" signal for this method.

**`sentence.substring(7)`**
Extracts everything from index `7` to the **end** of the String: `"Java programming"`.

**`sentence.substring(7, 11)`**
Extracts characters from index `7` up to (but **not including**) index `11` — the end index is **exclusive**. This gives characters at positions 7, 8, 9, 10 only, producing `"Java"`.

**`sentence.replace("Java", "Python")`**
Returns a new String with every occurrence of `"Java"` swapped for `"Python"` — the original `sentence` remains unchanged (immutability again).

**`sentence.contains("love")`**
Returns `true` or `false` depending on whether the substring exists anywhere inside the String.

**`"JAVA".equals("java")`**
Returns `false` — `.equals()` is case-sensitive by default.

**`"JAVA".equalsIgnoreCase("java")`**
Returns `true` — this variant ignores letter casing entirely.

**`sentence.startsWith("I")` / `sentence.endsWith("programming")`**
Check whether the String begins or ends with the given text — both return `true` here.

**`emptyStr.isEmpty()`** (where `emptyStr = ""`)
Returns `true` — the String has zero characters.

**`blankStr.isBlank()`** (where `blankStr = "   "`)
Returns `true` — `.isBlank()` considers whitespace-only Strings as "blank," even though they technically contain characters.

**`blankStr.isEmpty()`**
Returns `false` — `.isEmpty()` only checks for **zero length**, and `blankStr` actually has 3 space characters in it, so it's not truly empty, just visually blank.

---

### SECTION 6: Splitting and Joining Strings

**`String csvData = "Alice,Bob,Charlie,Dave"; String[] namesArray = csvData.split(",");`**
`.split(",")` breaks the String apart wherever a comma appears, returning an **array** of the resulting pieces: `["Alice", "Bob", "Charlie", "Dave"]`.

**`for (String n : namesArray) { System.out.println("- " + n); }`**
A for-each loop printing each extracted name with a `"- "` prefix.

**`String[] words = {"Java", "is", "fun"}; String joined = String.join(" ", words);`**
`String.join(" ", words)` does the **opposite** of split — it combines every element of the array into one String, inserting `" "` (a space) between each element. Result: `"Java is fun"`.

---

### SECTION 7: StringBuilder

**`StringBuilder sb = new StringBuilder();`**
Creates a **mutable** String-like object — unlike regular Strings, a `StringBuilder` can be changed in place without creating a new object every time.

**`for (int i = 1; i <= 5; i++) { sb.append("Number").append(i).append(" "); }`**
`.append()` adds text onto the end of the existing content, and — unlike regular String concatenation — this doesn't create 5 separate throwaway String objects; it modifies the same `StringBuilder` object directly each time, which is far more efficient inside loops.

**`sb.toString()`**
Converts the finished `StringBuilder` back into a regular `String` for printing/use elsewhere.

**`StringBuilder sb2 = new StringBuilder("Hello"); sb2.append(" World");`**
Starts with `"Hello"`, appends `" World"` → becomes `"Hello World"`.

**`sb2.insert(5, ",");`**
Inserts a comma at position `5` (right after "Hello") → becomes `"Hello, World"`.

**`sb2.reverse();`**
Reverses the entire character sequence in place → becomes `"dlroW ,olleH"`.

---

### SECTION 8: Comparing Strings Properly

**`String password1 = "secret123";` / `String password2 = "secret123";`**
Both are literals with identical text — Java's String Pool reuses the same object for both.

**`password1 == password2`**
Returns `true` — this is the **one case** where `==` happens to "work" for Strings, purely because both literals point to the exact same pooled object. This is exactly why relying on `==` is dangerous — it can accidentally seem correct sometimes.

**`String password3 = new String("secret123");`**
Forces a genuinely separate object, bypassing the pool.

**`password1 == password3`**
Returns `false` — even though the content is identical, they're now different objects in memory.

**`password1.equals(password3)`**
Returns `true` — the reliable, content-based comparison that should always be used instead of `==`.

---

### SECTION 9: Converting Between Strings and Other Types

**`int num = 100; String numStr = String.valueOf(num);`**
Converts an `int` into its String representation: `"100"`.

**`String numericInput = "250"; int parsedNum = Integer.parseInt(numericInput);`**
Converts a String containing digits back into an actual `int`: `250`.

## Key Rules / Gotchas Recap

- Never use `==` to compare String **content** — it compares object references, and can misleadingly "work" for literals due to String Pool reuse, while failing for `new String(...)` objects
- Strings are immutable — every method that seems to "modify" a String (`concat()`, `replace()`, `toUpperCase()`, etc.) actually returns a **new** String, leaving the original untouched
- `substring(start, end)` excludes the `end` index — a very common off-by-one mistake
- `isEmpty()` checks for zero length; `isBlank()` also treats whitespace-only content as effectively empty
- Use `StringBuilder` instead of repeated `+`/`+=` concatenation inside loops — far more efficient since it modifies one mutable object rather than creating many throwaway Strings

## Why This Structure Exists

Strings are everywhere in real programs, and understanding immutability (why "changing" a String actually creates a new one) has genuine performance implications — this is exactly why `StringBuilder` exists as the efficient alternative for heavy string-building work like loops.