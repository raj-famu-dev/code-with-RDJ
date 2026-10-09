# `_3_Operators.java`

## Concept
Arithmetic, unary, assignment, relational, logical, bitwise, and ternary operators — the mechanical layer beneath every calculation and decision a program makes.

## Full Line-by-Line Breakdown

### `public class _3_Operators {`
Declares the class. Must match the filename exactly.

### `public static void main(String[] args) {`
The standard, required entry point signature:
| Part | Meaning |
|---|---|
| `public` | JVM can call it from outside |
| `static` | Belongs to the class, no object needed to run it |
| `void` | Returns nothing |
| `main` | The exact name Java looks for to start the program |
| `(String[] args)` | Accepts command-line arguments (unused here, but required) |

---

### SECTION 1: Arithmetic Operators

**`int a = 15;` / `int b = 4;`**
Two integer variables used throughout this section.

**`a + b` → addition** → `19`

**`a - b` → subtraction** → `11`

**`a * b` → multiplication** → `60`

**`a / b` → division**
Since both `a` and `b` are `int`, this performs **integer division** — the decimal part is dropped entirely: `15 / 4` = `3`, not `3.75`.

**`a % b` → modulus**
Returns the **remainder** after division: `15 % 4` = `3` (since 4 goes into 15 three times, with 3 left over).

**`double preciseDivision = (double) a / b;`**
Casting `a` to `double` **before** the division forces the whole expression to compute as a decimal: `(double) 15 / 4` = `3.75`. Only one operand needs the cast — Java automatically promotes the other to match.

---

### SECTION 2: Unary Operators

**`int x = 10;`**
Starting value for this section.

**`-x` → negation**
Flips the sign: `10` becomes `-10`. Does not change `x` itself, just produces a negative value for that expression.

**`x++;` → post-increment**
Increases `x` by 1 (`x` becomes `11`). Used here as a standalone statement, so "post" vs "pre" doesn't matter yet — that distinction only shows up when used inline (see below).

**`x--;` → post-decrement**
Decreases `x` by 1 (`x` goes back to `10`).

**`int y = 5;`**
**`y++` used inline inside `println`:**
This is the critical distinction: `y++` returns the **current value first** (`5`), then increments `y` afterward. So the printed value is `5`, but `y` becomes `6` immediately after that line runs.

**`int z = 5;`**
**`++z` used inline inside `println`:**
This is the opposite: `++z` increments **first**, then returns the **new value**. So the printed value is `6` directly, and `z` is already `6` at that point.

---

### SECTION 3: Assignment Operators

**`int num = 10;`**
Starting value.

**`num += 5;`**
Shorthand for `num = num + 5;`. Result: `15`.

**`num -= 3;`**
Shorthand for `num = num - 3;`. Result: `12`.

**`num *= 2;`**
Shorthand for `num = num * 2;`. Result: `24`.

**`num /= 4;`**
Shorthand for `num = num / 4;`. Result: `6`.

**`num %= 4;`**
Shorthand for `num = num % 4;`. Result: `2` (remainder of `6 / 4`).

---

### SECTION 4: Relational (Comparison) Operators

**`int p = 10;` / `int q = 20;`**
Values being compared.

**`p == q`** — equal to → `false` (10 is not 20)

**`p != q`** — not equal to → `true`

**`p > q`** — greater than → `false`

**`p < q`** — less than → `true`

**`p >= q`** — greater than or equal to → `false`

**`p <= q`** — less than or equal to → `true`

Every relational operator always produces a `boolean` result — never a number.

---

### SECTION 5: Logical Operators

**`boolean isAdult = true;` / `boolean hasID = false;`**
Two boolean values to combine.

**`isAdult && hasID`** — AND → `false` (both must be `true`; `hasID` is `false`, so the whole thing fails)

**`isAdult || hasID`** — OR → `true` (only one needs to be `true`; `isAdult` already satisfies it)

**`!isAdult`** — NOT → `false` (flips `true` to `false`)

**Short-circuit behavior (explained in comments, not printed):**
- In `A && B`: if `A` is `false`, Java never even evaluates `B` — the result is already determined
- In `A || B`: if `A` is `true`, Java never evaluates `B` — same reasoning
  This matters for performance and for safely avoiding errors (e.g., checking `obj != null && obj.getValue() > 0` — the null check protects the second condition from crashing).

---

### SECTION 6: Bitwise Operators

**`int bit1 = 5;` (binary `0101`) / `int bit2 = 3;` (binary `0011`)**
Values shown in their binary form for clarity.

**`bit1 & bit2`** — bitwise AND → compares each bit position; both must be `1` to result in `1`. `0101 & 0011 = 0001` → `1`

**`bit1 | bit2`** — bitwise OR → either bit can be `1` to result in `1`. `0101 | 0011 = 0111` → `7`

**`bit1 ^ bit2`** — bitwise XOR → results in `1` only where bits *differ*. `0101 ^ 0011 = 0110` → `6`

**`~bit1`** — bitwise NOT → flips every bit, including the sign bit. Result: `-6` (due to how negative numbers are represented in binary)

**`bit1 << 1`** — left shift → shifts all bits one position left, effectively doubling the number: `5 << 1 = 10`

**`bit1 >> 1`** — right shift → shifts all bits one position right, effectively halving the number (dropping any remainder): `5 >> 1 = 2`

---

### SECTION 7: Ternary Operator

**`int age = 20;`**
Value being checked.

**`String result = (age >= 18) ? "Adult" : "Minor";`**
A compact one-line if-else:
| Part | Meaning |
|---|---|
| `(age >= 18)` | The condition being tested |
| `?` | "If true, use the next value" |
| `"Adult"` | Value used if the condition is `true` |
| `:` | "Otherwise, use this value instead" |
| `"Minor"` | Value used if the condition is `false` |

Since `age` is `20`, the condition is `true`, so `result` becomes `"Adult"`.

---

### SECTION 8: Operator Precedence

**`int precedenceTest = 10 + 5 * 2;`**
Java evaluates multiplication **before** addition (same as standard math rules), so this computes as `10 + (5 * 2)` = `10 + 10` = `20` — not `(10 + 5) * 2`.

**`int precedenceWithParens = (10 + 5) * 2;`**
Parentheses **override** the default order, forcing the addition to happen first: `15 * 2` = `30`.

**The full precedence order (highest to lowest), as listed in the comments:**
1. Parentheses `()`
2. Unary (`++`, `--`, `!`)
3. Multiplicative (`*`, `/`, `%`)
4. Additive (`+`, `-`)
5. Relational (`<`, `>`, `<=`, `>=`)
6. Equality (`==`, `!=`)
7. Logical AND (`&&`)
8. Logical OR (`||`)
9. Assignment (`=`, `+=`, `-=`, etc.)

## Key Rules / Gotchas Recap

- Integer division truncates — cast one operand to `double` first if you need a decimal result
- `y++` (post) uses the value *then* increments; `++z` (pre) increments *then* uses the value — this only matters when used inline
- `&&` and `||` short-circuit — the second operand may never even be evaluated
- Operator precedence follows a strict, math-like order; parentheses always override it

## Why This Structure Exists

Operators are the mechanical foundation beneath every `if` statement, loop condition, and calculation a program performs — nothing in later topics (control flow, loops, methods) works without this layer underneath it.