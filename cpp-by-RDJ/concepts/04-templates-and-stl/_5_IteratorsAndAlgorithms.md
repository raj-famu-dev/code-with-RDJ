# `_5_IteratorsAndAlgorithms.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
An iterator is a small object that points into a container and can move. Algorithms such as `std::sort`, `std::find_if`, `std::transform` and `std::accumulate` work on ranges of iterators and know nothing about the container itself, so one algorithm works for many containers. C++20 `std::ranges` lets you pass the container directly and build lazy pipelines of views.

## Full Line-by-Line Breakdown

### SECTION 1: iterator categories
Iterators come in categories with increasing power: input/output, forward (singly linked list), bidirectional (`list`, `map`), random access (`vector`, `deque`, arrays) and contiguous. The program tests them with the C++20 iterator concepts. `std::sort` needs random access because it jumps around, so it cannot be used on a `std::list` (that is a compile error; use the member `list.sort()`). `std::distance` and `std::next` work with every category, but run in O(1) only for random access.

Output from a real run:

```text
===== SECTION 1: iterator categories =====
vector  : random_access=true bidirectional=true
list    : random_access=false bidirectional=true
fwd_list: bidirectional=false forward=true
std::sort needs random access, so std::sort on a std::list does not compile; use list.sort().
list.sort(): 1 2 3
std::distance (O(1) for random access) = 4, std::next(begin,2) = 30
```

### SECTION 2: core algorithms
`sort` with `std::greater<>{}` sorts descending; `find_if` takes a predicate lambda and returns an iterator (compare to `end()` before dereferencing in real code); `transform` writes results to an output range (the output must already have room: `squares(v.size())`); `accumulate` folds a range. Trap: `accumulate`'s return type is the type of the INITIAL value, so summing `{0.5, 0.5}` starting from `0` (an `int`) gives 0, whereas starting from `0.0` gives 1. (An earlier draft of this file passed `begin()` and `end()` from two different temporaries; AddressSanitizer caught the heap overflow, and the final code uses one named vector.)

Output from a real run:

```text
===== SECTION 2: core algorithms =====
sorted: 1 2 3 5 7 9
sorted descending: 9 7 5 3 2 1
first multiple of 3: 9 at index 0
squares: 81 49 25 9 4 1
accumulate sum = 27, product of first 3 = 315
count_if even = 1, any_of > 8: true
accumulate trap: the start value's type decides the result type: accumulate({0.5,0.5}, 0) = 0 (int start truncates each partial sum)
accumulate(dv, 0.0) = 1
```

### SECTION 3: erase-remove idiom
`std::remove` does not remove anything: it moves the kept elements to the front and returns the new logical end; the container's size is unchanged. You must follow it with `erase(newEnd, end)`. The program shows the size still 6 after `remove`, the kept range `1 3 4`, then three equivalent ways: the manual two-step, the one-liner `a.erase(std::remove(...), a.end())`, and the C++20 `std::erase(c, 2)` / `std::erase_if` which do it in one call. Erasing in a range-`for` over the same vector invalidates its iterators and is undefined behaviour, so it is not demonstrated.

Output from a real run:

```text
===== SECTION 3: erase-remove idiom =====
after std::remove ALONE size is still 6 (remove only shuffles kept elements to the front)
kept range [begin,newEnd): 1 3 4 
after erase(newEnd, end): 1 3 4
erase-remove one-liner: 1 3 4
C++20 std::erase removed 3 elements: 1 3 4
erase_if odd kept: 1 3 5
Trap: erasing inside a range-for over the same vector invalidates iterators (undefined behaviour); use erase-remove / erase_if.
```

### SECTION 4: std::ranges basics
A view pipeline (`data | views::filter(...) | views::transform(...)`) is lazy: after building it the predicate had been called 0 times; one pass over it called the predicate 8 times (once per element), and no copy of the data was made. Do not modify the underlying container while a view over it is alive. `std::ranges::sort(words, comp)` and `ranges::find(data, 4)` take the container directly. `ranges::find` on a TEMPORARY container returns `std::ranges::dangling` instead of an iterator, so using it is a compile error: the library turns a dangling-iterator bug into a compile-time check.

Output from a real run:

```text
===== SECTION 4: std::ranges basics =====
pipeline built; predicate calls so far = 0 (views are LAZY: nothing ran yet)
iterating evens*10: 20 40 60 80
predicate calls after one pass = 8 (work happens while iterating; data was not copied)
Rule: do not modify the underlying container while a view over it is alive.
ranges::sort by length: fig pear banana
ranges::find(data, 4) found at index 3
find on a TEMPORARY returns std::ranges::dangling (not an iterator): true
iota 1, iota 2, iota 3
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `Iterator<T>` has `hasNext()`/`next()` | Iterators work like pointers: `*it`, `++it`, compared against `end()` |
| Streams: `list.stream().filter(...).map(...)` | `std::views::filter`/`transform` (lazy, no allocation) or algorithms |
| `Collections.sort(list)` | `std::sort(v.begin(), v.end())` or `std::ranges::sort(v)` |
| `list.removeIf(pred)` | `std::erase_if(v, pred)` (C++20); older: erase-remove |
| `ConcurrentModificationException` when changing a list while iterating | Silent undefined behaviour (invalidated iterators); no exception |
| Generics erased: streams box primitives (`IntStream` exists to avoid it) | Algorithms are templates on the iterator type, no boxing |
| Lambdas capture effectively-final variables | Lambdas choose capture mode explicitly (next file) |
| `Comparator` objects | Lambdas/functors as comparators (file 7) |

Related Java points for this topic:
- equals/hashCode: `std::find(b, e, value)` and `std::remove(b, e, value)` compare with `operator==`, like `List.indexOf`/`remove(Object)` call `equals`; no hash is involved.
- Collections: Java `Collection.removeIf` and `Collections.sort` are methods on the collection; C++ algorithms are free functions over iterator pairs, so they also work on plain arrays.

## Key Rules / Gotchas Recap
- `std::remove` + `erase`, or `std::erase`/`erase_if` in C++20.
- Algorithms take half-open ranges `[begin, end)`.
- Output ranges must already have space (`transform` into `v.size()` elements, or use `std::back_inserter`).
- `accumulate` result type = type of the init value.
- Check `it != end()` before dereferencing.
- Views are lazy and non-owning; the underlying data must outlive them and stay unchanged.
- `sort` needs random-access iterators.

## Why This Structure Exists
Data-processing code in AI and security tooling (log parsing, tokenization, feature filtering) is mostly "filter, map, reduce, sort" over large ranges. Algorithms plus lazy views express that without hand-written loops or temporary copies, and knowing iterator rules prevents invalidation bugs.
