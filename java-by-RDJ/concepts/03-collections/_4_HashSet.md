# `_4_HashSet.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
A `HashSet` stores each value at most once and finds values in O(1) on average. It uses `hashCode()` to pick a bucket and `equals()` to confirm a match. This ties directly back to `02-oop/_12_EqualsHashCodeToString`.

## Full Line-by-Line Breakdown

### The three helper classes
- **`Point`**: `equals` and `hashCode` both use `x` and `y`. The correct pattern.
- **`BrokenPoint`**: overrides `equals` but **not** `hashCode`. The compiler even warns about it. Broken on purpose.
- **`Student`**: `hashCode` returns `id`, a **mutable** field. Kept simple so the demo is predictable.

### SECTION 1: Uniqueness
`add` returns `true` the first time and `false` for a duplicate. Output: `true`, `false`, `size = 1`. Never depend on `HashSet` printing order; it is not specified.

### SECTION 2: How "the same" is decided
Step 1, `hashCode()` picks the bucket. Step 2, `equals()` confirms inside that bucket. A `HashSet` is a `HashMap` underneath with your element as the key. Two `Point(1, 2)` objects count as one: `size = 1`, and `contains(new Point(1,2))` is `true`.

### SECTION 3: Trap: `equals` without `hashCode`
Two "equal" `BrokenPoint`s inherit identity-based hash codes, so they land in different buckets and `equals` is never asked. Output: `size = 2` and `contains` is `false`. This is "almost always", not guaranteed, because identity hash codes are arbitrary.

### SECTION 4: Trap: mutating an element after adding it
The student is filed under hash `1`. After `s.id = 2`, lookups search the bucket for `2`: `contains` goes from `true` to `false`, yet `size()` is still `1`. The element is stuck in the wrong bucket. Rule: only use immutable fields for `hashCode`.

### SECTION 5: Set operations
`addAll` = union, `retainAll` = intersection, `removeAll` = difference. Results: `[1, 2, 3, 4, 5]`, `[3, 4]`, `[1, 2]` (copied into a `TreeSet` only to print in a stable order).

### SECTION 6: Complexity
`add`, `contains`, `remove` are O(1) on average, O(n) in the worst case with heavy collisions.

## Key Rules / Gotchas Recap
- Override `equals` and `hashCode` **together**, from the same fields
- Never change fields used by `hashCode` while the object is inside a set or is a map key
- Equal objects must have equal hash codes; the reverse is not required

## Why This Structure Exists
Searching a list for a duplicate is O(n) each time. Hashing turns "where would this be?" into a calculation, so membership tests stay fast no matter how large the set gets.
