# `_2_IndexingSlicingBroadcasting.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Indexing and slicing pick out parts of an array; boolean masks and fancy indexing pick elements by condition or by a list of positions; broadcasting lets arrays of different shapes be combined without writing loops. The most dangerous detail is that a basic slice is a view onto the same memory, not a copy, so changing the slice changes the original. Mastering these four ideas is what lets you read and write real NumPy and pandas code.

## Full Line-by-Line Breakdown

### SECTION 1: indexing and slicing
`m[row, col]` picks a single element; `m[:, 1]` means "all rows, column 1"; `m[1:, :2]` means "rows from 1 onward, first two columns". Slices use `start:stop:step` with stop excluded, and a negative step reverses. `m[::-1, 0]` reverses the rows then takes column 0.

```text
=== SECTION 1: indexing and slicing ===
m =
[[ 0  1  2  3]
 [ 4  5  6  7]
 [ 8  9 10 11]]
m[1, 2] = 6 (row 1, col 2; m[1][2] also works but chains two lookups)
m[0] = [0 1 2 3] (first row)
m[:, 1] = [1 5 9] (column 1)
m[1:, :2] =
[[4 5]
 [8 9]]
m[::-1, 0] = [8 4 0] (reverse rows, column 0)
```

### SECTION 2: views vs copies
This is the trap. `view = base[1:4]` does not copy anything; both names look at the same memory. Writing `view[0] = 99` changed `base` too, and `np.shares_memory` confirms it. When you want independence, call `.copy()`. Fancy indexing (a list of positions) is different: it always returns a copy. A plain Python list slice is a (shallow) copy, so someone arriving from lists or from Java's `Arrays.copyOfRange` may wrongly expect the same from NumPy.

```text
=== SECTION 2: views vs copies ===
TRAP: after view[0] = 99, base = [ 0 99  2  3  4  5] (base changed too!)
np.shares_memory(base, view) = True
FIX: .copy() -> base = [0 1 2 3 4 5] | safe = [99  2  3]
fancy indexing result shares memory with source? False
list slice is a copy: lst = [0, 1, 2, 3, 4, 5]
```

### SECTION 3: boolean masks
A comparison like `scores >= 60` produces an array of `True`/`False` of the same shape. Using that array as an index (`scores[mask]`) keeps only the `True` positions. `mask.sum()` counts them because `True` counts as 1. You must combine conditions with `&`, `|` and `~` with parentheses around each comparison; Python's `and`/`or` ask for one truth value for the whole array and raise `ValueError`. You can also assign through a mask (`scores2[scores2 < 60] = 60`), and `np.where(cond, a, b)` chooses between two values per element.

```text
=== SECTION 3: boolean masks ===
scores = [55 82 91 47 76 64]
mask (scores >= 60) = [False  True  True False  True  True]
scores[mask] = [82 91 76 64]
count passing = 4 (True counts as 1)
combine with & and | (NOT 'and'/'or'): [55 76 64]
TRAP 'and' on arrays raises ValueError: The truth value of an array with more than one element is am...
floor at 60 via mask assignment: [60 82 91 60 76 64]
np.where(scores >= 60, 'pass', 'fail'): ['fail' 'pass' 'pass' 'fail' 'pass' 'pass']
```

### SECTION 4: fancy indexing
Passing a list (or array) of integers picks those positions in that order, repeats allowed. With two index lists on a 2-D array, they are paired up: `m[[0, 2], [1, 3]]` means the elements at (0,1) and (2,3), not a 2x2 block. `m[[0, 2]]` with one list picks whole rows.

```text
=== SECTION 4: fancy indexing ===
letters[[0, 2, 6]] = ['a' 'c' 'g']
letters[[6, 0, 0]] = ['g' 'a' 'a'] (any order, repeats allowed)
m[[0, 2], [1, 3]] = [ 1 11] (pairs: (0,1) and (2,3))
m[[0, 2]] =
[[ 0  1  2  3]
 [ 8  9 10 11]]
```

### SECTION 5: broadcasting
Broadcasting is the rule for combining arrays of different shapes. Line the shapes up from the right; two dimensions are compatible when they are equal or one of them is 1, and the size-1 dimension is stretched to match. A `(3,1)` column plus a `(4,)` row gives a `(3,4)` grid. Subtracting column means (shape `(2,)`) from a `(3,2)` matrix centres each column, a very common step in data preparation. A `(3,4)` plus `(3,)` fails because the rightmost dimensions 4 and 3 differ; adding an axis with `[:, None]` turns `(3,)` into `(3,1)`, which then broadcasts.

```text
=== SECTION 5: broadcasting ===
Rule: compare shapes from the RIGHT; dims are compatible if equal or one is 1.
col.shape (3, 1) + row.shape (4,) -> (3, 4)
[[11 12 13 14]
 [21 22 23 24]
 [31 32 33 34]]
(3,4) + (4,) works:
[[2. 3. 4. 5.]
 [2. 3. 4. 5.]
 [2. 3. 4. 5.]]
(3,4) - column means (shape (4,)) centres each column:
[[ -1. -10.]
 [  0.   0.]
 [  1.  10.]]
TRAP shape (3,4) + (3,) fails: operands could not be broadcast together with shapes (3,4) (3,) 
FIX: add an axis -> (3, 4)
```

## Key Differences From Java
| Idea | Java | Python with NumPy |
|---|---|---|
| Single element | `a[i][j]` | `a[i, j]` (or `a[i][j]`) |
| Sub-array | `Arrays.copyOfRange(a, 1, 4)` always copies | `a[1:4]` is a view (shares memory) |
| Filter by condition | Loop with `if`, or `stream().filter(...)` | `a[a > 5]` |
| Different-sized operands | Not applicable; you loop and index each | Broadcasting stretches size-1 dimensions |
| Negative index | Not allowed (exception) | `a[-1]` is the last element |

How you would do this in Java: filtering is a `for` loop with an `if` (or a stream with `.filter(...)`), and adding a row to every row of a matrix is a nested loop. There is no view-style slice for primitive arrays in the JDK, so you would copy or pass offsets by hand.

## Key Rules / Gotchas Recap
- Basic slices are views; fancy indexing and boolean masks produce copies. Use `.copy()` when you need independence.
- Use `&`, `|`, `~` with parentheses, never `and`/`or`/`not`, on arrays.
- `m[[0, 2], [1, 3]]` pairs indices; it does not select a sub-grid.
- Broadcasting compares shapes from the right: equal, or one is 1.
- `(3,4) + (3,)` fails; add an axis (`[:, None]`) to line it up.

## Why This Structure Exists
Preparing data for a model (normalising columns, selecting rows that match a label, batching) is nearly all slicing, masking and broadcasting. The views-vs-copies rule also explains real bugs where "preprocessing" silently changes your raw data.
