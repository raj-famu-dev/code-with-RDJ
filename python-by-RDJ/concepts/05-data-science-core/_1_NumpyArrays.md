# `_1_NumpyArrays.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A NumPy `ndarray` is a fixed-size, rectangular block of numbers that all share one data type (`dtype`) and are stored side by side in memory. Because the type is fixed and the memory is contiguous, NumPy can do maths on the whole block at once in compiled C code, which is why almost all Python data science and machine learning (pandas, scikit-learn, PyTorch tensors) is built on this idea. You describe an array by its `shape` (size in each dimension), its `dtype`, and its `ndim` (number of dimensions).

## Full Line-by-Line Breakdown

### SECTION 1: ndarray basics
`np.array([1, 2, 3, 4])` converts a Python list into an array. `.dtype` says what kind of number it holds, `.shape` is a tuple of sizes (`(4,)` means one dimension of length 4, the trailing comma is how Python writes a one-element tuple), `.ndim` is how many dimensions, and `.size` is the total element count. A list of lists becomes a 2-D array with shape `(rows, cols)`. `.itemsize` is bytes per element and `.nbytes` is the total, so a 6-element `int64` array uses 6 x 8 = 48 bytes.

```text
=== SECTION 1: ndarray basics ===
a = [1 2 3 4]
type(a) = ndarray
a.dtype = int64
a.shape = (4,)  a.ndim = 1  a.size = 4
m =
[[1 2 3]
 [4 5 6]]
m.shape = (2, 3) (rows, cols)  m.ndim = 2
m.itemsize = 8 bytes per element; m.nbytes = 48
```

### SECTION 2: dtype
NumPy picks one dtype for the whole array. If any element is a float, everything becomes a float (this is called upcasting). You can force a type with `dtype=` or convert with `.astype(...)`. `astype(int)` truncates toward zero (`-1.9` becomes `-1`) rather than rounding.

The trap: fixed-width integers do not grow. A `uint8` holds 0 to 255, so `250 + 10` silently wraps around to `4`. Python's own `int` never overflows, so this surprises people coming from Python and from Java alike (Java's `int` also wraps silently). The fix is to choose a wider dtype. (The default integer dtype shown here, `int64`, is what a 64-bit Linux build gives; on other platforms it can differ.)

```text
=== SECTION 2: dtype ===
np.array([1, 2, 3]).dtype   -> int64
np.array([1.0, 2, 3]).dtype -> float64 (one float upcasts all)
np.array([True, 2]).dtype    -> int64
explicit float32: [1. 2. 3.] float32 itemsize 4
astype(int): [ 1 -1  2] (truncates toward zero, does not round)
TRAP uint8 250 + 10 = [4] (wrapped around, no error)
Python int 250 + 10 = 260
FIX: use a wider dtype -> [260]
```

### SECTION 3: creation functions
You rarely type arrays by hand. `zeros`, `ones`, `full` and `eye` (identity matrix) build arrays of a given shape. `arange(start, stop, step)` is like `range` and excludes `stop`; `linspace(start, stop, count)` includes `stop` and you choose how many points. `reshape` reinterprets the same numbers with a new shape. `np.random.default_rng(42)` makes a seeded random generator, so the "random" numbers are the same on every run; that is what makes experiments reproducible.

```text
=== SECTION 3: creation functions ===
zeros((2, 3)):
[[0. 0. 0.]
 [0. 0. 0.]]
ones(3): [1. 1. 1.]
full((2, 2), 7):
[[7 7]
 [7 7]]
eye(3):
[[1. 0. 0.]
 [0. 1. 0.]
 [0. 0. 1.]]
arange(0, 10, 3): [0 3 6 9] (stop excluded, like range)
linspace(0, 1, 5): [0.   0.25 0.5  0.75 1.  ] (stop INCLUDED, count given)
reshape: arange(6).reshape(2, 3):
[[0 1 2]
 [3 4 5]]
rng.integers(0, 10, size=5): [0 7 6 4 4]
rng.random(3): [0.69736803 0.09417735 0.97562235]
```

