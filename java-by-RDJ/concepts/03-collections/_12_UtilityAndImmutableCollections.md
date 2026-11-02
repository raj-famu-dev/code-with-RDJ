# `_12_UtilityAndImmutableCollections.java`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`Collections` (with an **s**) is a class of static helper methods. Separately, Java has several kinds of read-only or fixed-size collections that look similar but behave differently.

## Full Line-by-Line Breakdown

### SECTION 1: The `Collections` helpers
`sort`, `reverse`, `shuffle`, `max`, `min`, `frequency`, `swap`. Starting from `[5, 3, 9, 1, 7, 3]`: sorted `[1, 3, 3, 5, 7, 9]`, reversed `[9, 7, 5, 3, 3, 1]`, `max=9, min=1`, `frequency of 3 = 2`. `shuffle(nums, new Random(42))` uses a **seeded** `Random`, so the same JDK gives the same shuffle every run (`[7, 9, 3, 1, 3, 5]` here); with no seed it differs each time.

### SECTION 2: `binarySearch` needs a sorted list
On `[1, 3, 5, 7, 9]`, searching `7` gives index `3`. Searching `4` returns `-3`: a negative number means "not found" and encodes where it would be inserted. On an unsorted list the result is meaningless.

### SECTION 3: `List.of` is immutable
`add` throws `UnsupportedOperationException`. It also rejects `null` elements (`NullPointerException`). `Set.of` and `Map.of` are immutable too, reject duplicates, and have a deliberately unspecified iteration order.

### SECTION 4: Trap: `Arrays.asList` is fixed-size, not immutable
`view.set(0, "X")` works and **changes the original array** (`array[0]` becomes `X`), because the list is a view of the array. But `add` throws `UnsupportedOperationException`: the size cannot change.

### SECTION 5: View vs snapshot
```java
List<String> readOnlyView = Collections.unmodifiableList(source);
List<String> snapshot     = List.copyOf(source);
```
After `source.add("c")`, the view shows `[a, b, c]` (it follows the source) while the snapshot is still `[a, b]`. Writing through the view throws.

### SECTION 6: Why immutable collections?
Safe to share and return, safe across threads, and they state the intent that the data does not change. Return `List.copyOf(...)` or an unmodifiable view from a getter instead of your internal list.

## Key Rules / Gotchas Recap
- `Collection` (interface) vs `Collections` (helper class)
- `Arrays.asList`: settable and array-backed, but fixed-size
- `unmodifiableList` = live read-only view; `List.copyOf` = independent immutable copy
- `binarySearch` only on sorted data

## Why This Structure Exists
Hand-writing sort, shuffle, and search is error-prone, so the helpers exist. Immutable and view collections exist because exposing a mutable internal list is one of the most common sources of bugs in object-oriented code.
