# `_13_CollectionsCapstone.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
Three small programs that combine what the folder covered: counting with a `Map`, caching with a `LinkedHashMap`, and ranking with `Comparator` chains.

## Full Line-by-Line Breakdown

### Building blocks
- **`LruCache<K, V> extends LinkedHashMap<K, V>`**: the constructor calls `super(16, 0.75f, true)` for **access order**. Overriding `removeEldestEntry` to return `size() > capacity` makes the map evict its least recently used entry automatically after each `put`.
- **`record Player(String name, int score, int level)`**: an immutable data holder for Part 3.

### PART 1: Word frequency
```java
freq.merge(word, 1, Integer::sum);
```
Counts each word of `the quick brown fox jumps over the lazy dog the fox`. The entries are copied into a list and sorted with a comparator that is count **descending**, then word **ascending**:
```java
Map.Entry.<String, Integer>comparingByValue().reversed()
        .thenComparing(Map.Entry.comparingByKey());
```
Output: `the x3`, `fox x2`, `brown x1`. Several words tie on 1, and the tie-breaker puts `brown` first alphabetically.

### PART 2: LRU cache (capacity 3)
`put a, b, c`, then `get("a")` (makes `a` most recent), then `put d`. The cache is over capacity, so the **least recently used** entry, `b`, is evicted. Output: `[c, a, d]` (oldest first) and `Contains b? false`.

### PART 3: Leaderboard
Sorted by score descending, then level descending, then name:
```
#1 Lea  - 1200 pts, level 9
#2 Ana  -  900 pts, level 15
#3 Omar -  900 pts, level 15
#4 Kai  -  900 pts, level 12
```
Ana and Omar tie on score and level, so name breaks the tie.

### PART 4: Which collection, and why
`HashMap` for fast counting; `ArrayList` because sorting needs an indexable list; `LinkedHashMap` because access order gives LRU almost for free; a `Comparator` chain to rank by several rules without editing the class.

## Key Rules / Gotchas Recap
- `merge` is the idiomatic counter
- Override `removeEldestEntry` + access order = a working LRU cache in about ten lines
- A comparator chain is read top to bottom: first rule wins, later rules only break ties

## Why This Structure Exists
The individual files taught each collection in isolation. Real problems mix them: one structure to count, another to remember recency, another to rank. This file is the first place that choice has to be made on purpose.
