# `_3_OperatorsAndCasting.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
C++ operators look like Java's, but several behave in ways that surprise: integer division truncates, `%` keeps the sign of the dividend, and a single mistyped `&` for `&&` still compiles. Conversions between types happen silently unless you ask for them explicitly, so you need to know the named casts. `static_cast` is the safe, greppable one; the old C-style `(T)x` is a single syntax that can silently perform several different dangerous conversions.

## Full Line-by-Line Breakdown

### SECTION 1: ARITHMETIC AND INTEGER DIVISION
When both operands are integers, `/` discards the fractional part toward zero: `7 / 2` is 3 and `-7 / 2` is -3. `%` gives the remainder with the sign of the left operand, so `-7 % 2` is -1. The trap is `double wrong = a / b;`: the integer division happens FIRST, giving 3, and only then is the result converted to `double`. Cast one operand first (`static_cast<double>(a) / b`) to get 3.5.

Output from a real run:

```text
===== SECTION 1: ARITHMETIC AND INTEGER DIVISION =====
7 / 2 = 3 (integer division truncates toward zero)
-7 / 2 = -3, -7 % 2 = -1 (remainder takes the sign of the dividend)
7.0 / 2 = 3.5 (one double operand makes it floating point)
double wrong = a / b  -> 3
double right = static_cast<double>(a) / b -> 3.5
```

### SECTION 2: BITWISE, LOGICAL, SHORT-CIRCUIT
`|=` sets a bit, `&= ~mask` clears it, `^=` toggles it: starting from 5 the flags end as 140 (binary 10001100). `<<` and `>>` shift. `&&` and `||` short-circuit, so the right side of `false && noisy()` never runs (the counter stays 0). Bitwise `&` and logical `&&` are different operators: `6 & 3` is 2 but `6 && 3` is just `true`, printed as 1.

Output from a real run:

```text
===== SECTION 2: BITWISE, LOGICAL, SHORT-CIRCUIT =====
flags = 140 (binary 10001100)
1 << 4 = 16, 256 >> 3 = 32
short-circuit: calls = 0 (r1=0, r2=1)
& vs &&: 6 & 3 = 2 but 6 && 3 = 1
```

### SECTION 3: INCREMENT AND ASSIGNMENT
`i++` returns the old value, `++i` the new one: `post` is 5 and `pre` is 7. Compound assignments (`+=`, `*=` ...) chain as shown. The comment records an important rule: do not modify the same variable twice in one expression; keep each statement simple.

Output from a real run:

```text
===== SECTION 3: INCREMENT AND ASSIGNMENT =====
post = 5, pre = 7, i = 7
compound assignments end at x = 2
ternary = 100
```

### SECTION 4: static_cast VS THE C-STYLE CAST
`static_cast<int>(3.99)` truncates to 3 (it does not round) and `static_cast<uint8_t>(300)` wraps to 44. The reasons C-style casts are bad: (1) one syntax `(T)x` quietly picks `static_cast`, `const_cast` or `reinterpret_cast`, so a typo changes the meaning without any warning; (2) it can strip `const`, which is how people end up writing to read-only data; (3) it is nearly impossible to search for. The named casts are loud and each does one job: `static_cast` for sensible conversions, `const_cast` to remove const, `reinterpret_cast` to treat bytes as another type, `dynamic_cast` for checked downcasts. The last lines peek at the first byte of `0x01020304`: seeing 4 first proves this machine is little-endian.

Output from a real run:

```text
===== SECTION 4: static_cast VS THE C-STYLE CAST =====
static_cast<int>(3.99) = 3 (truncates, does not round)
static_cast<uint8_t>(300) = 44 (300 mod 256, defined for unsigned)
static_cast refuses to drop const; (int*)cp would compile silently. Locked is still 7
first byte of 0x01020304 in memory = 4 (4 on little-endian machines)
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `7 / 2` is 3, `-7 % 2` is -1 | Same results (C++11 and later define truncation toward zero) |
| `double d = 7 / 2;` gives 3.0 | Same trap: 3 |
| `int x = (int) 3.99;` cast syntax | `static_cast<int>(3.99)`; C-style `(int)3.99` also compiles but should be avoided |
| Casts between object types are checked at run time (`ClassCastException`) | `static_cast` between pointers is unchecked; `dynamic_cast` is the checked one |
| `>>>` unsigned shift | Shift of an unsigned value is logical, a signed `>>` is implementation-defined for negatives |
| `&&` short-circuit, `&` on booleans does not | Same, but `&` on `int` is bitwise and a typo compiles |
| Overflow wraps | Signed overflow is undefined behaviour |

## Key Rules / Gotchas Recap
- Integer division truncates toward zero; convert BEFORE dividing if you want a fraction.
- `%` has the sign of the dividend.
- `&&` and `||` short-circuit; `&` and `|` do not and are bitwise.
- `i++` yields the old value; `++i` yields the new one. Prefer `++i` when the value is unused.
- Use `static_cast`, not `(T)x`. It will not silently drop `const` or reinterpret bytes.
- `reinterpret_cast` is a last resort and the only reasonable target types for aliasing are `char`, `unsigned char` and `std::byte`.

## Why This Structure Exists
Careful casting and bit manipulation show up in parsers, network code, hashing, quantised AI model weights, and exploit-prevention work, where one wrong cast or shift is the difference between a safe program and a vulnerability. Named casts make those risky points visible in code review.
