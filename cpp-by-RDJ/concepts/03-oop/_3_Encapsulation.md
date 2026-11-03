# `_3_Encapsulation.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Encapsulation means hiding a class's data behind a small public interface so the class can guarantee its own rules (its invariants). If outside code can modify the data directly, the invariant is only a hope; if only member functions can, the class can enforce it.

C++ adds tools Java lacks: `const` member functions (a compiler-checked promise not to change the object), `mutable` (an escape hatch for caches), and `friend` (deliberately granting access to a specific outsider).

## Full Line-by-Line Breakdown

### SECTION 1: an invariant enforced by private data
`Percent` keeps its value private. The only way to change it is `set()`, which throws `std::out_of_range` for anything outside 0..100. The demo tries `set(150)`, catches the exception, and shows the old value (40) is still there. The invariant holds because there is no other door.

Output from a real run:

```text
===== SECTION 1: an invariant enforced by private data =====
Percent(40).get() = 40
rejected: percent must be 0..100, got 150
value after rejected set = 40 (unchanged, invariant intact)
```

### SECTION 2: const member functions
`double mean() const` promises not to change the visible state of the object. The function takes a `const Stats&` in `readOnlyView`, and the compiler only allows const members to be called on it. `mean()` still needs a cache, so the cache members are marked `mutable`, meaning "this member may change even inside a const function". The output shows the cache is filled once for two calls, then invalidated by `add()` and refilled. Rule: `mutable` is for caching/locking details that are not part of the logical value, never for hiding real changes.

Output from a real run:

```text
===== SECTION 2: const member functions =====
  mean via const& = 5
  mean via const& = 5
cache was filled 1 time(s) for 2 const calls (mutable cache)
  mean via const& = 4
after add(): cache filled 2 time(s) total
```

### SECTION 3: friend
`audit` is a free function that is declared `friend` inside `Secret`, so it may read private `v_`. The streaming operator is a friend defined inline, the most common legitimate use. Friendship is one-way and not inherited. It breaks encapsulation on purpose, so use it for tightly coupled helpers such as operators.

Output from a real run:

```text
===== SECTION 3: friend =====
  audit reads private v_ = 7
  streamed: Secret(7)
  friendship is not inherited and not mutual; grant it sparingly.
```

### SECTION 4: the leaky getter trap
`LeakyBag::items()` returns a non-const reference to its private vector. Private data, public back door: the caller calls `clear()` and the "never empty" rule dies (size 0). `SafeBag` returns a `const&` (read-only view) and offers `removeLast()` that enforces the rule by throwing; the loop stops at size 1. Returning a `const` reference or a copy keeps control inside the class.

Output from a real run:

```text
===== SECTION 4: the leaky getter trap =====
LeakyBag after caller clears items(): size = 0 (invariant broken)
SafeBag stopped by its own rule: invariant: bag may never become empty; size = 1
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `private` fields + getters returning mutable objects have the same leak | Same leak; fix with `const T&` returns (Java: unmodifiable view or defensive copy) |
| `final` fields/methods (no `const` method concept) | `const` member functions checked by the compiler, `const` propagates through references |
| No `friend`; package-private is the nearest tool | `friend` grants access to a named function/class |
| Reflection (`setAccessible`) can bypass `private` | No reflection; access control is checked at compile time |
| No `mutable` | `mutable` lets a const function update caches |

## Key Rules / Gotchas Recap
- Make data private; expose behavior, not fields.
- Mark every member function that does not modify the object `const`.
- Return `const T&` (or a copy) from getters; a non-const reference is a public field in disguise.
- `mutable` only for caches/locks, never to dodge `const`.
- `friend` is for tight coupling like `operator<<`; it is not inherited and not mutual.

## Why This Structure Exists
Invariants are what make large systems reliable. In security tooling, a buffer class that guarantees "length never exceeds capacity" prevents whole bug classes; in AI inference code `const`-correctness lets the compiler prove that shared model weights are read-only and safe to use across threads.