### SECTION 4: ndarray vs list
The same operators mean different things. `list * 2` repeats the list; `array * 2` multiplies every number. `list + list` joins them; `array + array` adds element by element. A list can hold mixed types; an array forces one dtype, so mixing a string in turns every element into text (`<U32` means "Unicode string up to 32 characters"), which silently breaks maths. The size comparison is a rough illustration: `sys.getsizeof` on a list counts only the array of pointers, while each Python int is a separate object stored elsewhere. The ndarray's `nbytes` is the real data.

```text
=== SECTION 4: ndarray vs list ===
list * 2  = [1, 2, 3, 1, 2, 3] (repeats the list)
array * 2 = [2 4 6] (element-wise maths)
list + list  = [1, 2, 3, 1, 2, 3] (concatenation)
array + array = [2 4 6] (element-wise add)
list can mix types: [1, 'two', 3.0]
array coerces to one dtype: <U32 -> ['1' 'two' '3.0']
sys.getsizeof([0]*1000) = 8056 bytes (pointer array only)
np.zeros(1000, int64).nbytes = 8000 bytes (actual data)
Why: a list stores pointers to separate int objects; an ndarray stores raw numbers contiguously.
```

### SECTION 5: ndarray vs Java array
A Java `int[]` is also fixed-size and typed, so the closest relative is the ndarray. The difference is what you can do to it: Java gives you indexing and `length` only, and you write the loops. NumPy has the maths built in. `np.append` does not grow the array in place; it returns a new one and leaves the original unchanged, just like you would allocate a bigger Java array and copy. A 2-D ndarray is one rectangular block, unlike Java's `int[][]`, which is an array of separate row arrays that can differ in length.

```text
=== SECTION 5: ndarray vs Java array ===
Java int[] is also fixed-size and typed, but has no maths: you write loops.
ndarray also has a fixed size once created; 'append' makes a NEW array:
np.append(arr, 4) = [1 2 3 4] | original arr unchanged: [1 2 3]
2-D: Java uses int[][] (array of arrays, rows may differ in length);
ndarray 2-D is ONE rectangular block: (2, 3)
```

## Key Differences From Java
| Idea | Java | Python with NumPy |
|---|---|---|
| Numeric array | `int[]`, `double[]` (built in, no maths) | `np.ndarray` (needs `import numpy as np`) |
| Maths on arrays | Write a `for` loop yourself, or use a library such as ND4J or EJML | `a * 2`, `a + b`, `a.sum()` operate on the whole array |
| Type | Declared: `double[] a = new double[3];` | Inferred from the data, overridable with `dtype=` |
| Multi-dimensional | `int[][]` (array of arrays, ragged allowed) | One rectangular block with a `shape` |
| Built-in support | None for numeric work in the JDK | Third-party library, but the de facto standard |
| Mixed types | Not possible in a primitive array | A list can mix; an array coerces to one dtype |

How you would do this in Java: the JDK has no numeric array library. You would use plain arrays with loops, or add a dependency such as ND4J (the engine used by Deeplearning4j) or EJML for matrices.

## Key Rules / Gotchas Recap
- All elements share one `dtype`; one float upcasts everything, one string turns everything into text.
- Fixed-width integers overflow silently (`uint8`: 250 + 10 = 4).
- `astype(int)` truncates toward zero, it does not round.
- `arange` excludes the stop value, `linspace` includes it.
- Size is fixed after creation; `np.append` returns a new array.
- Use `np.random.default_rng(seed)` for reproducible random numbers.

## Why This Structure Exists
Every model weight, image, embedding and dataset in AI engineering is ultimately an `ndarray` (or something shaped like one). Knowing shape and dtype is the first thing you check when code breaks, and shape mismatches are the most common bug in machine learning code.
