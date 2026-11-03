# `_3_OptionalVariantAny.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`std::optional<T>` is "a T or nothing", `std::variant<A, B, C>` is "exactly one of these types at a time", and `std::any` holds a value of any copyable type and lets you ask for it back. They replace null pointers, sentinel values like -1, unions, and `void*`. `std::variant` with `std::visit` is the closest C++ gets to a Java sealed interface with an exhaustive `switch`, and the compiler can check that you handled every alternative.

## Full Line-by-Line Breakdown

### SECTION 1: std::optional
`parse_digit` returns `std::optional<int>`: a value for digits, `std::nullopt` otherwise. You test it with `has_value()` or `if (r)`, read it with `*r`, and give a default with `value_or(-1)`. `value()` is the CHECKED accessor and throws `std::bad_optional_access` on an empty optional, while `*empty` is unchecked undefined behaviour (the TRAP; it is only described, never executed). `reset()` empties an optional and `emplace(...)` constructs a new value in place.

Output from a real run:

```text
===== SECTION 1: std::optional =====
parse_digit('7') has_value=true value=7 value_or(-1)=7
parse_digit('x') has_value=false value_or(-1)=-1
empty.value() threw std::bad_optional_access
TRAP: *empty is undefined behaviour (no check), so never dereference without testing.
after reset(), has_value=false
after emplace, value=Raj size=3
```

### SECTION 2: std::variant
A `std::variant<int, double, std::string>` holds exactly one alternative. `index()` says which (0, 1, 2), `holds_alternative<T>` tests, `get_if<T>(&v)` returns a pointer or `nullptr` (safe, no exception), and `std::get<T>(v)` throws `std::bad_variant_access` when the wrong alternative is active. TRAP: a default-constructed variant holds its FIRST alternative, so `variant<string,int>` starts as an empty string at index 0; use `std::monostate` as the first type if you want an explicit "empty" state.

Output from a real run:

```text
===== SECTION 2: std::variant =====
holds int? true, index=0
now holds string? true, index=2
get_if<string> -> hello
get_if<int> -> nullptr (wrong alternative)
std::get<int>(v) threw std::bad_variant_access
TRAP: default variant<string,int> holds index 0 (the first type), value=""; put a cheap default type first, or use std::monostate.
```

### SECTION 3: std::visit AND SEALED-STYLE SHAPES
`Shape` is a variant of `Circle`, `Rect` and `Triangle`: the C++ cousin of a sealed interface with three records. `std::visit` calls a visitor with whichever alternative is active. `area` uses a generic lambda with `if constexpr` (the branches that do not match are discarded at compile time). `describe` uses the `overloaded` helper, which inherits from several lambdas and pulls in all their `operator()` overloads, so each alternative gets its own lambda. If you forget one alternative, the program does not compile, which is like a Java exhaustive `switch` over a sealed type. (The circle area uses pi approximated as 3 so the printed numbers are tidy; this is a demo, not geometry.)

Output from a real run:

```text
===== SECTION 3: std::visit AND SEALED-STYLE SHAPES =====
circle r=2 area=12
rect 3x4 area=12
triangle area=15
A visitor must handle EVERY alternative or the program does not compile (like an exhaustive switch).
```

### SECTION 4: std::any
`std::any` can hold anything copyable. `type()` returns a `typeid` you compare against, and `std::any_cast<T>(box)` extracts the value. Asking for the wrong type throws `std::bad_any_cast`; the pointer form `any_cast<T>(&box)` returns `nullptr` instead of throwing. `reset()` empties it. `any` throws away compile-time type checking, so use `variant` whenever the possible types are known in advance.

Output from a real run:

```text
===== SECTION 4: std::any =====
holds int? true, value=10
holds string? true, value=now a string
any_cast<int> on a string threw std::bad_any_cast
pointer form any_cast<double>(&box) returned nullptr (no throw)
after reset, has_value=false
Prefer variant when the set of types is known; any loses all compile-time checking.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `Optional<Integer>`; `isPresent()`, `get()`, `orElse(x)`, `ifPresent`. | `std::optional<int>`; `has_value()`, `value()`, `value_or(x)`. It is a value type stored inline, no heap allocation. |
| `Optional` is only a return-type convention; the reference can still be `null`. | `optional` is a real type with no null-reference problem for values. |
| `Optional.get()` on empty throws `NoSuchElementException`. | `value()` throws `bad_optional_access`; `*opt` is undefined behaviour if empty. |
| `sealed interface Shape permits Circle, Rect, Triangle` plus a pattern `switch`. | `using Shape = std::variant<Circle, Rect, Triangle>;` plus `std::visit`. No inheritance, no virtual calls, no heap allocation. |
| Pattern matching `switch (shape) { case Circle c -> ... }` | `std::visit` with a visitor or the `overloaded` lambdas trick. |
| `Object` can hold anything; `instanceof` and casts. | `std::any` with `any_cast`; wrong type throws `bad_any_cast`. |

## Key Rules / Gotchas Recap
- Check before dereferencing an `optional`: `if (opt)`, `value_or`, or use `value()` if you want an exception.
- A variant's size is that of its largest alternative plus a tag; it lives inline.
- `get_if` (pointer) is the non-throwing access; `get` throws.
- A default-constructed variant holds the first alternative.
- `std::visit` must handle every alternative; this is a compile-time guarantee.
- Prefer `variant` over `any`; `any` allocates for large types and loses static type safety.

## Why This Structure Exists
Return types that say "this may fail or be absent" (`optional`) and message/event types that are "one of these kinds" (`variant`) make parsers, protocol handlers and AI pipelines (tool-call results, token types) explicit and exhaustively checked. In security code, an unchecked null or an unhandled message type is exactly how many bugs start.
