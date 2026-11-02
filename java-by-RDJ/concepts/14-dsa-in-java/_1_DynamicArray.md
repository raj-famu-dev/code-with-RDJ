> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Dynamic Array (what `ArrayList` is inside)

## Concept

An array has a fixed size. A **dynamic array** hides a plain `Object[]` behind `add`/`get`/`remove` and, when the array fills up, allocates a **bigger one and copies** everything across. The trick is *how much* bigger: **doubling**. That makes `add` cheap on average even though one unlucky `add` costs a full copy.

## Big-O (n = current size)

| Operation | Time | Why |
|---|---|---|
| `get(i)`, `set(i, x)` | **O(1)** | direct index into the array |
| `add(x)` at the end | **O(1) amortized** (O(n) on a resize) | doubling spreads the copy cost over many adds |
| `insert(i, x)` | **O(n)** | shifts every element after `i` right |
| `remove(i)` | **O(n)** | shifts every element after `i` left |
| `indexOf`, `contains` | **O(n)** | linear scan |
| memory | **O(capacity)**, up to about 2x size | unused slots after a doubling |

## Full Line-by-Line Breakdown

**State.** `Object[] data`, an `int size` (used slots) and `data.length` (capacity). They are different numbers. Generic arrays cannot be created (`new T[n]` is illegal, see `06-generics/_5`), so the storage is `Object[]` and reads cast back with `@SuppressWarnings("unchecked")`.

**`add`.** `ensureCapacity()` doubles when `size == data.length`, then `data[size++] = value`.

**`insert(i, x)`.** `System.arraycopy(data, i, data, i + 1, size - i)` shifts the tail one step right (it is safe for overlapping ranges), then writes `data[i]`.

**`remove(i)`.** Shift left over the gap, then `data[--size] = null`. That last line matters: without it the array keeps a reference to the removed object and the garbage collector can never free it.

**`shrinkIfSparse`.** Halve the array when it is a quarter full. Shrinking at one half would make an add/remove pair at the boundary resize every time ("thrashing").

Real output:

```
after adds and insert: [Ada, Alan, Linus, Grace], size 4, capacity 4
remove(0) returned Ada, now [Alan, Linus, Grace]
indexOf("Grace") = 2, contains("Zed") = false
IndexOutOfBoundsException: index 10, size 3
capacity changes while adding 1..40: 4 -> 8 -> 16 -> 32 -> 64
added 100000 items using 15 resizes and 131068 element copies (1.31 copies per add, always below 2)
capacity at 64 items: 64, after removing down to 10: 32
oracle test: 20000 random operations (4984 removals), identical to ArrayList: true
```

**Reading the amortized line.** 100,000 adds caused 15 resizes and 131,068 element copies, so **1.31 copies per add**. Doubling copies 4 + 8 + 16 + ... which sums to less than 2x the final size, hence "below 2" is a mathematical bound, not luck.

**The oracle test.** 20,000 random `add` / `insert` / `remove` / `set` calls run against both this class and `java.util.ArrayList` with a fixed seed. After every step the sizes must agree and every returned value must match; at the end the full contents are compared. `ArrayList` appears only here, as a trusted reference. It is never used inside the structure.

## Key Rules

1. Grow by a **factor** (doubling), never by a constant. +1 growth is O(n^2) overall.
2. `size` is not `capacity`. Bounds checks use `size`.
3. Null out removed slots so the GC can reclaim them.
4. Shrink at a lower threshold than you grow at.
5. Insert and remove in the middle are O(n): do not use an array-backed list as a queue.

## Gotchas Recap

- "O(1) amortized" does not mean every call is fast; one call in the sequence is O(n). Latency-sensitive code feels that.
- Forgetting `data[--size] = null` passes every test and still leaks.
- `ArrayList.remove(int)` vs `remove(Object)` on a `List<Integer>` is a famous trap (see `03-collections`).

## Why This Structure Exists

Building it yourself turns "ArrayList is fast at the end" from a sentence you memorized into a measurement (1.31 copies per add) you can reproduce, and the oracle test shows how to prove a data structure correct without reading its code.
