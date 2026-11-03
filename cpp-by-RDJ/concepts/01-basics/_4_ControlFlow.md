# `_4_ControlFlow.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
C++ control flow looks like Java's (`if`, `switch`, `for`, `while`, `do-while`), with a few modern additions that make it safer: `if` and `switch` can declare a variable that exists only inside them, range-based `for` walks containers without indices, and `[[fallthrough]]` documents an intentional fall into the next `case`. The main trap is that you choose, per loop, whether the loop variable is a copy or a reference.

## Full Line-by-Line Breakdown

### SECTION 1: if WITH INITIALISER
`if (auto it = stock.find("apple"); it != stock.end())` declares `it` and tests it in one statement; `it` is visible in the `if` and `else` branches but nowhere after, so a stale iterator cannot leak into later code. `find` returns an iterator to the match or `end()` when missing.

Output from a real run:

```text
===== SECTION 1: if WITH INITIALISER =====
apple count = 3
kiwi not stocked
```

### SECTION 2: switch AND [[fallthrough]]
In a `switch`, execution continues into the next `case` unless you `break` or `return`. In `describe`, `High` deliberately falls into `Medium`, so it prints `alert log`. The `[[fallthrough]];` attribute says "I meant that", and without it `-Wextra` warns about implicit fallthrough. `describe_no_fall` shows the safer style: every case returns. `switch` works only on integers and enums (not strings).

Output from a real run:

```text
===== SECTION 2: switch AND [[fallthrough]] =====
High   -> alert log 
Medium -> log 
Low    -> ignore 
no-fallthrough High -> alert
```

### SECTION 3: RANGE-BASED for
`for (int x : v)` makes a COPY of each element, so `x *= 10` changes the copy and the vector stays `1 2 3 4`. `for (int& x : v)` binds a reference, so the elements really become `10 20 30 40`. For big types read-only, write `const auto&` to avoid copying every string. `for (const auto& [k, val] : stock)` uses structured bindings to unpack a map entry (the map iterates in sorted key order).

Output from a real run:

```text
===== SECTION 3: RANGE-BASED for =====
after by-value loop:     1 2 3 4 
after by-reference loop: 10 20 30 40 
Ada(3) Linus(5) Grace(5) 
apple=3 pear=0 
```

### SECTION 4: LOOPS, break, continue
`continue` skips to the next iteration (evens are skipped) and `break` exits the loop (after 7). The `while` loop computes the Collatz step count for 27 (111, a known value you can verify by hand or with any other language). `do { } while` always runs the body once. The last loop indexes with `std::size_t`, matching `v.size()`'s unsigned type; using `int` there would trigger a signed/unsigned comparison warning.

Output from a real run:

```text
===== SECTION 4: LOOPS, break, continue =====
sum of odd numbers up to 7 = 16
Collatz steps for 27 = 111
3 2 1 liftoff
10,20,30,40
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `for (String n : names)` (always a reference to the object) | `for (const auto& n : names)`: you pick copy (`auto`) or reference (`auto&`) |
| `switch` on strings, enums, and arrow-form expressions | `switch` on integers and enums only; no arrow form |
| No implicit fallthrough warning needed in arrow form | Fallthrough is silent unless `-Wextra` or `[[fallthrough]]` |
| Variable declared before `if` leaks into the scope | `if (init; cond)` scopes the variable to the `if` |
| `Map.Entry<K,V> e : map.entrySet()` | `for (const auto& [k, v] : map)` |
| Conditions must be `boolean` | Any integer or pointer converts to bool: `if (x = 5)` compiles |

## Key Rules / Gotchas Recap
- `for (T x : v)` copies; `for (T& x : v)` modifies; `for (const T& x : v)` reads without copying.
- Every `case` needs `break`/`return`, or `[[fallthrough]]` when intended.
- `switch` cannot take a `std::string`.
- Use `if (init; cond)` to keep variables tightly scoped.
- Do not modify a container's size while looping over it with range-for (iterator invalidation; see 02-pointers-and-memory/_8).
- Compare index variables with `std::size_t` to match `.size()`.

## Why This Structure Exists
Reading and writing loops correctly, including who owns each element, is the basis of every data-processing pipeline and of performance work: copying a large object on every iteration is a classic hidden slowdown in numeric and AI code. Tight variable scopes also reduce the use-after-scope bugs that security reviews look for.
