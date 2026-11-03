# `_3_SequenceContainers.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
The standard library gives you four main sequence containers: `std::vector` (a growable contiguous array), `std::deque` (chunks with cheap insertion at both ends), `std::list` (doubly linked nodes) and `std::array` (a fixed-size array). Which one you choose decides how many element copies, moves and allocations your program performs.

This file checks the textbook complexity claims by COUNTING element moves and copies with an instrumented type, not by timing. No timings are printed or claimed.

## Full Line-by-Line Breakdown

### SECTION 1: std::vector
Pushing 1000 ints one at a time into a `std::vector` caused 11 reallocations in this standard library (g++ 13's libstdc++). That number is a measurement of this implementation: the standard only requires "amortized constant time", and capacity grows geometrically, which is why it is far below 1000. With `reserve(1000)` first, the data pointer never changed. The trap: when a vector reallocates, every pointer, reference and iterator into it becomes invalid; the demo shows the buffer moved after `reserve(100)` on a 3-element vector, comparing pointers only (addresses are never printed).

Output from a real run:

```text
===== SECTION 1: std::vector =====
after 1000 push_back: size=1000, capacity>=size: 1
number of reallocations for 1000 push_backs: 11 (a measurement of THIS standard library; far fewer than 1000 because capacity grows geometrically)
with reserve(1000) the buffer never moved: true
Trap: after growth, old pointers/iterators are invalid; the buffer moved: true (pointer comparison only, address not printed)
```

### SECTION 2: cost of inserting at the front and middle (counted)
`Counted` is an element type whose copy and move operations increment counters. Building each container with n elements and then inserting one at the FRONT:

- `vector`: 1001 operations for n = 1000 and 2001 for n = 2000. That is n element moves (shifting everything up by one) plus 1 for the new element: O(n), confirmed because it grew with n.
- `deque`: 1 operation (just placing the new element; nothing is shifted).
- `list`: 1 operation (link a new node; the 1 is moving the temporary into the node).

Inserting in the MIDDLE (n = 1000) cost 501 and 502 operations for vector and deque: about half the elements move. `list` is not measured there because reaching the middle needs an iterator walk, which is O(n) traversal but moves no elements.

Output from a real run:

```text
===== SECTION 2: cost of inserting at the front (counted element moves/copies, n=1000) =====
vector: 1001 ops  (shifts every element: O(n))
deque : 1 ops  (insert at either end of a deque is O(1))
list  : 1 ops  (relinks nodes: O(1))
vector with n=2000: 2001 ops (it grew with n; the list stayed at 1)
insert in the MIDDLE (n=1000): vector 501 ops, deque 502 ops (both shift elements: O(n); roughly half the elements move)
deque push_front/push_back both O(1): 1 2 3 
```

### SECTION 3: append cost and element access
Appending to a deque or list does not touch existing elements (0 operations). A vector with spare capacity also takes 0 operations, but a vector at full capacity moved its 4 old elements into a new buffer: that is the reallocation cost that "amortized O(1)" averages out. `std::list` has no `operator[]`; reaching the third element means walking nodes (`std::next`), while `vector` indexes directly.

Output from a real run:

```text
===== SECTION 3: append cost and element access =====
appending to a deque/list never relocates existing elements: deque ops = 0, list ops = 0 (n=1000)
vector with spare capacity, emplace_back ops: 0 (amortized O(1): no shifting)
vector at full capacity, emplace_back ops: 4 (reallocation moved/copied the old elements)
list has no operator[]; reaching element 2 means walking: *std::next(l.begin(), 2) = 30
vector r[2] = 30 (O(1) random access)
```

### SECTION 4: std::array and the complexity table
`std::array<int,4>` has its size in its type, lives wherever you declare it (no heap allocation), and `sizeof` is 16. `at()` is bounds-checked and throws; `operator[]` is not checked. The table summarizes the standard's guarantees:

| operation | vector | deque | list | array |
|---|---|---|---|---|
| random access | O(1) | O(1) | O(n) | O(1) |
| push_back | amortized O(1) | O(1) | O(1) | n/a |
| push_front | O(n) | O(1) | O(1) | n/a |
| insert in middle | O(n) | O(n) | O(1) once you hold the iterator | n/a |
| contiguous memory | yes | no | no | yes |

The experiments above verified the front, middle and append behavior of vector, deque and list. Random access and contiguity are properties of the interface and layout, not counted here. Default choice: `std::vector`, because contiguous memory is friendly to CPU caches; switch only when you have a reason (and a measurement).

Output from a real run:

```text
===== SECTION 4: std::array and the complexity table =====
std::array<int,4>: size 4 fixed at compile time, sizeof = 16 (no heap allocation, no growth)
a.at(3) = 4; a.at(4) threw out_of_range

standard guarantees (the counts above confirm the vector/deque/list front, middle and append rows):
  op                 vector      deque       list        array
  random access      O(1)        O(1)        O(n)        O(1)
  push_back          amort O(1)  O(1)        O(1)        n/a
  push_front         O(n)        O(1)        O(1)        n/a
  insert in middle   O(n)        O(n)        O(1)*       n/a
  contiguous memory  yes         no          no          yes
  (* O(1) once you HAVE the iterator; finding it is O(n))
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `ArrayList<Integer>` stores references to boxed objects | `vector<int>` stores the ints themselves, contiguously |
| `LinkedList<E>` is also a Deque | `std::list` (doubly linked) and `std::deque` are separate types; `std::forward_list` is singly linked |
| `ArrayList.get(i)` bounds-checked, throws | `v[i]` is unchecked (undefined behaviour out of range), `v.at(i)` throws |
| Collections hold references; copying a list copies references | Containers hold VALUES; copying a vector copies every element (use `std::move` or references) |
| Fixed array `int[]` is an object with `.length` | `std::array<int,N>` (size in the type) and C arrays (decay to pointers, avoid) |
| Garbage collector frees nodes | Container destructor frees elements; no GC |
| Generic types are erased; `List<Integer>` boxes | Generic types are instantiated per element type; no boxing |
| `ArrayList` growth hidden | `reserve`, `capacity`, `shrink_to_fit` are explicit tools |

Related Java points for this topic:
- Comparator: sorting a `std::vector` takes a comparator lambda just as `list.sort(Comparator)` does (file 7 covers writing them).
- equals/hashCode: `std::find` and `std::vector::operator==` use the element's `operator==`, where Java's `contains`/`indexOf` call `equals`; you never need a hash for sequence containers.

## Key Rules / Gotchas Recap
- Default to `std::vector`; call `reserve` when you know the size.
- Growth invalidates iterators, pointers and references into a vector.
- `list` and `deque` have different invalidation rules; read the reference before storing iterators.
- `operator[]` does not check bounds; `at()` does.
- Do not trust Big-O alone: contiguous memory often beats lower-complexity node-based structures. Measure before switching (this file deliberately does not).
- Prefer `emplace_back` to construct in place; mark move constructors `noexcept` so vectors move instead of copy during growth.

## Why This Structure Exists
Memory layout and copy counts are the foundation of performance work in inference pipelines and data processing. Instrumented types like `Counted` are a quick, honest way to learn what a data structure costs without guessing, and invalidation bugs are a common source of real memory-safety vulnerabilities.
