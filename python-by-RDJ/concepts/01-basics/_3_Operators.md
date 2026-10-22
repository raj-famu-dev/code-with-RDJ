# `_3_Operators.py`

## Concept
Arithmetic, logical, membership, and identity operators — including several operator categories (membership, identity) that have no Java equivalent at all.

## The Full Code

```python
a = 15
b = 4

print("a + b =", a + b)
print("a - b =", a - b)
print("a * b =", a * b)
print("a / b =", a / b)
print("a % b =", a % b)
print("15 / 4 =", 15 / 4)
print("8 / 2 =", 8 / 2)
print("a // b =", a // b)
print("15 // 4 =", 15 // 4)
print("-15 // 4 =", -15 // 4)
print("a ** 2 =", a ** 2)

x = 10
x += 1
x -= 1

num = 10
num += 5
num -= 3
num *= 2
num /= 4
num //= 2
num **= 2

p = 10
q = 20
print("p == q:", p == q)
print("1 < p < 15:", 1 < p < 15)

is_adult = True
has_id = False
print("is_adult and has_id:", is_adult and has_id)
print("is_adult or has_id:", is_adult or has_id)
print("not is_adult:", not is_adult)

bit1 = 5
bit2 = 3
print("bit1 & bit2:", bit1 & bit2)
print("bit1 | bit2:", bit1 | bit2)
print("bit1 ^ bit2:", bit1 ^ bit2)
print("~bit1:", ~bit1)
print("bit1 << 1:", bit1 << 1)
print("bit1 >> 1:", bit1 >> 1)

age = 20
result = "Adult" if age >= 18 else "Minor"

name = "RDJ"
print("'D' in name:", 'D' in name)
print("'Z' not in name:", 'Z' not in name)

list1 = [1, 2, 3]
list2 = [1, 2, 3]
list3 = list1
print("list1 == list2:", list1 == list2)
print("list1 is list2:", list1 is list2)
print("list1 is list3:", list1 is list3)
```

## Line-by-Line Breakdown

### `a / b` → `3.75`
**This is the single biggest difference in this whole file.** In Java, `int / int` truncates. In Python, `/` is "true division" — it **always** returns a float, regardless of whether both operands are integers, even when the result divides evenly (`8 / 2` gives `4.0`, not `4`).

### `a // b` → `3`
Floor division — the operator that gives Java-style truncated integer division. `//` is how you get Java's `/` behavior back.

### `-15 // 4` → `-4`
A genuine gotcha: floor division rounds **toward negative infinity**, not toward zero. Java's truncation (and Python's own `int()` conversion from Topic 4) rounds toward zero instead — meaning `//` and `int()` can disagree with each other on negative numbers.

### `a ** 2` → `225`
Python's built-in power operator — no `Math.pow()` needed.

### `x += 1` / `x -= 1`
Python's shorthand assignment operators work identically to Java's. But notice: **there is no `x++` or `x--` at all** — writing that is a flat syntax error in Python.

### `num //= 2` and `num **= 2`
Two shorthand assignment operators Java has no equivalent for at all, since Java lacks both `//` and `**` as operators in the first place.

### `1 < p < 15` → `True`
A **chained comparison** — Python evaluates this as "is `p` greater than 1 AND less than 15" in one expression. Java has no equivalent syntax at all; writing something similar in Java would be interpreted completely differently (or wouldn't compile).

### `is_adult and has_id`, `is_adult or has_id`, `not is_adult`
Python spells out its logical operators as words — `and`, `or`, `not` — instead of Java's symbols `&&`, `||`, `!`. Short-circuit behavior works identically otherwise.

### The bitwise section (`&`, `|`, `^`, `~`, `<<`, `>>`)
Identical symbols and identical behavior to Java — this is one of the few operator categories that transfers directly with no differences at all.

### `result = "Adult" if age >= 18 else "Minor"`
Python's ternary-style expression. Reads almost like English: `value_if_true if condition else value_if_false` — structurally reversed from Java's `condition ? value_if_true : value_if_false`.

### `'D' in name` → `True`
The **membership operator** — checks whether a value exists inside a sequence (string, list, etc.). This single keyword replaces what Java needs `.contains()` or `.indexOf() != -1` to accomplish, and it has no direct Java equivalent as an operator.

### `list1 is list2` → `False`, `list1 is list3` → `True`
The **identity operator** `is` — checks whether two variables point to the *exact same object* in memory, conceptually mirroring Java's `==` behavior on objects. Meanwhile `list1 == list2` is `True`, since `==` in Python checks **content**, not identity. This mirrors Java's `==` vs `.equals()` distinction, just using different keywords (`is` for reference, `==` for content).

## Key Differences From Java

| Concept | Java | Python |
|---|---|---|
| `/` on two ints | Truncates (integer division) | **Always** returns a float |
| Java-style truncated division | Just use `/` | Use `//` instead |
| Power | `Math.pow(a, 2)` | `a ** 2` |
| Increment/decrement | `x++`, `x--`, `++x`, `--x` | **Do not exist at all** — syntax error |
| Logical operators | `&&`, `\|\|`, `!` | `and`, `or`, `not` |
| Chained comparisons | Not supported as written | `1 < p < 15` works as one combined check |
| Ternary | `condition ? a : b` | `a if condition else b` |
| Membership check | `.contains()` / `.indexOf() != -1` | `in` / `not in` |
| Reference equality | `==` for objects | `is` / `is not` |
| Bitwise operators | `& \| ^ ~ << >>` | Identical symbols, identical behavior |

## Key Rules / Gotchas Recap

- `/` always returns a float; use `//` for integer-style division
- `//` floors toward negative infinity, while `int()` (from Topic 4) truncates toward zero — these two disagree on negative numbers
- `is` checks object identity (same memory location); `==` checks content — don't confuse the two, especially with mutable objects like lists

## Why This Structure Exists

Operators are the mechanical foundation beneath every condition and calculation a program performs. Python's choices here — words instead of symbols for logical operators, true division by default, membership/identity operators baked into the language — reflect a general design philosophy of favoring readability and explicitness over Java's more symbol-dense, C-derived syntax.