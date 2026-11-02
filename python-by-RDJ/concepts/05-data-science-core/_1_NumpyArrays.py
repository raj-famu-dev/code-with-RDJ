# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""NumPy arrays: ndarray, dtype, shape, creation functions, and how they differ
from Python lists and from Java arrays."""

import sys

import numpy as np

# ===== SECTION 1: WHAT AN ndarray IS =====
print("=== SECTION 1: ndarray basics ===")
a = np.array([1, 2, 3, 4])
print("a =", a)
print("type(a) =", type(a).__name__)
print("a.dtype =", a.dtype)  # int64 on most 64-bit Linux/macOS builds
print("a.shape =", a.shape, " a.ndim =", a.ndim, " a.size =", a.size)
m = np.array([[1, 2, 3], [4, 5, 6]])
print("m =\n", m, sep="")
print("m.shape =", m.shape, "(rows, cols)  m.ndim =", m.ndim)
print("m.itemsize =", m.itemsize, "bytes per element; m.nbytes =", m.nbytes)

# ===== SECTION 2: dtype =====
print("\n=== SECTION 2: dtype ===")
print("np.array([1, 2, 3]).dtype   ->", np.array([1, 2, 3]).dtype)
print("np.array([1.0, 2, 3]).dtype ->", np.array([1.0, 2, 3]).dtype, "(one float upcasts all)")
print("np.array([True, 2]).dtype    ->", np.array([True, 2]).dtype)
f32 = np.array([1, 2, 3], dtype=np.float32)
print("explicit float32:", f32, f32.dtype, "itemsize", f32.itemsize)
print("astype(int):", np.array([1.9, -1.9, 2.5]).astype(int), "(truncates toward zero, does not round)")
# TRAP: fixed-width integers overflow silently (Python int never does)
small = np.array([250], dtype=np.uint8)
print("TRAP uint8 250 + 10 =", small + np.uint8(10), "(wrapped around, no error)")
print("Python int 250 + 10 =", 250 + 10)
big = np.array([250], dtype=np.int64) + 10
print("FIX: use a wider dtype ->", big)

# ===== SECTION 3: CREATION FUNCTIONS =====
print("\n=== SECTION 3: creation functions ===")
print("zeros((2, 3)):\n", np.zeros((2, 3)), sep="")
print("ones(3):", np.ones(3))
print("full((2, 2), 7):\n", np.full((2, 2), 7), sep="")
print("eye(3):\n", np.eye(3), sep="")
print("arange(0, 10, 3):", np.arange(0, 10, 3), "(stop excluded, like range)")
print("linspace(0, 1, 5):", np.linspace(0, 1, 5), "(stop INCLUDED, count given)")
print("reshape: arange(6).reshape(2, 3):\n", np.arange(6).reshape(2, 3), sep="")
rng = np.random.default_rng(42)  # seeded generator -> reproducible
print("rng.integers(0, 10, size=5):", rng.integers(0, 10, size=5))
print("rng.random(3):", rng.random(3))

# ===== SECTION 4: ndarray vs PYTHON LIST =====
print("\n=== SECTION 4: ndarray vs list ===")
lst = [1, 2, 3]
arr = np.array([1, 2, 3])
print("list * 2  =", lst * 2, "(repeats the list)")
print("array * 2 =", arr * 2, "(element-wise maths)")
print("list + list  =", lst + lst, "(concatenation)")
print("array + array =", arr + arr, "(element-wise add)")
print("list can mix types:", [1, "two", 3.0])
print("array coerces to one dtype:", np.array([1, "two", 3.0]).dtype, "->", np.array([1, "two", 3.0]))
print("sys.getsizeof([0]*1000) =", sys.getsizeof([0] * 1000), "bytes (pointer array only)")
print("np.zeros(1000, int64).nbytes =", np.zeros(1000, dtype=np.int64).nbytes, "bytes (actual data)")
print("Why: a list stores pointers to separate int objects; an ndarray stores raw numbers contiguously.")

# ===== SECTION 5: ndarray vs JAVA ARRAY =====
print("\n=== SECTION 5: ndarray vs Java array ===")
print("Java int[] is also fixed-size and typed, but has no maths: you write loops.")
print("ndarray also has a fixed size once created; 'append' makes a NEW array:")
grown = np.append(arr, 4)
print("np.append(arr, 4) =", grown, "| original arr unchanged:", arr)
print("2-D: Java uses int[][] (array of arrays, rows may differ in length);")
print("ndarray 2-D is ONE rectangular block:", m.shape)
