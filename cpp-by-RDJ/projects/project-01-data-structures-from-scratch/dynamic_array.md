# `dynamic_array.hpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`DynamicArray<T>` is a growable array built from nothing but raw memory: it asks `std::allocator<T>` for an uninitialised block, builds elements into it one at a time with `std::construct_at`, and doubles the block when it is full. That is exactly what `std::vector` (and Java's `ArrayList`) does underneath. Writing it yourself shows why `push_back` is "O(1) amortised", why a `noexcept` move constructor matters, and what the rule of five really protects.

## Full Line-by-Line Breakdown

### Members and the three numbers
`data_` points at the block, `size_` is how many elements are alive, `capacity_` is how many fit. Memory between `size_` and `capacity_` is raw: no object lives there, so nothing may be read or destroyed there. `reallocations_` counts how often the block was replaced (used by the demo). `alloc_` is the `std::allocator<T>`; `[[no_unique_address]]` lets the empty allocator take no space.

### Constructors, destructor, copy, move (the rule of five)
- The initializer-list and copy constructors start with `: DynamicArray()`. That *delegating* call finishes constructing an empty object first, so if a later copy throws, the destructor still runs and frees what was built. A plain constructor that throws halfway would leak.
- The move constructor steals the pointer and counters with `std::exchange`, leaving the source as a valid empty array. It is `noexcept`, which is what lets containers of `DynamicArray` move instead of copy.
- Copy assignment is copy-and-swap: build a copy (this may throw, and `*this` is untouched if it does), then `swap`. Move assignment moves into a temporary and swaps, so the old buffer is freed when the temporary dies. Both survive `a = a`.
- The destructor calls `release()`: destroy every live element with `std::destroy_at`, then give the block back.

### `emplace_back`, growth and the aliasing trap
When there is room, the new element is built in place with `std::construct_at(data_ + size_, args...)`. When the array is full, a new block of double the size is allocated and **the new element is built first**, then the old elements are moved across. Why the order? `a.push_back(a[0])` passes a reference *into the old block*; if we moved the old elements first and freed that block, the reference would dangle. `tests.cpp` checks this case with strings (`test_dynamic_array_strings_and_aliasing`).

The capacity sequence printed by the demo shows the doubling:

```text
===== SECTION 1: DynamicArray growth (1000 push_back calls) =====
capacity changes (measurement): 4 -> 8 -> 16 -> 32 -> 64 -> 128 -> 256 -> 512 -> 1024
size=1000 capacity=1024 reallocations=9
noexcept move:  copies=1000 (one per add) moves=1020 (relocation) moves per add=1.020
throwing move:  copies=2020 moves=0   <- TRAP: without noexcept, relocation COPIES instead of moving
```

Doubling is why `push_back` is amortised O(1): 1000 pushes caused 9 reallocations, and the relocation work (`moves=1020`, about 1 move per add) is a small constant on top of the one copy per add.

### `adopt` and `std::move_if_noexcept` (the TRAP)
`adopt` moves the live elements into the new block. It uses `std::move_if_noexcept`, which *moves* only if the move constructor is `noexcept` and otherwise *copies*. If a move could throw halfway, the old array would be half-emptied and impossible to restore; copying leaves the old block intact so we can roll back. The demo's last line shows the price of forgetting `noexcept`: relocation copied every element (2020 copies, 0 moves) instead of moving. `tests.cpp` proves the strong guarantee: a copy that throws while relocating leaves `size`, `capacity` and the contents unchanged, and no element leaks (`test_dynamic_array_bounds_and_exceptions`).

### `insert`, `erase`, `at`
`insert(index, value)` first makes room at the end by building a new last element from the old last one, then shifts the rest of the tail right with move assignment and move-assigns the value into the gap: O(n). `erase` shifts left and pops. `at` and the index checks throw `std::out_of_range`; `operator[]` does no check (like `vector`).

### Iterators
A raw pointer already behaves as a random-access iterator, so `begin()` returns `data_` and `end()` returns `data_ + size_`. That is why range-for and `std::sort` work on it.

## Key Differences From Java
| Java `ArrayList<T>` | C++ `DynamicArray<T>` |
|---|---|
| Stores references to objects (`Object[]`) | Stores the objects themselves, contiguous in memory |
| Garbage collector frees removed objects | `std::destroy_at` runs the destructor right now; the block is freed explicitly |
| Growing copies references (cheap) | Growing moves or copies whole objects; `noexcept` on the move decides which |
| No copy constructor question: assignment copies the reference | Copy, move and assignment are all yours to define (rule of five) |
| `list.add(list.get(0))` is always safe | `v.push_back(v[0])` is only safe because we construct the new element before relocating |
| `IndexOutOfBoundsException` always | `operator[]` unchecked, `at()` checked |

## Key Rules / Gotchas Recap
- Raw capacity is not alive: only `[0, size_)` holds objects.
- Build the new element before moving the old ones (aliasing).
- Mark move constructors `noexcept`, or growth silently copies.
- Delegate to the default constructor so a throwing copy still runs the destructor.
- Self-assignment (`a = a`) must be harmless.

## Why This Structure Exists
Contiguous storage is the layout that CPU caches and vectorised numeric code (tensors, buffers, parsers) depend on, and the lifetime rules shown here (construct, move, destroy, strong exception safety) are the same ones that decide whether a systems or security tool leaks, crashes or corrupts memory.
