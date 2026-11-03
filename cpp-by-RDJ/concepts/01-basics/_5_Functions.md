# `_5_Functions.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A C++ function parameter is a copy by default. To avoid the copy you pass a reference (`T&`) or, for read-only access to a large object, a const reference (`const T&`). This is the biggest functional difference from Java, where objects are always passed by reference value and primitives by copy. C++ also lets you overload functions by parameter type, give parameters default values, and mark small functions `inline`.

## Full Line-by-Line Breakdown

### SECTION 1: VALUE vs REFERENCE
`increment_value(int x)` receives a copy, so the caller's variable stays 1. `increment_ref(int& x)` receives an alias to the caller's variable, so it becomes 2. In Java you cannot write the second function for a primitive.

Output from a real run:

```text
===== SECTION 1: VALUE vs REFERENCE =====
after increment_value: 1 (unchanged)
after increment_ref:   2 (changed)
```

### SECTION 2: WHAT PASSING BY VALUE COSTS
`Noisy` counts its copies with a static counter. Passing by value performs one copy; passing by `const&` performs none; passing by `&` also none and the callee's change (`!`) is visible to the caller. Returning a freshly built object from a function adds no copy since C++17 (guaranteed copy elision). Rule of thumb: pass cheap types (`int`, `double`, pointers) by value, big types by `const&`, and use non-const `&` for out-parameters. A temporary cannot bind to a non-const reference (the commented-out line).

Output from a real run:

```text
===== SECTION 2: WHAT PASSING BY VALUE COSTS =====
copies after by_value:     1
copies after by_const_ref: 1 (no new copy)
by_ref modified the caller's object: data!
copies after returning by value: 1 (guaranteed elision, none added)
Rule: small types (int, double, pointers) by value; big types by const&; out-params by &.
```

### SECTION 3: OVERLOADING
The compiler picks the overload whose parameter types match the argument: `int`, `double` and `std::string` versions of `show`. A string literal can only become a `std::string` (an implicit conversion), so that overload is chosen. Overloads must differ in their parameters, not just the return type, and an ambiguous call is a compile error, not a silent guess.

Output from a real run:

```text
===== SECTION 3: OVERLOADING =====
int:7 double:2.50 string:x
string:literal
```

### SECTION 4: DEFAULT ARGUMENTS AND inline
`greet("Ada")` fills in `"Hello"` and `1` at the CALL site at compile time. Defaults must be the trailing parameters, and you cannot skip a middle one. Put defaults in the declaration only. `inline` today mostly means "this function may be defined in several translation units without violating the One Definition Rule", which is why header functions are `inline`; the optimiser decides on its own whether to really inline. The final lambda shows a `const&` parameter on an inline closure.

Output from a real run:

```text
===== SECTION 4: DEFAULT ARGUMENTS AND inline =====
Hello, Ada!
Hi, Ada!
Hey, Ada!!!
inline square(9) = 81
lambda over const& vector = 6
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Primitives pass by value; objects pass a reference by value | EVERYTHING passes by value unless you write `&` |
| Cannot change a caller's `int` | `void f(int& x)` can |
| No default arguments; you write overloads | Default arguments exist, plus overloads |
| `final` on a parameter is optional | `const T&` is the standard "read only, no copy" idiom |
| Method may return `null` | Return by value, pointer, or `std::optional` |
| JIT decides on inlining | `inline` is mostly a linkage hint; the optimiser decides |

## Key Rules / Gotchas Recap
- Parameters are copies unless you write `&`.
- Large read-only parameters: `const T&`. Small ones (int, double, pointers): by value.
- A non-const lvalue reference cannot bind to a temporary.
- Default arguments are trailing, filled in by the caller, and declared once (in the header).
- Overloads differ by parameter types; return type alone is not enough.
- `inline` is about the One Definition Rule more than speed.

## Why This Structure Exists
Passing the right way is the difference between a fast and a slow inference loop or parser, and the difference between code that mutates shared state by accident and code that does not. Reference semantics are also how C++ APIs express ownership and mutability, which is something security reviewers read for.
