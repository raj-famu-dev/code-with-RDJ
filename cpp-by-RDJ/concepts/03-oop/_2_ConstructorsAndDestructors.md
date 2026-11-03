# `_2_ConstructorsAndDestructors.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A constructor runs when an object is created and a destructor runs automatically when it ends (scope exit, `delete`, container destruction). C++ guarantees the order: bases and members are built before the constructor body, and destroyed in exactly the reverse order after the destructor body.

This predictable pairing is the foundation of RAII: acquire a resource in the constructor, release it in the destructor, and cleanup happens even when exceptions are thrown. Java has no equivalent timing guarantee because the garbage collector decides when (and whether) cleanup runs.

## Full Line-by-Line Breakdown

### SECTION 1: default, parameterized, delegating
`Rect` has three constructors. `Rect(int w, int h)` is the real one. `Rect()` and `Rect(int side)` DELEGATE to it (`: Rect(1, 1)`), so the setup logic lives in one place; the delegating constructor's own body runs after the target finishes, which the output shows ("body ran after delegation"). The final line is about the "most vexing parse": `Rect r3();` does not create an object, it declares a function named `r3`. Write `Rect r3;` or `Rect r3{};`.

Output from a real run:

```text
===== SECTION 1: default, parameterized, delegating =====
Rect r0;
  Rect(1,1) target ctor
  Rect() body ran after delegation
Rect r1(4);
  Rect(4,4) target ctor
Rect r2(2, 3);
  Rect(2,3) target ctor
areas: 1 16 6
Most vexing parse: `Rect r3();` declares a FUNCTION, not an object. Use `Rect r3;` or `Rect r3{};`.
```

### SECTION 2: explicit
A single-argument constructor that is not `explicit` defines an implicit conversion. `Feet(double)` is not explicit, so `describeFeet(3.5)` silently builds a `Feet` from a double. `Meters(double)` is `explicit`, so you must write `Meters{3.5}`; passing a bare `3.5` is a compile error (stated in the output, not compiled). Mark single-argument constructors `explicit` unless the conversion is truly natural.

Output from a real run:

```text
===== SECTION 2: explicit =====
describeFeet(3.5) compiles (implicit double -> Feet): 3.5
describeMeters(Meters{3.5}) must be spelled out: 3.5
describeMeters(3.5) would be a compile error because the constructor is explicit.
```

### SECTION 3: destruction order
`Logger` prints `+` on construction and `-` on destruction. In the first scope `a` and `b` are built, then a `Derived`. Building a `Derived` builds its base first (`Base subobject`, then `Base()` body), then its members in declaration order (`m1`, `m2`), then the `Derived()` body. When the scope closes everything unwinds in the exact reverse: `~Derived()` body, `m2`, `m1`, `~Base()` body, the base member, then `b` and `a`. The second block shows a `std::vector` destroying its elements; with g++ 13's library it goes front to back, but the standard does not promise that order, so never depend on it.

Output from a real run:

```text
===== SECTION 3: destruction order =====
 scope opens
  + local a
  + local b
  + Base subobject
  Base() body
  + member m1
  + member m2
  Derived() body
 scope closes (destruction runs in REVERSE order of construction)
  ~Derived() body
  - member m2
  - member m1
  ~Base() body
  - Base subobject
  - local b
  - local a

With g++ 13 (libstdc++) a vector destroys its elements front to back (the standard does not promise an order):
  + v0
  + v1
  + v2
 vector scope closes
  - v0
  - v1
  - v2

(r0, r1, r2 are destroyed when main returns.)
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `new Foo()` always heap-allocates | `Foo f;` constructs on the stack; heap only with `new`/`make_unique` |
| Constructor chaining: `this(...)` as the first line | Delegating constructor: `Foo() : Foo(1, 1) {}` |
| Implicit conversion is mostly not user-defined | One-argument constructors convert implicitly unless `explicit` |
| `finalize()` is unreliable (deprecated); use try-with-resources / `close()` | Destructors run deterministically at scope exit: that IS the cleanup mechanism |
| Fields default to 0/null | Built-in members stay uninitialized unless you initialize them |

## Key Rules / Gotchas Recap
- Construction: base class, then members in declaration order, then the body. Destruction is the exact reverse.
- Delegate to one "real" constructor to avoid duplicated setup.
- Mark single-argument constructors `explicit`.
- Beware the most vexing parse; prefer brace initialization `T x{};`.
- Destructors must not throw.
- Order of container element destruction is implementation-specific.

## Why This Structure Exists
Deterministic destruction lets C++ manage files, sockets, locks and GPU buffers without a garbage collector. Security and performance tooling relies on knowing exactly when a resource is released and zeroed.
