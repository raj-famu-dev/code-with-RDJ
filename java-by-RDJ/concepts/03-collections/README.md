# 03 · Collections Framework

**Priority: NOW.** Everything after this folder (streams, Spring, the projects) is built on collections.

Convention: one `_N_Name.java` (sectioned, runnable) plus one `_N_Name.md` (line-by-line walkthrough) per topic, same as `01-basics` and `02-oop`.

## Planned files

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_CollectionsFrameworkOverview` | Where do `List`, `Set`, `Queue`, `Map` sit in the hierarchy, and why is `Map` not a `Collection`? | 📘 |
| 2 | `_2_ArrayList` | How does it grow? Cost of add at end, add at index 0, `get(i)`, `remove(i)`? | 📘 |
| 3 | `_3_LinkedList` | Why is `get(i)` slow? When is it genuinely faster than `ArrayList`? | 📘 |
| 4 | `_4_HashSet` | How do `hashCode` and `equals` (see `02-oop/_12`) decide what counts as a duplicate? | 📘 |
| 5 | `_5_LinkedHashSetAndTreeSet` | What ordering does each guarantee, and what does `TreeSet` require of its elements? | 📘 |
| 6 | `_6_HashMap` | `put`, `get`, `getOrDefault`, `merge`, `computeIfAbsent`, iterating `entrySet()` | 📘 |
| 7 | `_7_HashMapInternals` | Buckets, collisions, load factor, resizing, long buckets turning into trees | 📘 |
| 8 | `_8_LinkedHashMapAndTreeMap` | Insertion order vs access order vs sorted keys, and the navigation methods | 📘 |
| 9 | `_9_QueueDequePriorityQueue` | FIFO vs LIFO, `ArrayDeque` vs `Stack`, how a `PriorityQueue` orders elements | 📘 |
| 10 | `_10_Iterators` | `Iterator.remove()`, fail-fast behavior, reproduce `ConcurrentModificationException` | 📘 |
| 11 | `_11_ComparableVsComparator` | Natural vs custom ordering, `Comparator.comparing(...).thenComparing(...)` | 📘 |
| 12 | `_12_UtilityAndImmutableCollections` | `Collections` helpers, `List.of` vs `Arrays.asList` vs `unmodifiableList` | 📘 |
| 13 | `_13_CollectionsCapstone` | Word-frequency counter, LRU cache, and a ranked leaderboard in one program | 📘 |

## Traps to hit on purpose (write a failing example, then fix it)
- Modifying a list while looping over it
- Using a mutable object as a `HashMap` key, then changing it
- `equals` overridden without `hashCode`
- `List<Integer>.remove(1)` vs `remove(Integer.valueOf(1))`
- `Arrays.asList(...)` is fixed-size; `List.of(...)` is immutable

## Exit test (answer from memory, no code open)
1. Walk through what happens inside `HashMap.put("a", 1)` step by step.
2. Pick the right collection for: unique names in insertion order; top-K scores; undo history; cache with eviction.
3. Give the time complexity of the main operations of `ArrayList`, `LinkedList`, `HashMap`, `TreeMap`, `PriorityQueue`.
4. Why does `ConcurrentModificationException` exist?

📘 = reference file and walkthrough committed (compiled and run). Do not mark a row ✅ until you have retyped the file, broken it on purpose, and rewritten its `.md` in your own words.
