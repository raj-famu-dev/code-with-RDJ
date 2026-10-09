# `_2_VariablesAndDataTypes.java`

## Concept
Declaring variables and Java's 8 primitive data types — the basic containers every program uses to store information.

## ⚠️ A Note on This File's `main` Method

```java
static void main() {
```

This is **not** the traditional entry point signature. The standard, universally-required form is:
```java
public static void main(String[] args)
```

This file's version omits `public` and `(String[] args)`. Newer Java versions (21+ preview features) allow a simplified no-argument `main()` for quick single-file programs, but this only works with matching compiler flags/versions and isn't the standard, portable entry point. **Recommendation:** switch this back to the full standard signature to avoid confusion or compatibility issues:
```java
public static void main(String[] args) {
```

## Full Line-by-Line Breakdown

### `public class _2_VariablesAndDataTypes{`
Declares the class. Must match the filename exactly. `public` means accessible from anywhere.

---

### SECTION 1: Primitive Data Types

**`byte myByte = 100;`**
8-bit integer, range -128 to 127. Smallest whole-number type.

**`short myShort = 30000;`**
16-bit integer, range -32,768 to 32,767. Rarely used in practice — `int` is the default.

**`int myInt = 2_000_000;`**
32-bit integer, the standard whole-number type. Underscores are just visual separators — ignored by the compiler.

**`long myLong = 15000000000L;`**
64-bit integer for numbers too big for `int`. The `L` suffix is **mandatory** — without it, Java assumes `int` and errors on overly large values.

**`System.out.println("byte: " + myByte);`** (and the 3 lines after it)
Prints each variable's value, using `+` to concatenate the label text with the variable's value (auto-converted to String).

**`float myFloat = 5.75f;`**
32-bit decimal. The `f` suffix is **mandatory** — without it, Java assumes `double`.

**`double myDouble = 19.99;`**
64-bit decimal, more precise than `float`. The **default** choice for decimals — no suffix needed.

**`char myChar = 'A';`**
A single character, single quotes only. Internally stored as a Unicode number.

**`char myCharFromNumber = 66;`**
Proves a `char` is really just a number underneath — 66 is the Unicode value for `'B'`. Assigning an `int` literal directly to a `char` works as long as it's a valid character code.

**`boolean isJavaFun = true;` / `boolean isLearningDone = false;`**
Only two possible values: `true` or `false`.

---

### SECTION 2: String (Non-Primitive Reference Type)

**`String myName = "RDJ";`**
Not a primitive — an object. Double quotes (not single, which are for `char`).

**`String greeting = "Hello, " + myName + "!";`**
`+` here means **concatenation** (joining text), not addition.

**`greeting.length()`**
A method call on the String object — returns the number of characters it contains.

**`greeting.toUpperCase()`**
Returns a **new** String with all characters uppercase — does NOT modify `greeting` itself, since Strings are immutable (every "change" creates a new object).

---

### SECTION 3: Type Casting

**`int intValue = 100;` → `double widenedToDouble = intValue;`**
**Implicit/widening cast** — smaller type (`int`) automatically fits into a larger type (`double`). No data lost, no special syntax needed.

**`double doubleValue = 9.78;` → `int narrowedToInt = (int) doubleValue;`**
**Explicit/narrowing cast** — the `(int)` in front forces the conversion. The decimal is **truncated**, not rounded: `9.78` becomes `9`, not `10`.

**`int numberForChar = 65;` → `char resultChar = (char) numberForChar;`**
Converts a number back into its corresponding Unicode character — `65` becomes `'A'`.

---

### SECTION 4: Constants

**`final double PI = 3.14159;` / `final int MAX_USERS = 100;`**
`final` locks the variable — once assigned, it can never be reassigned. Attempting `PI = 3.14;` afterward would be a compile error. Named in ALL_CAPS by convention to visually signal "this never changes."

---

### SECTION 5: `var` — Type Inference

**`var inferredInt = 42;`**
Compiler looks at the value (`42`) and infers the type is `int` — you never wrote `int` yourself, but it's still fully type-checked afterward as if you had.

**`var inferredString = "Auto-typed";`**
Compiler infers `String` from the quoted value.

**`var inferredDouble = 3.14;`**
Compiler infers `double` from the decimal value.

**Important:** `var` is not a "loose" or untyped variable — it's still strongly typed, just with the compiler doing the typing for you based on what's immediately assigned.

---

### SECTION 6: Variable Naming Rules & Conventions

**Rules (enforced by the compiler):**
- Can contain letters, digits, underscore (`_`), dollar sign (`$`)
- Cannot start with a digit
- Cannot be a reserved keyword (`class`, `int`, `public`, etc.)
- Case-sensitive — `age` and `Age` are two different variables

**Conventions (best practice, not enforced):**
- `camelCase` for variables/methods — e.g., `firstName`, `totalAmount`
- `PascalCase` for class names — e.g., `VariablesAndDataTypes`
- `ALL_CAPS` for constants — e.g., `MAX_USERS`, `PI`

**`int studentAge = 21;`**
A practical example following the camelCase convention correctly.

## Key Rules / Gotchas Recap

- `float`/`long` need their suffix (`f`/`L`), or the compiler assumes `double`/`int`
- Narrowing casts truncate decimals — they don't round
- Local variables (like all of these) have **no default value** — they must be initialized before use, unlike object fields which default to `0`/`false`/`null` automatically

## Why This Structure Exists

Java is **statically typed** — every variable's type is fixed at declaration and checked at compile time, catching type errors before the program ever runs.