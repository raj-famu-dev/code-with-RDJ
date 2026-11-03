# `_5_VirtualFunctionsAndPolymorphism.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A `virtual` function is chosen at run time based on the real type of the object, not the type of the pointer or reference used to reach it. That is polymorphism: one `Shape&` can be a square, a circle or anything else derived from it, and `area()` does the right thing.

C++ implements this with a hidden vtable pointer inside each polymorphic object. It is cheap but not free, and it comes with one deadly trap: a base class that is deleted through a pointer must have a `virtual` destructor.

## Full Line-by-Line Breakdown

### SECTION 1: virtual + override + final
`Shape` declares a virtual destructor, a pure virtual `area()` (the `= 0` makes it abstract; see file 6) and a virtual `name()`. `label()` is non-virtual and is written once; inside it, the calls to `name()` and `area()` dispatch on the real object. `override` tells the compiler "this must override a base virtual", and `final` forbids further overriding or deriving (`Circle` cannot be derived; `Cube::name` cannot be overridden again). Note `Cube` reports `CubeFace` and `area=9`, which proves the most-derived override was called through a `unique_ptr<Shape>`. (Pi is approximated as 3 so printed values are integers.)

Output from a real run:

```text
===== SECTION 1: virtual + override + final =====
  Square area=16
  Circle area=12
  CubeFace area=9
label() is written once in Shape and calls name()/area() which dispatch on the REAL object type.
```

### SECTION 2: the vtable, observed
Mechanism, explained in plain English. Each class with virtual functions gets one table (the vtable): an array of pointers to the functions that class uses. Each object gets one hidden pointer (the vptr) to its class's table. A virtual call does: read the object's vptr, index the table, jump to the function. Constructing a `Cube` sets its vptr to the Cube table, so `name()` finds `Cube::name` even through a `Shape&`. (During a base constructor the vptr points at the base table, which is why virtual calls from constructors do NOT reach the derived override.)

You can measure the cost in memory: a `double` alone is 8 bytes; add a virtual function and the struct is 16 bytes (on this 64-bit machine), because of the vptr. The call cost is an extra indirect jump and potentially lost inlining; the file claims no timings since none were measured.

Output from a real run:

```text
===== SECTION 2: the vtable, observed =====
sizeof(Square) = 16 (one double = 8, plus one hidden vptr = 8)
sizeof(NoVirtual) = 8, sizeof(WithVirtual) = 16
Cost model: one pointer per object, one indirect call per virtual call, can prevent the compiler from inlining the call.
```

### SECTION 3: virtual destructor trap
With a virtual destructor (`GoodBase`), `delete p` on a `GoodBase*` that points to a `GoodDerived` runs `~GoodDerived` and then `~GoodBase`: the correct chain. With a NON-virtual destructor (`BadBase`), the same `delete` is undefined behaviour; typically only `~BadBase` runs, so anything `BadDerived` owns leaks. This is hidden behind the flag `--trap` because AddressSanitizer would (rightly) abort on it. The flag was run without sanitizers and printed:

```text
TRAP (--trap): deleting BadDerived through BadBase* (undefined behaviour):
  ~BadBase
Notice: '~BadDerived' was never printed, so Derived's resources would leak.
```

The missing `~BadDerived` line is the proof. The rule: if a class has any virtual function, or is meant to be a base class used through pointers, give it a `virtual ~T() = default;`.

Default-run output:

```text
===== SECTION 3: virtual destructor trap =====
Correct (virtual destructor), deleting through GoodBase*:
  ~GoodDerived
  ~GoodBase
TRAP not run by default (it is undefined behaviour). Run with --trap to see ~BadDerived never print.
```

### SECTION 4: how override protects you
`Oops::greet(long)` was meant to override `Base2::greet(int)` but the parameter type differs, so it is a brand-new function that hides the base one; calling through `Base2&` runs the base version (an empty function, so nothing prints). Without `override` the compiler accepts this silently (g++ even warns with `-Woverloaded-virtual`, which the file turns off around that one demo). `Fixed` uses `override`, the signature matches, and the call prints. Writing `override` on `Oops::greet(long)` would be a compile error, which is exactly the point.

Output from a real run:

```text
===== SECTION 4: how override protects you =====
  Oops::greet(long) was NOT called through Base2& (it is not an override); nothing printed above.
  Fixed::greet(int) overrides
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Every instance method is virtual unless `final`/`static`/`private` | Non-virtual unless you write `virtual` |
| `@Override` annotation is optional | `override` keyword is optional but you should always write it |
| `final` class / method | `final` on class or virtual function |
| Objects are deleted by the GC; no destructor problem | `delete` through a base pointer needs a virtual destructor or it is undefined behaviour |
| Overriding is by name + parameter types | Same, but a mismatch silently creates a new function unless you use `override` |
| Every object has a hidden class pointer | Only polymorphic classes get a vptr (extra 8 bytes here) |

## Key Rules / Gotchas Recap
- Polymorphism needs a reference or pointer; by-value copies slice (file 4).
- Always `override` (and `final` where intended).
- Base with virtuals => `virtual ~Base() = default;`.
- Do not call virtual functions from constructors/destructors expecting derived behavior.
- `delete` through a base pointer without a virtual destructor is undefined behaviour; sanitizers flag it, so the demo is behind `--trap`.

## Why This Structure Exists
Plugin architectures, inference backends (CPU/GPU implementations behind one interface) and scanner modules in security tools all use virtual dispatch. Knowing the vptr/vtable mechanism also explains why a corrupted object can hijack control flow, a core concept in exploit mitigation (control-flow integrity).
