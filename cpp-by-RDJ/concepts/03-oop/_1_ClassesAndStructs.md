# `_1_ClassesAndStructs.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A C++ `class` and a C++ `struct` are the same thing except for one default: members of a `struct` are `public` unless you say otherwise, members of a `class` are `private`. Everything else (methods, constructors, inheritance, templates) works identically for both.

Access specifiers (`public`, `protected`, `private`) decide who may touch a member. A constructor's member initializer list (`: x(a), y(b)`) builds each member directly instead of default-constructing it and assigning later, and `this` is the hidden pointer to the object a method was called on.

## Full Line-by-Line Breakdown

### SECTION 1: class vs struct
`PointS` is a `struct`, so `ps.x` is reachable from `main`. `PointC` is a `class` with the same two ints, so they are private and only reachable through its constructor and `sum()`. The program checks that both have the same size and are both standard-layout types: the choice of keyword changes nothing about memory layout. Convention: use `struct` for plain bundles of data, `class` when there are invariants to protect.

Output from a real run:

```text
===== SECTION 1: class vs struct =====
struct member access ps.x = 3 (public by default)
class method pc.sum() = 7 (members private by default; ps.x style access would not compile)
sizeof(PointS) == sizeof(PointC): true
both standard-layout: true/true
```

### SECTION 2: access specifiers
`Account` shows all three levels. `owner()` and `deposit()` are `public` (the interface). `balance_` and `owner_` are `private` (only `Account` code may touch them). `protectedValue()` is `protected`: invisible to outside code, visible to classes that inherit from `Account`. `balance_ = 0` is a default member initializer, used whenever a constructor does not set the member itself. The program cannot demonstrate the compile errors (the file must compile), so it states them.

Output from a real run:

```text
===== SECTION 2: access specifiers =====
rdj balance = 75
a.balance_ would be a compile error (private); a.protectedValue() too (protected).
```

### SECTION 3: member initializer lists
`Noisy` prints whenever it is constructed, copied or assigned, which makes the hidden work visible. `ViaList` initializes its member in the list: one copy-construction, done. `ViaBody` first default-constructs `n` (the `"default"` line), then the body assigns over it: two operations instead of one. For `int` the difference is trivial; for strings, vectors, or members that have no default constructor, `const` members and references, the list is mandatory.

The trap: members are initialized in the order they are DECLARED in the class, never in the order written in the list. `OrderTrap` writes `second` first in its list, but `first` is declared first, so `first` is built first. The program uses a `Tracer` that prints, so the wrong order is visible without reading uninitialized memory. In real code the damage would be `first(second * 2)` reading `second` before it exists. g++ warns about this with `-Wreorder`; the file silences that warning with a `#pragma` ONLY around the demo struct so the file still compiles with zero warnings.

Output from a real run:

```text
===== SECTION 3: member initializer lists =====
  Noisy(src) constructed
ViaList (initializes n directly by copy):
  Noisy copied -> src-copy
ViaBody (default-constructs n, then assigns in the body):
  Noisy(default) constructed
  Noisy assigned -> src-assigned
result names: src-copy | src-assigned
OrderFixed(5): first=10 second=5
OrderTrap: list says second then first; actual construction order:
  init first (written second in list)
  init second (written first in list)
```

### SECTION 4: this
`this` is a pointer to the current object. `add` returns `*this` (a reference to the object), which is what allows chaining: `c.add(1).add(2).add(3)`. `isSame` compares `this` with the address of the argument, which tells whether two references refer to the same object. In `const` member functions `this` has type `const Counter*`.

Output from a real run:

```text
===== SECTION 4: this =====
chained add(1).add(2).add(3) total = 6
c.isSame(c) = true, c.isSame(d) = false
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `class` only; access defaults to package-private | `class` (private default) and `struct` (public default) |
| Access modifier written on every member | One specifier applies to all following members until the next one |
| Fields are initialized in the constructor body or at declaration | Member initializer list runs BEFORE the body; order follows declaration order |
| `this` is a reference | `this` is a pointer (`this->x`, `*this`) |
| Objects live on the heap, variables are references | `Account a("rdj");` is a real object on the stack, not a reference |
| Fields have defaults (0, null) | Fields of built-in type are uninitialized unless you initialize them |

## Key Rules / Gotchas Recap
- `struct` vs `class` is only the default access level.
- Prefer the initializer list over assigning in the body; required for `const` members, references and members without a default constructor.
- Keep the list in declaration order; turn on `-Wall` so `-Wreorder` tells you when you do not.
- Give built-in members a default (`int n = 0;`); they are NOT zeroed for you.
- `sizeof` values (like those in later files) are for this platform (x86-64 g++ 13); they are not guaranteed by the language.

## Why This Structure Exists
Deterministic, explicit object construction is the base of every C++ systems program: parsers, network code and ML runtimes depend on objects being fully and correctly built. Reading uninitialized members is a classic source of security bugs, so initializer discipline is a safety habit, not style.
