# `_4_AssociativeContainers.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Associative containers look things up by key instead of by position. The ordered family (`std::map`, `std::set`, `std::multimap`) keeps keys sorted in a balanced tree: O(log n) operations and sorted iteration. The unordered family (`std::unordered_map`, `std::unordered_set`) hashes keys into buckets: average O(1) lookups and no order.

The ordering-vs-hashing choice and one infamous trap (`operator[]` inserts) are what you must understand to use them correctly.

## Full Line-by-Line Breakdown

### SECTION 1: map and set (ordered)
The map was filled out of order but iterates alphabetically by key (`adam`, `mia`, `zoe`). The set drops duplicates and keeps values sorted. `lower_bound(2)` finds the first element not less than 2, an operation that only exists because the data is ordered. `insert` does NOT overwrite an existing key (it returns a pair whose `.second` is false); `insert_or_assign` does.

Output from a real run:

```text
===== SECTION 1: map and set (ordered) =====
map iterates in KEY order: adam=25 mia=40 zoe=31
set of {5,1,3,3,1} keeps unique sorted values: 1 3 5
lower_bound(2) in set = 3 (first element not less than 2: possible only because it is ordered)
insert({"mia",99}) did insert? false, mia is still 40 (insert does not overwrite)
insert_or_assign overwrote: mia = 41
```

### SECTION 2: the operator[] insertion trap
`stock["pear"]` looks like a read, but if the key is missing `operator[]` default-constructs a value (0 for int) and INSERTS it. The size grew from 1 to 2 just from reading. Use `contains` (C++20) or `find` to test for presence, and `at` when a missing key is a bug (it throws `out_of_range`). `operator[]` is not even available on a `const` map. It is the right tool when you want insertion, such as `++counts[word]`.

Output from a real run:

```text
===== SECTION 2: the operator[] insertion trap =====
size before: 1
read stock["pear"] = 0, size after: 2 (a lookup changed the map!)
contains("kiwi") = false, size still 2 (contains/find do not insert)
find("kiwi") == end(): true
at("kiwi") throws out_of_range for missing keys
frozen["b"] would not compile on a const map; use at/find. Counting words idiom: ++counts[word] (the insertion IS wanted there).
```

### SECTION 3: unordered_map and unordered_set (hashing)
Lookup is by hash. The iteration order of an unordered container is unspecified and may differ between implementations or even versions, so the program copies the keys into a vector and sorts them before printing, which keeps the output stable. The set removes duplicates; `load_factor` stays at or below `max_load_factor` because the table rehashes (grows its bucket array) as elements are added. There is no `lower_bound`: hashing throws away order.

Output from a real run:

```text
===== SECTION 3: unordered_map and unordered_set (hashing) =====
lookup h["mia"] via find: 40, size 4
iteration order of an unordered_map is unspecified; sorted keys: adam leo mia zoe
unordered_set of {3,1,3,2} has size 3 (duplicates removed), contains(2) = true
load_factor <= max_load_factor: true (rehashing keeps buckets roughly sized to the element count)
No lower_bound / range-by-order on unordered containers: hashing destroys order.
```

### SECTION 4: multimap
`std::multimap` allows several values per key. `count` and `equal_range` retrieve them all; equal keys keep their insertion order. It has no `operator[]`, since there is no single value to return.

Output from a real run:

```text
===== SECTION 4: multimap =====
count("cpp") = 3, size = 4
all values for cpp (insertion order kept among equal keys): templates stl raii
multimap has no operator[] (which value would it mean?).

Choosing: ordered needs operator< (O(log n), sorted iteration, range queries); unordered needs hash + == (average O(1), no order).
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `TreeMap` (red-black tree, sorted) | `std::map` (typically a red-black tree) |
| `HashMap` | `std::unordered_map` |
| `TreeSet`, `HashSet` | `std::set`, `std::unordered_set` |
| `LinkedHashMap` (insertion order) | No standard equivalent |
| `map.get(k)` returns `null` when missing | `find` returns `end()`; `at` throws; `operator[]` inserts a default |
| `map.put(k, v)` overwrites | `insert` does NOT overwrite; `insert_or_assign` or `m[k] = v` does |
| `Map<String,Integer>` boxes values | `map<string,int>` stores ints in the nodes |
| Keys use `compareTo`/`Comparator` or `equals`+`hashCode` | Keys need `operator<` (or a comparator) for ordered, `hash` + `==` for unordered (next file) |
| Generics erased; `Map<K,V>` is one class | Each `map<K,V>` is its own generated class |
| `Map.of(...)`, `containsKey` | initializer lists; `contains` (C++20) |

## Key Rules / Gotchas Recap
- `m[key]` inserts when missing; use `find`/`contains`/`at` for lookups.
- `insert` keeps the old value; `insert_or_assign` replaces it.
- Never rely on unordered iteration order.
- Ordered containers need a strict weak ordering; unordered need a hash that agrees with `==`.
- Do not modify a key while it is in a container (map keys are `const` for this reason).
- Rehashing invalidates unordered iterators; node-based references stay valid.

## Why This Structure Exists
Symbol tables, caches, feature indexes, packet-flow tables and vocabulary lookups all rely on associative containers. Understanding when a lookup silently inserts, or when iteration order changes between runs, prevents subtle bugs in data pipelines and security tools.
