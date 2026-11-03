# `_8_ConstAndLifetimes.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`const` is a promise checked by the compiler: this object, through this name, will not be modified. Using it everywhere possible turns a class of bugs into compile errors. Lifetimes are the other half: a reference, pointer or iterator is only valid as long as the object it refers to is alive and has not moved. When a `std::vector` grows, it allocates a new buffer and frees the old one, so every pointer, reference and iterator into the old buffer becomes invalid. Using one is undefined behaviour.

Every dangerous line in this file is only DESCRIBED in a comment. The code that runs shows the safe alternatives.

## Full Line-by-Line Breakdown

### SECTION 1: CONST CORRECTNESS
`balance()` is a `const` method, so it can be called on a `const Account` and through a `const Account&`; `deposit()` is not, so the commented-out calls would not compile. `mutable int reads_` lets a const method update bookkeeping (a call counter) that is not part of the object's logical state; the output shows `reads = 1` after a call on a const object. A method returning `const std::string&` to a member gives read-only access without a copy, and is safe while the object lives. `const_cast` can strip `const`, but modifying an object that was defined const through it is undefined behaviour.

Output from a real run:

```text
===== SECTION 1: CONST CORRECTNESS =====
  balance 500 cents
  const object can call const methods: 900
  mutable counter changed through const methods: reads = 1
  label via const&: checking
  const is a compile-time contract: it moves bugs from run time to compile time.
  const_cast can remove const, but modifying a truly const object that way is undefined behaviour.
```

### SECTION 2: DANGLING REFERENCE TRAPS
Three traps are described in comments: returning a reference to a local, a `string_view` over a temporary, and a lambda capturing a local by reference and then outliving it. The safe patterns run: return by value; bind a `const&` to a temporary (its life is extended to the reference's scope, so `extended` prints `hello RDJ`); capture by value (`[start]`), so the returned lambda owns its own copy, and each call increments it (11, 12).

Output from a real run:

```text
===== SECTION 2: DANGLING REFERENCE TRAPS =====
  good_value() = 1 (return by value is safe)
  lifetime extension keeps the temporary alive: hello RDJ
  lambda capture by value survives: 11, 12
```

### SECTION 3: VECTOR REALLOCATION INVALIDATES
The vector is shrunk to exactly 3 elements, so the next `push_back` must reallocate. The code records where the buffer was as an integer (not a usable pointer) and shows that capacity changed and the buffer moved to a new location (a measurement of what this run did). Any pointer, reference or iterator taken before that call is now invalid and is never used. Three safe habits run: re-take the pointer AFTER the growth, remember an INDEX instead (`v[2]` still works after more growth), or `reserve(10)` up front so the pointer never goes stale while you stay within capacity.

Output from a real run:

```text
===== SECTION 3: VECTOR REALLOCATION INVALIDATES =====
  capacity changed after push_back: true
  measurement: the element buffer moved to a new location: true
  re-taken pointer reads 1
  index 2 is still valid after more growth: v[2] = 3
  with reserve(10) the pointer stayed valid: *stable = 1
```

### SECTION 4: ITERATOR INVALIDATION WHILE LOOPING
Inserting or erasing while iterating invalidates iterators. Two bugs are described: `push_back` inside a range-for, and `erase(it)` followed by `++it`. The first working version uses the iterator that `erase` RETURNS, which points at the next valid element. The second uses C++20's `std::erase_if`, which does the whole remove-and-erase correctly in one call. Both leave `1 3 5`.

Output from a real run:

```text
===== SECTION 4: ITERATOR INVALIDATION WHILE LOOPING =====
  erase-in-loop (using the returned iterator): 1 3 5 
  std::erase_if:                              1 3 5 
```

### SECTION 5: WHICH CONTAINERS KEEP REFERENCES VALID
Different containers give different guarantees. `std::list` and `std::map` store each element in its own node, so existing references stay valid when you insert elsewhere. `std::vector` and `std::string` keep elements contiguous and may reallocate, invalidating everything. Always check the container's invalidation rules before keeping a reference across a modification.

Output from a real run:

```text
===== SECTION 5: WHICH CONTAINERS KEEP REFERENCES VALID =====
  list: reference to element survives push_back: 1
  map: reference to element survives inserts: 1
  vector/string use contiguous storage: growth may invalidate EVERYTHING; always check the container's rules.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `final` stops reassigning a variable, not mutating the object | `const` stops modification through that name, and is part of the type (`const T&`, const methods) |
| No const methods | `int balance() const` is enforced by the compiler |
| `ConcurrentModificationException` when a list changes during iteration (usually) | Silent undefined behaviour: the iterator just reads freed memory |
| References never dangle: the GC keeps the object alive | A reference or pointer to a destroyed or moved object dangles |
| `ArrayList` growth is invisible to your references (they point to elements by object reference) | `vector` growth moves the elements: raw pointers/iterators into it become invalid |
| Lambdas capture effectively-final variables by value | `[&]` captures by reference and can dangle; `[=]` / `[x]` captures by value |

## Key Rules / Gotchas Recap
- Make everything `const` that can be: parameters (`const T&`), methods (`... const`), locals.
- `mutable` is for bookkeeping (caches, counters) that does not change the object's logical value.
- Never return a reference or pointer to a local variable.
- A `const&` bound to a temporary extends its life; a `string_view`/pointer does not.
- `push_back`, `insert`, `resize`, `reserve` on a vector may invalidate all pointers, references and iterators into it.
- Do not hold an iterator across an `erase`/`insert`; use the returned iterator or `std::erase_if`.
- Lambdas: capture by value when the closure may outlive the scope.
- `std::list`/`std::map` references survive inserts; `std::vector`'s do not.

## Why This Structure Exists
Const-correctness and lifetime discipline are how big C++ code bases keep thousands of functions safe to change, and invalidated iterators and dangling references are among the most common causes of crashes and exploitable use-after-free bugs. Reading code for these patterns is a core skill in performance engineering and in security review.
