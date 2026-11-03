# `_7_ComparatorsAndHashing.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Containers need to know how to compare and identify your types. Ordered containers (`map`, `set`, `priority_queue`, `sort`) use a comparator that must be a "strict weak ordering". Unordered containers (`unordered_map`, `unordered_set`) need a hash function and an equality test that agree: equal values must produce equal hashes.

This is the C++ version of Java's `Comparator` and `equals`/`hashCode` contract.

## Full Line-by-Line Breakdown

### SECTION 1: comparators for ordered containers
`std::map<int, std::string, std::greater<int>>` iterates from the largest key to the smallest. `CaseInsensitiveLess` is a functor (a struct with `operator()`), so `"BOB"` and `"alice"` are equivalent to the already-inserted `"bob"` and `"Alice"` and are not inserted (set size 3). The `Person` set uses a lambda comparator on age only: `Cy` (age 30) is dropped because `Ann` already has age 30, since a set treats `!(a<b) && !(b<a)` as "same". A lambda comparator needs `decltype(byAge)` as the template argument and the lambda passed to the constructor. A strict weak ordering means `comp(x, x)` is false, and consistent transitivity: writing `<=` instead of `<` violates this and is undefined behaviour in `sort` and in ordered containers (not run here).

Output from a real run:

```text
===== SECTION 1: comparators for ordered containers =====
map<int,..., std::greater> iterates: 3:three 2:two 1:one
case-insensitive set size = 3: Alice bob Carol ("BOB" and "alice" were equal under the comparator, so they were not inserted)
set by age (lambda comparator) has 2 people: Cy was dropped because age 30 already exists (equivalence = !(a<b) && !(b<a)).
Java: TreeSet(Comparator) behaves the same way: compare()==0 means duplicate.
Rule: comparators must be a strict weak ordering. `a.age <= b.age` breaks it (comp(x,x) must be false) and is undefined behaviour in std::sort/set.
```

### SECTION 2: priority_queue with a comparator
`priority_queue` is a max-heap: with the default `std::less` the largest element is on top. Adding `std::greater` flips it to a min-heap, the standard way to get "smallest first" (Java's `PriorityQueue` is a min-heap by default; this is the opposite default). `TaskLess` orders `Task` by priority, then by label; because the queue pops the greatest element, `a.label > b.label` makes the alphabetically earlier label come out first among equal priorities: `5/deploy` before `5/fix-bug`.

Output from a real run:

```text
===== SECTION 2: priority_queue with a comparator =====
default priority_queue<int> pops the LARGEST first: 9 7 4 1
with std::greater it pops the SMALLEST first: 1 4 7 9
tasks by priority then label: 5/deploy 5/fix-bug 2/write 1/relax
(Trap: the comparator's meaning is inverted vs sorting: 'less' puts the item at the BOTTOM, so max-heap pops the greatest.)
```

### SECTION 3: custom hash + equality
`Point` defines `==`. `PointHash` mixes the hash of `x` and `y` with a standard "hash combine" step so `{1,2}` and `{2,1}` differ. It is passed as the third template argument of `unordered_map`. Writing to `grid[{1,2}]` twice overwrote the same entry (size 2), and `contains({2,1})` is false because order matters. You can also specialize `std::hash<Point>` once so you never need the extra argument. The contract is exactly Java's: `a == b` must imply `hash(a) == hash(b)`.

Output from a real run:

```text
===== SECTION 3: custom hash + equality =====
size = 2, grid[{1,2}] = oak, contains {3,4}: true, contains {2,1}: false (order of x,y matters)
hash of same value twice is equal: true, hash({1,2}) != hash({2,1}): true
Java parallel: equals(Object) <-> operator==, hashCode() <-> the hash functor. Contract: a == b implies hash(a) == hash(b).
(In C++ you can also specialize std::hash<Point> so no third template argument is needed.)
```

### SECTION 4: the inconsistent-hash trap
`Tagged` considers two objects equal when `id` matches, but `BadTaggedHash` also hashes `note`. Insert `{1,"first"}`, then ask for `{1,"other"}`: `==` says they are equal, but their hashes differ, so the container looks in a different place and answers `false`. Nothing crashes or warns; the container is just wrong. `GoodTaggedHash` hashes only the fields `==` compares, and the lookup succeeds. Caveat: with a bad hash the failure depends on bucket layout, so it could pass by accident on another implementation or data set; the printed result is what this run produced.

Output from a real run:

```text
===== SECTION 4: the inconsistent-hash trap =====
BadTaggedHash: contains({1, "other"}) = false (== says equal, but the hashes differ so the lookup looks in the wrong bucket)
GoodTaggedHash: contains({1, "other"}) = true (hash uses only the fields that == uses)
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `Comparator<T>.compare(a, b)` returns negative/zero/positive | Comparator returns `bool` "a goes before b" (strict weak ordering) |
| `TreeMap(Comparator)`, `list.sort(Comparator)` | `map<K,V,Cmp>`, `std::sort(b, e, cmp)` |
| `PriorityQueue` is a MIN-heap by default | `priority_queue` is a MAX-heap by default (`std::greater` for min) |
| Comparator type is an interface; generics are erased | The comparator is a template parameter: a distinct type, inlined, no erasure |
| `equals(Object)` + `hashCode()` overridden in the class | `operator==` in the class, hash as a separate functor or `std::hash` specialization |
| `Objects.hash(a, b)` | Write your own combine (the standard has no `hash_combine`) |
| `HashMap` of mutable keys breaks silently if the hash changes | Same danger: do not change fields used in `==`/hash while the object is a key |
| `compare()==0` means TreeSet duplicates | Equivalence `!(a<b)&&!(b<a)` means duplicates |
| Collections hold references | Containers hold values; keys are copied in |

## Key Rules / Gotchas Recap
- Comparators must be strict weak orderings: `comp(x,x)` is false; never use `<=`.
- Ordered containers define "equal" through the comparator alone, not through `==`.
- Hash and `==` must agree: hash exactly the fields that `==` uses.
- `priority_queue` pops the greatest by default.
- Unordered iteration order is unspecified; sort before printing.
- Changing a key's fields after insertion corrupts the container.

## Why This Structure Exists
Schedulers, graph algorithms (Dijkstra's min-heap), caches and deduplication all depend on correct ordering and hashing. A wrong hash is also a classic denial-of-service surface in security work (hash flooding), so understanding how hashing works is directly useful.
