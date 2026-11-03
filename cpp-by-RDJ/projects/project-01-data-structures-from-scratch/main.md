# `main.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`main.cpp` is a demo that prints **measured counts**, not timings. Instrumented element types count their own copies and moves, a counting comparator counts heap comparisons, and the hash map reports its own bucket and chain statistics. Counts from seeded input are deterministic, so the output is identical on every run (verified: two runs compared byte for byte), which timings can never be.

## Full Line-by-Line Breakdown

### Instrumentation helpers
`Counted<Noexcept>` increments static counters in its copy and move operations; the template flag decides whether its move constructor is `noexcept`, which is the whole point of the Section 1 trap. `CountingLess` counts every comparison. `ConstantHash` always returns 7.

### SECTION 1: DynamicArray growth
```text
===== SECTION 1: DynamicArray growth (1000 push_back calls) =====
capacity changes (measurement): 4 -> 8 -> 16 -> 32 -> 64 -> 128 -> 256 -> 512 -> 1024
size=1000 capacity=1024 reallocations=9
noexcept move:  copies=1000 (one per add) moves=1020 (relocation) moves per add=1.020
throwing move:  copies=2020 moves=0   <- TRAP: without noexcept, relocation COPIES instead of moving
```
Capacity doubles 4, 8, ..., 1024: nine reallocations for 1000 pushes. With a `noexcept` move, relocation costs 1020 moves in total (about one per add). Without `noexcept`, `move_if_noexcept` falls back to copying: 2020 copies and no moves.

### SECTION 2: insert at the front, array vs list
```text
===== SECTION 2: insert 1000 items at the FRONT (array shifts, list relinks) =====
DynamicArray: element moves=501520 (each insert shifts the whole tail; n(n-1)/2 = 499500 shifts for n=1000, plus relocation moves)
LinkedList:   element copies=0 moves=1000 (nodes are linked, elements never shift)
after insert(99 before 3) and reverse(): 5 4 3 99 2 1
```
The array must shift its whole tail on every front insert (n(n-1)/2 = 499500 shifts for n = 1000, plus relocation and one extra move per insert, 501520 moves in total). The list links a node and moves each element exactly once into its node. The last line shows `insert` before the third node followed by `reverse()`.

### SECTION 3: HashMap
```text
===== SECTION 3: HashMap (separate chaining, rehash at load factor 0.75) =====
bucket count after each rehash (measurement): 8 -> 16 -> 32 -> 64 -> 128 -> 256 -> 512 -> 1024 -> 2048 -> 4096 -> 8192 -> 16384
10000 sequential int keys: size=10000 buckets=16384 in_use=10000 load=0.610 rehashes=12 longest_chain=1
10000 seeded random int keys: size=10000 buckets=16384 in_use=7546 longest_chain=6
2000 keys that are multiples of 1024: buckets=4096 in_use=128 longest_chain=16
1000 keys, a hash that always returns 7: buckets=2048 in_use=1 longest_chain=1000   <- a linked list in disguise
   still correct: contains(999)=1 contains(1000)=0
word count via operator[]: to=2 be=2 or=1 not=1 size=4
```
Rehash happens at load factor 0.75, doubling 8 -> 16384 for 10000 keys (`rehashes=12`, which counts the very first allocation of 8 buckets). Keys that are multiples of 1024 only use 128 of 4096 buckets (longest chain 16): even with the bit-mixing function, structured keys cluster. The constant-hash map is still correct but is a single chain of 1000.

### SECTION 4: MinHeap
```text
===== SECTION 4: MinHeap (binary heap in an array) =====
12 seeded random ints popped in order: 13 14 14 20 24 26 35 42 50 67 76 78 
n=1000: comparisons for 1000 pushes=2222, for 1000 pops=14971 (reference n*log2(n)=9966)
heapify of the same 1000 items: comparisons=1869 (heapify is O(n); compare with the push count above)
```
Twelve seeded random ints come out sorted. The comparison counts are exact for this seed; heapify needs fewer comparisons than pushing the same 1000 items one by one.

### Complete output (two consecutive runs were byte-identical)
```text
Data structures from scratch: demo (all numbers are counts measured on this run)

===== SECTION 1: DynamicArray growth (1000 push_back calls) =====
capacity changes (measurement): 4 -> 8 -> 16 -> 32 -> 64 -> 128 -> 256 -> 512 -> 1024
size=1000 capacity=1024 reallocations=9
noexcept move:  copies=1000 (one per add) moves=1020 (relocation) moves per add=1.020
throwing move:  copies=2020 moves=0   <- TRAP: without noexcept, relocation COPIES instead of moving

===== SECTION 2: insert 1000 items at the FRONT (array shifts, list relinks) =====
DynamicArray: element moves=501520 (each insert shifts the whole tail; n(n-1)/2 = 499500 shifts for n=1000, plus relocation moves)
LinkedList:   element copies=0 moves=1000 (nodes are linked, elements never shift)
after insert(99 before 3) and reverse(): 5 4 3 99 2 1 

===== SECTION 3: HashMap (separate chaining, rehash at load factor 0.75) =====
bucket count after each rehash (measurement): 8 -> 16 -> 32 -> 64 -> 128 -> 256 -> 512 -> 1024 -> 2048 -> 4096 -> 8192 -> 16384
10000 sequential int keys: size=10000 buckets=16384 in_use=10000 load=0.610 rehashes=12 longest_chain=1
10000 seeded random int keys: size=10000 buckets=16384 in_use=7546 longest_chain=6
2000 keys that are multiples of 1024: buckets=4096 in_use=128 longest_chain=16
1000 keys, a hash that always returns 7: buckets=2048 in_use=1 longest_chain=1000   <- a linked list in disguise
   still correct: contains(999)=1 contains(1000)=0
word count via operator[]: to=2 be=2 or=1 not=1 size=4

===== SECTION 4: MinHeap (binary heap in an array) =====
12 seeded random ints popped in order: 13 14 14 20 24 26 35 42 50 67 76 78 
n=1000: comparisons for 1000 pushes=2222, for 1000 pops=14971 (reference n*log2(n)=9966)
heapify of the same 1000 items: comparisons=1869 (heapify is O(n); compare with the push count above)

Done.
```

## Key Differences From Java
| Java | C++ here |
|---|---|
| Measure allocations with a profiler or `System.nanoTime` | Count copies and moves with an instrumented type: exact and deterministic |
| Autoboxing hides object creation | `Counted` shows each value being copied or moved |
| `Collections` growth is invisible | `reallocation_count()` and `bucket_count()` expose growth |

## Key Rules / Gotchas Recap
- Print counts, not timings, when you want a reproducible result.
- Seed every random generator explicitly (`std::mt19937 rng(42)`).
- `noexcept` on a move constructor changes what generic containers do.

## Why This Structure Exists
Measuring *what the code does* (copies, comparisons, chain lengths) before measuring *how long it takes* is how performance work stays honest and reproducible, whether you are tuning an inference pipeline or a parser.
