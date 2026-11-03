# `_1_MoveSemantics.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Move semantics let C++ transfer the contents of a temporary or no-longer-needed object (steal its pointer) instead of duplicating them. An lvalue is something with a name and an address that you can use again; an rvalue is a temporary about to disappear. `std::move` does not move anything, it only casts an lvalue to an rvalue reference so that the move constructor or move assignment operator is chosen. This is how `std::vector`, `std::string` and `std::unique_ptr` are returned and stored cheaply, and it is a core reason C++ can be fast without garbage collection.

## Full Line-by-Line Breakdown

### SECTION 1: LVALUES AND RVALUES
`which(const std::string&)` and `which(std::string&&)` are two overloads that reveal which kind of reference was bound. `name` has a name, so it is an lvalue and picks the first overload. `std::string("temp")` is a temporary (rvalue) and picks the second. `std::move(name)` produces an rvalue-reference expression, so the second overload is chosen again, even though `name` is still a perfectly normal variable. The lesson in the last line: `std::move` is only a cast.

Output from a real run:

```text
===== SECTION 1: LVALUES AND RVALUES =====
  which(const std::string&)  [lvalue/const overload]
  which(std::string&&)       [rvalue overload]
  which(std::string&&)       [rvalue overload]
std::move did not move anything by itself; it is a cast.
```

### SECTION 2: COPY vs MOVE CONSTRUCTION
`Buffer` owns a heap array and counts every copy and move in static counters. `Buffer b(a)` runs the copy constructor: new memory plus an element-by-element copy (`copies=1`). `Buffer c(std::move(a))` runs the move constructor: it just takes `a`'s pointer and nulls it out (`moves=1`, no new allocation). `Buffer d = make_buffer()` shows guaranteed copy elision (C++17): the object is built directly in `d`, so neither counter changes. This is the measurable proof that a move avoids a copy; the counts are exact, not timings.

Output from a real run:

```text
===== SECTION 2: COPY vs MOVE CONSTRUCTION =====
after Buffer b(a) -> copies=1 moves=0
after Buffer c(std::move(a)) -> copies=1 moves=1
after Buffer d = make_buffer() -> copies=1 moves=1
sizes: b=1000 c=1000 d=1000
```

### SECTION 3: MOVED-FROM STATE
After `Buffer c(std::move(a))`, `a` is "moved-from": our class leaves it with a null pointer, `size()==0` and `empty()==true`. The standard rule for library types such as `std::string` is that a moved-from object is in a valid but unspecified state: you may destroy it or assign to it, but you must not assume its contents. Here `s.size()` happened to be 0 on this implementation, but the program says plainly not to rely on that. Re-assigning `s` is always safe and gives it a fresh value.

Output from a real run:

```text
===== SECTION 3: MOVED-FROM STATE =====
a after being moved from: size=0 empty=true
t = "hello world..."
s.size() after move: 0 (valid but unspecified; do not rely on it)
s after re-assignment: assigned again
```

### SECTION 4: MOVE ASSIGNMENT
Copy assignment `x = y` copies (`copies=1`, written with the copy-and-swap idiom). `x = std::move(y)` runs the move assignment operator: it frees `x`'s old array, takes `y`'s pointer and nulls `y`. The `this != &other` guard makes self-assignment safe; the demo creates a reference alias `alias` so the compiler's self-move warning is not triggered, and `x` keeps size 20.

Output from a real run:

```text
===== SECTION 4: MOVE ASSIGNMENT =====
after x = y -> copies=1 moves=0
after x = std::move(y) -> copies=1 moves=1
x.size() after self-move guard: 20
```

### SECTION 5: vector GROWTH, noexcept TRAP
`std::vector` must relocate elements when it grows. For `Buffer`, whose move constructor is `noexcept`, the 5th `emplace_back` moves the 4 old elements (`moves=4`, `copies=0`). For `Sloppy`, whose move constructor is NOT marked `noexcept`, `vector` uses `std::move_if_noexcept` and falls back to COPYING (`copies=4`) so that an exception during relocation cannot lose data. TRAP: forgetting `noexcept` on move operations silently turns cheap moves into copies inside containers.

Output from a real run:

```text
===== SECTION 5: vector GROWTH, noexcept TRAP =====
4 emplace_back into reserved vector -> copies=0 moves=0
5th emplace_back forced reallocation (noexcept move used) -> copies=0 moves=4
Sloppy (move not noexcept) -> copies=4 moves=0  (vector copied the 4 old elements to keep the strong guarantee)
```

### SECTION 6: BY-VALUE PARAMETERS AND RETURNS
Passing by value then returning: with an lvalue argument `pass_through(p1)` the parameter is copy-constructed (1 copy) and `return b;` moves it out (1 move). With `std::move(p1)` the parameter is move-constructed and the return moves again (`moves=2`, no copies). The final TRAP: `std::move` applied to a `const Buffer` yields `const Buffer&&`, which cannot bind to `Buffer&&`, so the copy constructor runs (`copies=1`). You cannot steal from something const, and the compiler silently falls back rather than warning.

Output from a real run:

```text
===== SECTION 6: BY-VALUE PARAMETERS AND RETURNS =====
pass_through(lvalue) -> copies=1 moves=1
pass_through(std::move) -> copies=0 moves=2
r1.size()=50 r2.size()=50
TRAP: std::move(const Buffer) -> copies=1 moves=0
A const object cannot be stolen from, so the copy constructor ran.
from_const.size()=10
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `Object b = a;` copies a reference; both names refer to one object. | `Buffer b = a;` copies the whole object (deep copy if the class says so). Sharing needs a pointer, reference or `shared_ptr`. |
| No way to "steal" from an object; the GC reclaims memory later. | `std::move` plus a move constructor transfers ownership and leaves the source empty. |
| Returning an object returns a reference (cheap). | Returning by value is cheap because of copy elision and moves. Do NOT return `std::move(local)`; it can prevent elision. |
| A "moved-from" state does not exist. | A moved-from object is valid but unspecified; only destroy it or assign to it. |
| `null` is available on any reference. | A moved-from `unique_ptr` is null by guarantee; other types define their own empty state. |
| No rule about exceptions in resource transfer. | Mark move operations `noexcept` or containers will copy instead. |

## Key Rules / Gotchas Recap
- `std::move` is a cast to rvalue; the move happens inside the move constructor/assignment that gets chosen.
- Never use an object after moving from it, except to destroy it or assign a new value.
- Mark move constructor and move assignment `noexcept`; otherwise `std::vector` growth copies.
- `std::move` on a `const` object silently copies.
- Rule of five: if you write a destructor, copy ctor, or copy assignment, think about the move ones too (or use the Rule of Zero with `std::vector`/`std::unique_ptr` members).
- Do not `return std::move(local);` it blocks copy elision.

## Why This Structure Exists
Moving large buffers, tensors and strings without copying is the difference between a fast and a slow data pipeline in AI inference code and parsers. In security tooling, understanding exactly when memory is duplicated, stolen or left empty is also how you reason about use-after-move bugs and about sensitive data lingering in copies.
