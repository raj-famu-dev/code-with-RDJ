# `_7_RuleOfThreeFiveZero.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
If a class owns a resource such as heap memory, the compiler-generated copy simply copies the pointer, so two objects believe they own the same block and both free it. The Rule of Three says: if you write a destructor, copy constructor or copy assignment, you almost certainly need all three. The Rule of Five adds move construction and move assignment (to steal resources instead of copying). The Rule of Zero says the best classes need none of them: hold `std::string`, `std::vector` and smart pointers and let the compiler-generated members do the right thing.

The WRONG class in this file really has the shallow-copy bug. By default the demo detaches the copy so nothing is freed twice; `--bug=shallow-copy` lets the double free happen so you can see it under AddressSanitizer.

## Full Line-by-Line Breakdown

### SECTION 1: THE BUG (RULE OF THREE VIOLATED)
`WrongBuffer` has a destructor that frees its array but no copy constructor. `WrongBuffer copy = original;` therefore copies the POINTER. Writing 99 through `copy` also changes `original` (they share one block), and the two raw pointers compare equal. When both objects are destroyed, each runs `delete[]` on the same address: a double free (see `--bug=shallow-copy` below). The default run calls `detach_for_demo()` (sets the copy's pointer to null) just so the program can end cleanly; that method exists only for the demo and no real code should have it.

Output from a real run:

```text
===== SECTION 1: THE BUG (RULE OF THREE VIOLATED) =====
  wrote 99 through the copy; original.at(0) = 99 (shared block, not a copy)
  both point at the same array: true
  detached the copy so destruction is safe. Without that, both destructors would delete[] the same block.
```

#### Seeing the double free (`--bug=shallow-copy`)

```bash
g++ -std=c++20 -g -fsanitize=address,undefined -o prog _7_RuleOfThreeFiveZero.cpp
./prog --bug=shallow-copy
```

With the flag, the copy is NOT detached, so both destructors free the same block. Real headline lines from AddressSanitizer (pid and address removed):

```text
ERROR: AddressSanitizer: attempting double-free on ADDR in thread T0:
SUMMARY: AddressSanitizer: double-free ../../../../src/libsanitizer/asan/asan_new_delete.cpp:155 in operator delete[](void*)
(exit code 1)
```

The default run (no flag) does not do this and exits with code 0, also under the sanitizers.

### SECTION 2: RULE OF FIVE DONE RIGHT
`Buffer` implements all five special members. The copy constructor makes a DEEP copy (new array, copy the numbers), so `b.set(0, 1)` leaves `a` unchanged. Copy assignment uses the copy-then-swap pattern: it makes a temporary copy first (so if allocation throws, the target is untouched), swaps with it, and lets the temporary's destructor free the old block; a `this != &o` check keeps `c = c` safe. The static counters show two copies so far and no moves.

Output from a real run:

```text
===== SECTION 2: RULE OF FIVE DONE RIGHT =====
  deep copy: a.at(0) = 7, b.at(0) = 1
  copy assignment: c.size() = 3, c.at(2) = 7
  self-assignment survived: c.size() = 3
  copies so far = 2, moves so far = 0
```

### SECTION 3: COPY vs MOVE
`std::move(big)` does not move anything by itself; it casts to an rvalue so the MOVE constructor is chosen. The move constructor steals the pointer and size and leaves the source empty (`size() == 0`): O(1) no matter how big the array is. A moved-from object is valid but its content is unspecified, so only assign to it or destroy it. The counters show that no extra copy happened. Move assignment frees the old block, then steals.

Output from a real run:

```text
===== SECTION 3: COPY vs MOVE =====
  after move: stolen.size() = 1000, big.size() = 0 (moved-from is valid but empty)
  copies = 2, moves = 1
  move assignment: target.size() = 1000, stolen.size() = 0
```

### SECTION 4: noexcept MATTERS FOR vector
When a `vector` reallocates, it moves its elements to the new buffer only if the move constructor is `noexcept`; otherwise it COPIES them, to keep the strong exception guarantee (if a move threw halfway, the old elements would be lost). The two counters show the difference after four `push_back` calls: the type without `noexcept` triggered 3 copies, the one with `noexcept` triggered none. (The exact counts depend on the library's growth steps.) Always mark move operations `noexcept` when they cannot throw.

Output from a real run:

```text
===== SECTION 4: noexcept MATTERS FOR vector =====
  move ctor NOT noexcept: copies=3 moves=4 after 4 push_backs (includes reallocations)
  move ctor noexcept    : copies=0 moves=7 after 4 push_backs (includes reallocations)
  vector only moves on reallocation if the move cannot throw; otherwise it copies to keep its guarantee.
```

### SECTION 5: RULE OF ZERO
`Document` holds a `std::string` and a `std::vector<int>` and declares no special members at all. The compiler-generated copy is correct (deep, because the members copy deeply) and the generated move is cheap. This is the target design: write resource-owning wrappers once (the standard library already did), and compose them.

Output from a real run:

```text
===== SECTION 5: RULE OF ZERO =====
  d1: Notes with 3 pages; d3: Notes with 3 pages
  Rule of Zero: hold std::string / std::vector / smart pointers and write none of the five.
  Rule of Three/Five: if you write ANY of destructor, copy, move, write (or delete) all of them.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Assignment copies a reference; objects are shared | Assignment copies the OBJECT (value semantics) |
| `clone()` / copy constructors are opt-in and rare | Copy constructor and copy assignment are automatic, so you must make them correct |
| No destructors to pair with copying | Destructor + copy + move must agree about ownership |
| Moving is not a concept (references are cheap) | Move semantics transfer ownership of expensive resources cheaply |
| Shallow-vs-deep copy decision is explicit in `clone()` | Compiler-generated copy is memberwise: shallow for raw pointers (the bug), deep for `std::vector`/`std::string` |
| GC prevents double free | A shallow copy of an owning raw pointer double-frees |

## Key Rules / Gotchas Recap
- If a class owns a raw resource, write the destructor, copy constructor, copy assignment, move constructor and move assignment, or delete the ones you do not want (Rule of Five).
- Compiler-generated copy of a raw pointer copies the address (shallow), producing two owners.
- Copy-then-swap makes copy assignment exception safe; guard against self-assignment.
- `std::move` is only a cast; the move constructor does the stealing.
- A moved-from object is valid but unspecified: assign or destroy it, do not rely on its content.
- Mark move constructor/assignment `noexcept`, or containers will copy instead of move.
- Best option: Rule of Zero, with members that already manage themselves.

## Why This Structure Exists
This rule is the reason real C++ code uses `std::vector` and `std::unique_ptr` instead of hand-rolled buffers: manual resource classes are where double-free and use-after-free bugs are born, and they are also where performance is won or lost through unnecessary copies. Knowing the rules lets you read and review low-level code in inference runtimes and security-sensitive libraries.
