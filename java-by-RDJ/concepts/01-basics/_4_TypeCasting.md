# `_4_TypeCasting.java`

## Concept
Converting values between data types — implicit (automatic) widening and explicit (manual) narrowing — plus the real-world gotchas that come with data loss.

## Full Line-by-Line Breakdown

### `public class _4_TypeCasting {`
Declares the class. Must match the filename exactly.

### `public static void main(String[] args) {`
Standard entry point signature — required for the JVM to start the program.

---

### SECTION 1: What Is Type Casting?
No code here — just the conceptual framing: casting means converting a value from one data type to another, split into two categories — **implicit** (automatic, safe) and **explicit** (manual, risky).

---

### SECTION 2: Implicit Casting (Widening)

**`byte byteValue = 10;`**
Starting value — smallest integer type.

**`short shortValue = byteValue;`**
`byte` automatically fits into `short` — no data lost, no cast syntax needed, since `short` can hold every value `byte` can and more.

**`int intValue = shortValue;`**
Same automatic widening — `short` fits into `int`.

**`long longValue = intValue;`**
`int` fits into `long` — still automatic.

**`float floatValue = longValue;`**
`long` fits into `float` — automatic, even though `float` is technically less precise for very large numbers (a subtle trade-off, but Java allows it without a cast).

**`double doubleValue = floatValue;`**
`float` fits into `double` — automatic, completing the full widening chain.

**The six `println` lines**
Print each value at every stage of the chain, proving the value passed through unchanged the whole way.

**`char letterGrade = 'A';`**
A character value.

**`int charToInt = letterGrade;`**
Widening a `char` into an `int` — no cast needed, since `char` is really just a 16-bit number underneath. `'A'` becomes `65` (its Unicode value).

---

### SECTION 3: Explicit Casting (Narrowing)

**`double bigDouble = 99.99;`**
Starting value — the largest type in this chain.

**`float narrowedFloat = (float) bigDouble;`**
The `(float)` in front is the **explicit cast syntax** — required because going from a larger type to a smaller one risks losing data, so Java forces you to confirm you mean it.

**`long narrowedLong = (long) narrowedFloat;`**
Casting `float` down to `long`. Since `float` had a decimal (`99.99`), converting to `long` (a whole-number type) **truncates** the decimal — it becomes `99`, not rounded to `100`.

**`int narrowedInt = (int) narrowedLong;`**
Continues narrowing — `long` to `int`. Value stays `99` since it already fits within `int`'s range.

**`short narrowedShort = (short) narrowedInt;`**
`int` to `short` — still `99`, well within `short`'s range.

**`byte narrowedByte = (byte) narrowedShort;`**
`short` to `byte` — still `99`, since `byte`'s max is `127` and `99` fits comfortably.

**The six `println` lines**
Print each stage, showing the value stayed `99` throughout (only the decimal was lost at the very first narrowing step, from `float` to `long`).

---

### SECTION 4: Data Loss Examples (Key Gotchas)

**`double price = 9.99;` → `int truncatedPrice = (int) price;`**
Casting truncates — it does **not** round. `9.99` becomes `9`, not `10`, because the decimal portion is simply cut off, not evaluated for rounding.

**`int largeNumber = 130;` → `byte overflowedByte = (byte) largeNumber;`**
`byte`'s range is only `-128` to `127`. `130` doesn't fit, so instead of erroring, Java **wraps around** — the result becomes `-126`. This happens silently, with no warning or exception, making it a classic hidden-bug source.

**`int negativeNumber = -200;` → `byte negativeOverflow = (byte) negativeNumber;`**
Same wraparound behavior, but starting from a negative number — demonstrates that overflow isn't just a "too big" problem, it applies to out-of-range values in either direction.

---

### SECTION 5: Casting Between `int` and `char`

**`int numberCode = 97;` → `char resultChar = (char) numberCode;`**
Explicit cast from `int` to `char` — required because this is a narrowing conversion (an `int` can represent far more values than a `char` can). `97` becomes `'a'` (its Unicode character).

**`char sourceChar = 'z';` → `int resultInt = sourceChar;`**
No cast needed here — `char` to `int` is a **widening** conversion (going from a smaller-range type to a larger one), so it's automatic. `'z'` becomes `122`.

---

### SECTION 6: String Conversions (Not True Casting)

**`int number = 42;` → `String numberAsString = String.valueOf(number);`**
Strings can't be cast like primitives — `(String) number` wouldn't work. Instead, you use a conversion **method**. `String.valueOf(...)` is the preferred, clean way to turn a number into text.

**`String numberAsString2 = "" + number;`**
An alternative approach — concatenating an empty string with a number forces Java to convert it to a String automatically. Works, but considered less clean/explicit than `String.valueOf()`.

**`String numericText = "123";` → `int parsedInt = Integer.parseInt(numericText);`**
Converts a String **containing digits** into an actual `int`. `Integer.parseInt()` is the standard method for this.

**`double parsedDouble = Double.parseDouble("45.67");`**
Same idea, but for decimal values — converts a numeric-looking String into an actual `double`.

**The comment about `NumberFormatException`**
Warns that `Integer.parseInt("abc")` would crash the program at runtime, since `"abc"` isn't a valid number — parsing is not silently forgiving like some other conversions.

---

### SECTION 7: Mixed-Type Arithmetic (Automatic Promotion)

**`int intNum = 10;` / `double doubleNum = 3.5;`**
Two different types being combined.

**`double mixedResult = intNum + doubleNum;`**
When an `int` and a `double` are used together in one expression, Java automatically **promotes** the `int` to a `double` *before* doing the math — so `10` briefly becomes `10.0`, and the result is `13.5`. No manual cast needed here since it's happening between two different types already, not a narrowing situation.

**`int a = 7;` / `int b = 2;`**
Two integers, both the same type.

**`a / b`**
Since both are `int`, this is **integer division** — `7 / 2` gives `3`, dropping the remainder entirely (no automatic promotion happens here, because both operands are already the same type).

**`(double) a / b`**
Casting just `a` to `double` before the division forces the whole expression to compute with decimal precision: `3.5`.

---

### SECTION 8: When to Use Explicit Casting (Real Use Cases)

**`int totalScore = 270;` / `int totalStudents = 8;`**
Two whole numbers representing a total and a count.

**`double average = (double) totalScore / totalStudents;`**
A genuinely practical use of casting — without the `(double)`, this would perform integer division and silently produce a wrong, truncated average. Casting one operand first ensures accurate decimal results.

**`double calculatedIndex = 3.9;` → `int actualIndex = (int) calculatedIndex;`**
Array and list indices in Java must be whole numbers (`int`) — never decimals. Casting truncates `3.9` down to `3`, which is a safe, valid index. This is a real pattern you'll see constantly once arrays/collections are involved.

## Key Rules / Gotchas Recap

- Widening (small → large) is automatic; narrowing (large → small) requires an explicit `(type)` cast
- Casting **truncates** decimals, it does **not** round
- Narrowing a number outside a type's valid range causes silent **overflow/wraparound**, not an error — this is a genuinely dangerous, hard-to-spot bug source
- `char` and `int` convert into each other through their shared Unicode number representation
- Strings require conversion **methods** (`String.valueOf()`, `Integer.parseInt()`), not cast syntax
- Mixed-type arithmetic between *different* types auto-promotes the smaller one; but two `int`s dividing each other still does integer division regardless

## Why This Structure Exists

Java refuses to silently convert between incompatible types unless explicitly told to — this design choice prevents accidental, invisible data loss, but it means you need to understand exactly which conversions are safe (automatic) versus which ones carry real risk (manual, and your responsibility to verify).