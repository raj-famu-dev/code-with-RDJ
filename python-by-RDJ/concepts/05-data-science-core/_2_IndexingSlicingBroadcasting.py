# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Indexing and slicing ndarrays: the views-vs-copies trap, boolean masks,
fancy indexing, and the broadcasting rules."""

import numpy as np

# ===== SECTION 1: BASIC INDEXING AND SLICING =====
print("=== SECTION 1: indexing and slicing ===")
m = np.arange(12).reshape(3, 4)
print("m =\n", m, sep="")
print("m[1, 2] =", m[1, 2], "(row 1, col 2; m[1][2] also works but chains two lookups)")
print("m[0] =", m[0], "(first row)")
print("m[:, 1] =", m[:, 1], "(column 1)")
print("m[1:, :2] =\n", m[1:, :2], sep="")
print("m[::-1, 0] =", m[::-1, 0], "(reverse rows, column 0)")

# ===== SECTION 2: VIEWS VS COPIES (THE BIG TRAP) =====
print("\n=== SECTION 2: views vs copies ===")
base = np.arange(6)
view = base[1:4]  # basic slice -> VIEW, shares memory
view[0] = 99
print("TRAP: after view[0] = 99, base =", base, "(base changed too!)")
print("np.shares_memory(base, view) =", np.shares_memory(base, view))
base = np.arange(6)
safe = base[1:4].copy()  # explicit copy
safe[0] = 99
print("FIX: .copy() -> base =", base, "| safe =", safe)
fancy = np.arange(6)[[1, 2, 3]]  # fancy indexing -> COPY
print("fancy indexing result shares memory with source?", np.shares_memory(base, fancy))
# Python list slices are copies (shallow); ndarray basic slices are views.
lst = [0, 1, 2, 3, 4, 5]
part = lst[1:4]
part[0] = 99
print("list slice is a copy: lst =", lst)

# ===== SECTION 3: BOOLEAN MASKS =====
print("\n=== SECTION 3: boolean masks ===")
scores = np.array([55, 82, 91, 47, 76, 64])
mask = scores >= 60
print("scores =", scores)
print("mask (scores >= 60) =", mask)
print("scores[mask] =", scores[mask])
print("count passing =", mask.sum(), "(True counts as 1)")
print("combine with & and | (NOT 'and'/'or'):", scores[(scores > 50) & (scores < 80)])
try:
    scores[(scores > 50) and (scores < 80)]  # TRAP
except ValueError as e:
    print("TRAP 'and' on arrays raises ValueError:", str(e)[:60] + "...")
scores2 = scores.copy()
scores2[scores2 < 60] = 60  # assignment through a mask
print("floor at 60 via mask assignment:", scores2)
print("np.where(scores >= 60, 'pass', 'fail'):", np.where(scores >= 60, "pass", "fail"))

# ===== SECTION 4: FANCY INDEXING =====
print("\n=== SECTION 4: fancy indexing ===")
letters = np.array(list("abcdefg"))
print("letters[[0, 2, 6]] =", letters[[0, 2, 6]])
print("letters[[6, 0, 0]] =", letters[[6, 0, 0]], "(any order, repeats allowed)")
print("m[[0, 2], [1, 3]] =", m[[0, 2], [1, 3]], "(pairs: (0,1) and (2,3))")
print("m[[0, 2]] =\n", m[[0, 2]], sep="")

# ===== SECTION 5: BROADCASTING =====
print("\n=== SECTION 5: broadcasting ===")
print("Rule: compare shapes from the RIGHT; dims are compatible if equal or one is 1.")
col = np.array([[10], [20], [30]])  # shape (3, 1)
row = np.array([1, 2, 3, 4])  # shape (4,)
print("col.shape", col.shape, "+ row.shape", row.shape, "->", (col + row).shape)
print(col + row)
mat = np.ones((3, 4))
print("(3,4) + (4,) works:\n", mat + row, sep="")
print("(3,4) - column means (shape (4,)) centres each column:")
data = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
print(data - data.mean(axis=0))
try:
    np.ones((3, 4)) + np.ones(3)  # TRAP: trailing dims 4 vs 3
except ValueError as e:
    print("TRAP shape (3,4) + (3,) fails:", e)
print("FIX: add an axis ->", (np.ones((3, 4)) + np.ones(3)[:, None]).shape)
