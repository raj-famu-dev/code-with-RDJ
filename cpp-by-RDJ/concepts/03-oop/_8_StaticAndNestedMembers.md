# `_8_StaticAndNestedMembers.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A `static` member belongs to the class itself rather than to any one object: one copy shared by all objects, usable without creating an object. Nested types (a struct, class or enum declared inside another class) group related names and keep the outer namespace clean.

Enumerations come in two flavors: old unscoped `enum` (names leak into the surrounding scope and convert to `int`) and modern `enum class` (scoped and type-safe). Prefer `enum class`.

## Full Line-by-Line Breakdown

### SECTION 1: static members
`Widget` counts live objects with a static data member `liveCount_` incremented in the constructor and decremented in the destructor. `Widget::live()` is a static function: called through the class, with no `this`, so it can only touch static data. The output shows 0, 2, 3 live objects and 0 again after the scope ends, while `totalCreated` stays at 3. You can also call a static through an object (`c.live()`), but writing `Widget::live()` is clearer.

Output from a real run:

```text
===== SECTION 1: static members =====
live before: 0
live with 2 objects: 2 (shared by the class, called without an object)
live with 3 objects: 3 via object c.live() = 3
live after scope: 0, totalCreated: 3
```

### SECTION 2: inline static
Before C++17 you declared `static int count;` in the class and defined `int Widget::count = 0;` in exactly one `.cpp` file, or the linker complained about an undefined reference. `static inline` defines it in the class itself, which is safe in a header included from many files. `static constexpr` members are implicitly inline.

Output from a real run:

```text
===== SECTION 2: inline static =====
Before C++17 a static data member needed `int Widget::totalCreated = 0;` in exactly one .cpp file.
With `static inline` the definition is in the class; kMaxName = 16 (static constexpr)
Trap avoided: without inline, defining a static in a header included twice gives a linker error (multiple definition).
```

### SECTION 3: nested types
`Graph::Edge` and `Graph::Kind` live inside `Graph`. Code outside the class must write the full name. The demo builds a directed and an undirected graph with the same edges and shows node 2 has degree 1 vs 2. Unlike a Java (non-static) inner class, a C++ nested class does not hold a hidden reference to an outer object; it is closer to a Java `static` nested class. It can access the outer class's private members, though.

Output from a real run:

```text
===== SECTION 3: nested types =====
outside code must say Graph::Edge: {1,2}
degree of node 2 in directed graph  : 1
degree of node 2 in undirected graph: 2
A nested class is only a namespace-like grouping: it has no hidden pointer to an outer object (unlike a Java inner class).
```

### SECTION 4: enum class vs unscoped enum
Unscoped `Color` puts `Red`, `Green`, `Blue` into the global scope (so two unscoped enums with the same names clash) and converts to `int` silently. `enum class Fruit` requires `Fruit::Banana` and never converts to `int` unless you `static_cast`. `enum class Level : unsigned char` picks the underlying type explicitly, so `sizeof(Level)` is 1 byte. Default recommendation: `enum class`.

Output from a real run:

```text
===== SECTION 4: enum class vs unscoped enum =====
unscoped Green converts to int silently: 1
enum class needs the scope and prints via a function: Banana
static_cast<int>(Fruit::Banana) = 1 (conversion must be explicit)
`Fruit::Apple == 0` does not compile (enum class never converts to int on its own).
sizeof(Level) = 1 byte (underlying type was chosen), High = 200
Light is an unscoped enum: On_ = 1; the unscoped Color Red == 0 compiles and is true (an enum silently acts like an int)
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `static` fields initialized in a static block or inline | `static inline` (C++17) or defined once in a `.cpp` |
| Static nested class vs inner class | A nested class is always like Java's static nested class |
| `enum` is a class with methods, always scoped (`Color.RED`) | `enum class` is just named integers (no methods); plain `enum` leaks names |
| `Color.values()`, `ordinal()` | No built-in iteration; you write it |
| Static initialization order handled by class loader | Static initialization order across translation units is unspecified ("static init order fiasco") |

## Key Rules / Gotchas Recap
- Static data members need exactly one definition: use `static inline` or `static constexpr`.
- Static member functions have no `this`.
- Prefer `enum class`; give it an explicit underlying type when size or serialization matters.
- Do not rely on the order in which statics in different .cpp files are initialized.
- Plain enums convert to int silently and pollute scope.

## Why This Structure Exists
Instance counters, registries and configuration constants are everywhere in real systems, and typed enums prevent whole classes of mix-up bugs (wrong state code, wrong protocol field) in parsers and network tools.
