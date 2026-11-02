# `_2_ArrayList.java`

> Walkthrough drafted with Claude. Check it against your own understanding and rewrite it in your own words.

## Concept
`ArrayList` is a resizable wrapper around a plain array. Elements sit side by side, so reading by index is instant, but inserting or removing near the front means shifting everything after it.

## Full Line-by-Line Breakdown

### SECTION 1: What it really is
A hidden `Object[]`. **Size** is how many elements you stored; **capacity** is the length of the hidden array. `get(1)` is O(1): the position is calculated directly. Output: `get(1) = b`.

### SECTION 2: How it grows
When the array is full, `ArrayList` allocates a bigger one and copies everything over. In OpenJDK the default capacity is 10 and growth is roughly 1.5x, but those numbers are implementation details, not promises. Result: `add` at the end is **O(1) amortized**. `new ArrayList<>(1000)` pre-sizes the array when you know the count, avoiding repeated copying. Output: `big.size() = 1000`.

### SECTION 3: Front and middle are O(n)
```java
list.add(0, "front");
String removed = list.remove(1);
list.set(0, "FRONT");
```
`add(0, x)` shifts every element right; `remove(i)` shifts everything after `i` left; `set(i, x)` just replaces in place, O(1). Outputs: `[front, a, b, c]`, then `remove(1) returned "a"` leaving `[front, b, c]`, then `[FRONT, b, c]`.

### SECTION 4: Trap: `remove(int)` vs `remove(Object)`
On a `List<Integer>`, `nums.remove(1)` means "remove the element **at index 1**". To remove the **value** 1 you must write `nums.remove(Integer.valueOf(1))`. From `[10, 1, 20, 1]`: index removal gives `[10, 20, 1]`, then value removal gives `[10, 20]`. The commented-out `nums.remove(99)` would throw `IndexOutOfBoundsException`, since 99 is read as an index.

### SECTION 5: Trap: modifying while looping
The for-each loop uses an `Iterator`. `ArrayList` counts structural changes (`modCount`); removing `"x"` inside the loop makes the next `next()` throw `ConcurrentModificationException`, which the code catches. Fix: `words.removeIf(w -> w.equals("y"))`. Output: `After removeIf: [z]`.

### SECTION 6: Scans and bad indexes
`indexOf` and `contains` scan the list: O(n). `fruit.get(3)` on a 3-element list throws `IndexOutOfBoundsException: Index 3 out of bounds for length 3` (valid indexes are 0 to `size()-1`).

### SECTION 7: Complexity
| Operation | Cost |
|---|---|
| `get(i)`, `set(i, x)` | O(1) |
| `add(x)` at end | O(1) amortized |
| `add(i, x)`, `remove(i)`, `remove(Object)` | O(n) |
| `contains`, `indexOf` | O(n) |

## Key Rules / Gotchas Recap
- `list.remove(1)` on `List<Integer>` removes **by index**
- Never add or remove inside a for-each over the same list; use `removeIf` or an iterator
- Pre-size when you know the count

## Why This Structure Exists
An array gives the fastest possible indexed reads and is friendly to the CPU cache, but its size is fixed. `ArrayList` hides the resizing so you get array speed with list convenience, which is why it is the default list choice.
