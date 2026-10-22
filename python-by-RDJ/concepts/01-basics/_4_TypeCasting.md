# `_4_TypeCasting.py`

## Concept
Type conversion using explicit functions instead of Java's `(type)` cast syntax — plus Python's unique "truthiness" rules and the complete absence of integer overflow.

## The Full Code

```python
whole_number = 10
decimal_number = 3.5
mixed_result = whole_number + decimal_number
print(type(mixed_result))

price = 9.99
truncated_price = int(price)

whole = 100
as_float = float(whole)

numeric_text = "123"
parsed_int = int(numeric_text)

numeric_decimal_text = "45.67"
parsed_float = float(numeric_decimal_text)

number = 42
number_as_string = str(number)

print(int(9.99))
print(int(-9.99))
print(-15 // 4)

print(bool(0))
print(bool(1))
print(bool(-5))
print(bool(''))
print(bool('hello'))
print(bool(None))

huge_number = 99999999999999999999999999999999999999
print(type(huge_number))

letter = 'A'
unicode_value = ord(letter)
back_to_char = chr(65)

age = 25
print(f"Age is {age}")
```

## Line-by-Line Breakdown

### `mixed_result = whole_number + decimal_number`
This is the **one** automatic conversion Python performs: when an `int` and a `float` are combined in an expression, Python automatically promotes the `int` to a `float` first. This mirrors Java's automatic numeric promotion — the only place Python's conversion behavior resembles Java's "implicit widening" concept at all.

### `truncated_price = int(price)`
`int()` on a float **truncates** — cuts off the decimal entirely, same rule as Java's `(int)` cast. `int(9.99)` gives `9`, not `10`.

### `parsed_int = int(numeric_text)` / `parsed_float = float(numeric_decimal_text)`
These are **functions**, not cast operators — this replaces Java's `(int)`/`(double)` syntax entirely for converting values of one type into another. There's no symbolic cast syntax in Python at all; every conversion is an explicit function call.

### `number_as_string = str(number)`
Converts a number into its string representation — same purpose as Java's `String.valueOf()`.

### `int(-9.99)` → `-9`
Confirms `int()` truncates **toward zero**, even for negatives.

### `-15 // 4` → `-4`
Shown again here deliberately, next to `int(-9.99)`, to highlight the inconsistency: `int()` truncates toward zero, but `//` (floor division, from Topic 3) rounds toward negative infinity. These two mechanisms disagree with each other for negative numbers — a genuine Python-specific gotcha worth remembering.

### `bool(0)`, `bool('')`, `bool(None)` → all `False`
### `bool(-5)`, `bool('hello')` → both `True`
This is Python's **"truthiness"** concept, which Java has no equivalent for at all. `bool()` can convert almost any value into a boolean, following consistent rules: zero, empty strings, and `None` are "falsy"; nearly everything else (including negative numbers!) is "truthy." This concept becomes especially relevant in control flow, where Python lets you write `if some_string:` directly instead of Java's `if (someString != null && !someString.isEmpty())`.

### `huge_number = 99999999999999999999999999999999999999`
This number is far larger than Java's `long` could ever hold without using `BigInteger`. Python handles it with zero special handling — `type(huge_number)` still just reports `<class 'int'>`. **Python integers have no fixed size and cannot overflow** — an entire category of Java bugs (byte/int wraparound) simply doesn't exist here.

### `ord(letter)` → `65` / `chr(65)` → `'A'`
Since Python has **no separate `char` type** (a single character is just a string of length 1), these two functions replace Java's `(int) someChar` and `(char) someInt` casts respectively. `ord()` gets a character's Unicode code point; `chr()` does the reverse.

### `print(f"Age is {age}")`
A preview of f-strings (fully covered in Topic 11): inside an f-string, any value is automatically converted to its string form for display — no `str()` call needed, unlike regular `+` concatenation.

## Key Differences From Java

| Concept | Java | Python |
|---|---|---|
| Cast syntax | `(int) someDouble` | `int(some_float)` — function call |
| Widening/narrowing distinction | Explicit, enforced categories | Mostly irrelevant — only int+float mixing auto-converts |
| Integer overflow | Silent wraparound on narrowing | **Does not exist** — ints have no fixed size |
| Invalid string conversion | `NumberFormatException` | `ValueError` |
| Boolean conversion | Only `true`/`false` exist | `bool()` works on nearly anything — "truthiness" |
| `char` type | Separate type, castable | No `char` type — use `ord()`/`chr()` |
| Rounding direction for negatives | `(int)` and `/` agree (toward zero) | `int()` truncates toward zero, but `//` floors toward negative infinity — **they disagree** |

## Key Rules / Gotchas Recap

- `int()` truncates, never rounds — same rule as Java's `(int)` cast
- Python integers cannot overflow — this removes a whole class of Java bugs, but also removes the early warning signal that "this number got too big"
- `int()` and `//` round negative numbers in **opposite directions** from each other — a subtle, real source of bugs if unnoticed

## Why This Structure Exists

Python replaces Java's cast-operator syntax with explicit function calls for every conversion, since there's no compiler to enforce type rules ahead of time — conversions must be deliberate and visible in the code itself. The "truthiness" system and unlimited-size integers both reflect a broader Python design preference: fewer rigid rules, more flexibility, at the cost of losing some of the early-warning safety Java's stricter type system provides.