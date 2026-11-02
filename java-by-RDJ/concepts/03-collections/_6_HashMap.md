# `_6_HashMap.java`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A `HashMap` stores key → value pairs with O(1) average lookup. It is the most used collection in everyday Java.

## Full Line-by-Line Breakdown

### SECTION 1: `put` and `get`
`put` returns the **previous** value for that key (or `null`). Output: `put apple=5 returned: null`, then `put apple=7 returned: 5`. `get("kiwi")` on a missing key returns `null`.

### SECTION 2: Safer lookups and updates
- `getOrDefault("kiwi", 0)` returns `0` instead of `null`
- `putIfAbsent` only adds when the key is missing (`pear` ignored, `plum` added)
- `merge("apple", 1, Integer::sum)` does `7 + 1`; for a missing key it stores `1`
Result: `{apple=8, fig=1, pear=3, plum=10}` (printed via a `TreeMap` copy for stable order).

### SECTION 3: Counting and grouping
The two most common patterns:
```java
byLength.computeIfAbsent(w.length(), k -> new ArrayList<>()).add(w);
firstLetterCount.merge(w.charAt(0), 1, Integer::sum);
```
`computeIfAbsent` creates the list the first time a key appears. Output: `{3=[cat, dog, ant, cow], 4=[bird, fish]}` and `{a=1, b=1, c=2, d=1, f=1}`.

### SECTION 4: Iterating
Use `entrySet()` when you need both key and value. Calling `get()` inside a `keySet()` loop does a pointless second lookup.

### SECTION 5: Trap: unboxing a missing key
`int missing = stock.get("nope");` unboxes `null` and throws `NullPointerException`. Fix: `getOrDefault("nope", 0)` or check `containsKey` first.

### SECTION 6: Nulls, removal, views
`HashMap` allows **one** null key and any number of null values: `get(null)` is `1`, `get("a")` is `null`. Since `null` can mean "missing" **or** "stored null", use `containsKey` to tell them apart. `keySet()`, `values()` and `entrySet()` are live views.

### SECTION 7: Complexity
`put`, `get`, `remove`, `containsKey` are O(1) on average. `containsValue` is O(n). Iteration order is **not** specified.

## Key Rules / Gotchas Recap
- `get` returns `null` for a missing key; unboxing that `null` crashes
- `merge` and `computeIfAbsent` replace the old "check, then put" dance
- Never rely on `HashMap` iteration order

## Why This Structure Exists
Looking something up by a name, ID, or word is the most common operation in programs. A hash map makes that a calculation instead of a search.
