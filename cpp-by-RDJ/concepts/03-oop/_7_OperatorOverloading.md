# `_7_OperatorOverloading.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
C++ lets your own types use operators like `+`, `==`, `<`, `<<` and `[]` by writing functions named `operator+`, `operator==` and so on. Used well, `Money + Money` reads like math; used badly, it makes code puzzling.

C++20 adds the three-way comparison `<=>` (the "spaceship") so one function, or one `= default`, can generate `<`, `<=`, `>` and `>=`.

## Full Line-by-Line Breakdown

### SECTION 1: arithmetic and streaming
`Money` stores integer cents (never floating point for money). `operator+` is a const member returning a new value; `operator+=` modifies and returns `*this`; unary `operator-` has no parameter. `operator==` is `= default`, which compares members one by one, and C++20 gives `!=` for free. `operator<<` is a friend that writes to an `std::ostream&` and returns it so chaining works. While writing this file, the first version printed `-$19.99` as `$-19.0-99` because `%` and `/` of negative numbers were mishandled; the fix prints the sign first and uses the absolute value. The output below is from the fixed code.

Output from a real run:

```text
===== SECTION 1: arithmetic and streaming =====
a=$19.99 b=$5.01 total=$25.05 -a=-$19.99
Money(100) == Money(100): true, != works via == in C++20: true
```

### SECTION 2: comparison with <=>
`Version` writes `auto operator<=>(const Version&) const = default;`. The compiler compares `major`, then `minor`, then `patch` and generates all six comparisons, so `1.2.3 < 1.10.0` is true (numeric compare, not text) and `std::sort` works. A defaulted `<=>` also implicitly defaults `==`. `Parcel` demonstrates a custom rule: only whole kilograms matter. A hand-written `<=>` does NOT create `==`; you must write `==` yourself (the file does, and notes the trap).

Output from a real run:

```text
===== SECTION 2: comparison with <=> =====
1.2.3 < 1.10.0: true, 1.2.3 == 1.2.3: true
(v1 <=> v2) < 0: true (std::strong_ordering::less)
sorted: 1.9.9 1.10.0 2.0.0 
Parcel(1200g) == Parcel(1900g): true (same whole kg, by OUR rule)
Parcel(1900g) < Parcel(2100g): true
Trap: equality by a custom rule must be written yourself; == is not generated from a hand-written <=>.
```

### SECTION 3: operator[]
`Vec3` has two overloads of `operator[]`: one returns `double&` (writable) and the const overload returns `const double&`. Both use `.at()`, which throws `std::out_of_range` instead of reading past the end; the plain `vector::operator[]` does no bounds check and out-of-range access is undefined behaviour.

Output from a real run:

```text
===== SECTION 3: operator[] =====
v[0]=1 v[1]=20 cv[2]=3
v[3] threw std::out_of_range (we used at(), so no silent overflow)
```

### SECTION 4: explicit conversion
`explicit operator bool()` allows `if (on)` and `static_cast<bool>(off)` but blocks `on + 1` or passing it to an `int` parameter. `Celsius` has an IMPLICIT `operator double()` as the cautionary example: it converts silently anywhere, so arithmetic and comparisons with unrelated values compile. The final lines list the rules for when NOT to overload.

Output from a real run:

```text
===== SECTION 4: explicit conversion =====
if (on) works: explicit operator bool is allowed in conditions
off as bool: false
int n = on + 1; would not compile (explicit stops silent arithmetic)
Celsius silently converted to double: 36.6 (convenient, but it also lets t + 5 and t < 'x' compile)

Rules for when NOT to overload:
  - only when the meaning is obvious (Money + Money, not Employee + Employee)
  - never overload &&, ||, or , (comma): you lose short-circuit/ordering guarantees
  - keep == and < consistent with each other; keep symmetric ones as non-members/friends
  - prefer `explicit` conversions; prefer a named function when an operator would surprise a reader
```

## Key Differences From Java
| Java | C++ |
|---|---|
| No operator overloading (only `+` for String) | Most operators can be overloaded |
| `equals(Object)` + `hashCode()` | `operator==` (and a hash functor for unordered containers; see file 7 in the STL folder) |
| `Comparable<T>.compareTo` | `operator<=>` (C++20), or `operator<` |
| `toString()` | `operator<<(std::ostream&, const T&)` |
| `list.get(i)` | `operator[]` |
| `if (obj != null)` / no truthiness | `explicit operator bool()` |
| Strings compare by `equals`; `==` is reference equality | `==` compares VALUES for types that define it |

## Key Rules / Gotchas Recap
- Overload only when the meaning is obvious; otherwise name a function.
- Do not overload `&&`, `||`, `,` (you lose short-circuit or evaluation order guarantees).
- Keep `==`, `<`, and hashing consistent with each other.
- Mark conversion operators `explicit`.
- A hand-written `<=>` does not provide `==`; defaulted `<=>` does.
- Provide `const` and non-const `operator[]`.
- Stream operators are non-member (usually friend) because the stream is on the left.

## Why This Structure Exists
Numeric and tensor libraries (and fixed-width integer types in security code) rely on operators so formulas read naturally. Correct comparisons are also needed for ordered containers and sorting, which the STL folder builds on.
