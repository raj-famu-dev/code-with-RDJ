# `_5_LinkedHashSetAndTreeSet.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
Three sets, three ordering promises: `HashSet` (none), `LinkedHashSet` (insertion order), `TreeSet` (sorted).

## Full Line-by-Line Breakdown

### SECTION 1: Same input, different ordering
Input `pear, apple, fig, apple, banana`. `LinkedHashSet` prints `[pear, apple, fig, banana]` (insertion order, duplicate dropped). `TreeSet` prints `[apple, banana, fig, pear]` (sorted).

### SECTION 2: `LinkedHashSet`
A `HashSet` plus a linked list through its entries: same O(1) average speed, slightly more memory, predictable iteration. Re-adding `"c"` does **not** move it: `[c, a, b]`.

### SECTION 3: `TreeSet` navigation (O(log n))
Backed by a balanced tree (red-black in OpenJDK). Because it is sorted it has range methods. For `[10, 20, 30, 40]`:
| Call | Result | Meaning |
|---|---|---|
| `floor(25)` | 20 | greatest element ≤ 25 |
| `ceiling(25)` | 30 | smallest element ≥ 25 |
| `lower(20)` / `higher(20)` | 10 / 30 | strictly less / greater |
| `headSet(30)` / `tailSet(30)` | `[10, 20]` / `[30, 40]` | `< 30` / `>= 30` |
| `descendingSet()` | `[40, 30, 20, 10]` | reverse view |

### SECTION 4: What `TreeSet` requires
Elements must be `Comparable`, or you must supply a `Comparator`. Adding a `Plain` object (not `Comparable`) throws `ClassCastException`, which the code catches.

### SECTION 5: Trap: the comparator defines "duplicate"
A `TreeSet` never calls `equals()`. With a comparator on string length, `"pear"` and `"plum"` compare as `0`, so the second is treated as the same element and dropped. Output: `[fig, pear]`. Fix: add a tie-breaker with `thenComparing`.

### SECTION 6: Choosing
Just uniqueness, fastest → `HashSet`. Uniqueness plus insertion order → `LinkedHashSet`. Sorted order or range queries → `TreeSet`.

## Key Rules / Gotchas Recap
- `TreeSet` duplicates are decided by `compare() == 0`, not `equals()`
- `TreeSet` operations are O(log n); hash-based sets are O(1) on average
- Re-adding an existing element to a `LinkedHashSet` does not change its position

## Why This Structure Exists
Sometimes you need more than "have I seen this?". Ordered and sorted sets keep that extra structure for you, so you do not have to sort a list every time you need it.
