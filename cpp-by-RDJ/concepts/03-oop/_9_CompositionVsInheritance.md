# `_9_CompositionVsInheritance.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Inheritance says "is-a"; composition says "has-a". "Prefer composition over inheritance" means: when a class merely needs the services of another class, hold it as a member and expose a small interface, instead of inheriting and exposing everything. Inheritance couples you to the base's entire public interface and implementation details.

The file refactors one design both ways so you can see the difference.

## Full Line-by-Line Breakdown

### SECTION 1: Version A, inheritance
`StackByInheritance` derives from `std::vector<int>` and adds `push`/`pop`. It seems to work, but it is still a vector: the demo calls `insert` and `erase` on the middle of a "stack", which no stack should allow, so the stack discipline is not enforced. In addition `std::vector` has no virtual destructor, so deleting a derived object through a `vector*` would be undefined behaviour (stated, not run). The standard containers are not designed as base classes.

Output from a real run:

```text
===== SECTION 1: Version A, inheritance =====
pop() = 3 (looks like a stack)
but a 'stack' also allows insert/erase anywhere; contents now: 99 2
Also: std::vector has no virtual destructor; deleting a StackByInheritance through a vector* would be undefined behaviour.
```

### SECTION 2: Version B, composition
`Stack` holds a private `std::vector<int>` and exposes only `push`, `pop`, `top`, `empty`, `size`. `pop` on an empty stack throws `std::underflow_error` instead of invoking undefined behaviour. Because the vector is hidden, you could change it to a `std::deque` and no caller would change (nothing else is exposed). That is the real gain: you control the interface.

Output from a real run:

```text
===== SECTION 2: Version B, composition =====
top = 30, size = 3
pop x3: 30 20 10
pop on empty: pop on empty Stack (invariant enforced)
s.insert(...) does not exist: only push/pop/top/empty/size can be called.
Later we could swap std::vector for std::deque or std::list inside Stack and no caller would change.
```

### SECTION 3: composition lets behavior change at run time
`Checkout` HAS a `Discount` (a small abstract interface; this is the Strategy pattern). `setDiscount` swaps the behavior on a live object: 2000 cents becomes 1500 with 25% off. With inheritance you would create a subclass per behavior and could not change an object's behavior after construction. Ownership is explicit via `unique_ptr`.

Output from a real run:

```text
===== SECTION 3: composition lets behavior change at run time =====
no discount on 2000c: 2000
25% off on 2000c   : 1500 (same Checkout object, new behaviour)

Rule of thumb:
  - inherit for a true is-a relationship AND when you need polymorphism through the base
  - otherwise hold the other class as a member (has-a) and forward the few operations you want
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Extending `ArrayList` for a stack is the same mistake (classic `java.util.Stack extends Vector` flaw) | Same lesson, with an extra danger: standard containers have no virtual destructor |
| Inject a dependency via constructor/interface | Same, with `unique_ptr<Interface>` expressing ownership |
| Many classes are non-final and open to inheritance | Mark classes `final` when they are not designed for inheritance |
| Delegation is manual boilerplate | Same; forward only what you need |
| Interfaces used for strategy | Abstract base class or `std::function` (see the STL folder, lambdas) |

## Key Rules / Gotchas Recap
- Ask "is it truly an X in every context?" before inheriting.
- Do not inherit from standard containers; wrap them.
- Composition lets you hide, swap and enforce invariants.
- Use inheritance when you need polymorphism through a base interface.
- Hold owned collaborators by value or `unique_ptr`.

## Why This Structure Exists
Large codebases (inference servers, security scanners) are easier to change when classes depend on small interfaces rather than on deep inheritance trees. Composition keeps the blast radius of a change small.
