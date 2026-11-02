# `_8_LinkedHashMapAndTreeMap.java`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Three maps, three ordering promises: `HashMap` (none), `LinkedHashMap` (insertion or access order), `TreeMap` (sorted keys).

## Full Line-by-Line Breakdown

### SECTION 1: Ordering side by side
Entries `zebra=1, apple=2, mango=3`. `LinkedHashMap` prints them in insertion order; `TreeMap` prints `{apple=2, mango=3, zebra=1}`.

### SECTION 2: Updating a key does not move it
`linked.put("zebra", 100)` changes the value but `zebra` stays first: `{zebra=100, apple=2, mango=3}`.

### SECTION 3: Access order, the basis of an LRU cache
```java
new LinkedHashMap<>(16, 0.75f, true)
```
The final `true` switches to **access order**: every `get` or `put` moves that entry to the end. After `put a, b, c` and `get("a")`, the order is `[b, c, a]`, so the **first** entry is always the least recently used. The full cache is built in `_13_CollectionsCapstone`.

### SECTION 4: `TreeMap` navigation (O(log n))
`firstKey` 60, `lastKey` 90. `headMap(80)` = keys `< 80` → `{60=D, 70=C}`. `tailMap(80)` = keys `>= 80` → `{80=B, 90=A}`. `descendingMap()` reverses the order.

### SECTION 5: The classic use: range lookup
```java
Map.Entry<Integer, String> band = grades.floorEntry(85);
```
`floorEntry(k)` returns the entry with the greatest key `<= k`. Score 85 maps to grade `B` (band starts at 80), with no chain of `if`/`else`. `ceilingEntry(85)` gives `90=A`.

### SECTION 6: Trap: null keys
`HashMap` accepts one null key. A `TreeMap` with natural ordering cannot compare `null`, so `put(null, ...)` throws `NullPointerException`.

### SECTION 7: Custom order
`new TreeMap<>(Comparator.reverseOrder())` gives `{c=3, b=2, a=1}`.

### SECTION 8: Choosing
Fastest lookup → `HashMap`. Insertion/access order or LRU → `LinkedHashMap`. Sorted keys or range queries → `TreeMap`.

## Key Rules / Gotchas Recap
- `LinkedHashMap(..., true)` = access order = LRU building block
- `floorEntry` / `ceilingEntry` solve range-lookup problems cleanly
- `TreeMap` treats `compare() == 0` as the same key, like `TreeSet`

## Why This Structure Exists
Different problems need different guarantees about order. Choosing the map by the guarantee you need (none, remembered, sorted) is cheaper than sorting by hand every time.
