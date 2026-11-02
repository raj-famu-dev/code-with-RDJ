# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Linear algebra with NumPy: dot, matmul (@), transpose, inverse, solve, norms,
and a tiny worked neural-network layer showing why this is the maths of AI."""

import numpy as np

np.set_printoptions(precision=4, suppress=True)

# ===== SECTION 1: VECTORS AND DOT PRODUCT =====
print("=== SECTION 1: dot product ===")
u = np.array([1.0, 2.0, 3.0])
v = np.array([4.0, 5.0, 6.0])
print("u . v =", np.dot(u, v), "= 1*4 + 2*5 + 3*6 =", sum(a * b for a, b in zip(u, v)))
print("u @ v =", u @ v, "(same thing for 1-D)")
print("TRAP: u * v is element-wise, NOT a dot product:", u * v)

# ===== SECTION 2: MATRIX MULTIPLICATION AND TRANSPOSE =====
print("\n=== SECTION 2: matmul and transpose ===")
A = np.array([[1.0, 2.0], [3.0, 4.0]])
B = np.array([[0.0, 1.0], [1.0, 0.0]])
print("A @ B =\n", A @ B, sep="")
print("B @ A =\n", B @ A, sep="")
print("A @ B == B @ A ?", np.array_equal(A @ B, B @ A), "(matrix multiplication is NOT commutative)")
print("A * B (element-wise) =\n", A * B, sep="")
M = np.array([[1, 2, 3], [4, 5, 6]])
print("M.shape =", M.shape, " M.T.shape =", M.T.shape)
print("M @ M.T =\n", M @ M.T, sep="")
try:
    M @ M
except ValueError as e:
    print("TRAP shapes (2,3) @ (2,3) fail: inner dims must match ->", str(e)[:50] + "...")

# ===== SECTION 3: INVERSE AND SOLVE =====
print("\n=== SECTION 3: inverse and solve ===")
# System: 2x + y = 5 ; x + 3y = 10
S = np.array([[2.0, 1.0], [1.0, 3.0]])
rhs = np.array([5.0, 10.0])
x_inv = np.linalg.inv(S) @ rhs
x_solve = np.linalg.solve(S, rhs)
print("inv(S) =\n", np.linalg.inv(S), sep="")
print("x via inv(S) @ rhs  =", x_inv)
print("x via solve(S, rhs) =", x_solve, "(preferred: faster and more accurate)")
print("check S @ x =", S @ x_solve, "== rhs", rhs)
print("S @ inv(S) ~ identity:", np.allclose(S @ np.linalg.inv(S), np.eye(2)))
singular = np.array([[1.0, 2.0], [2.0, 4.0]])  # row 2 = 2 * row 1
print("det(singular) =", np.linalg.det(singular))
try:
    np.linalg.inv(singular)
except np.linalg.LinAlgError as e:
    print("TRAP inverse of singular matrix:", e)

# ===== SECTION 4: NORMS =====
print("\n=== SECTION 4: norms ===")
w = np.array([3.0, 4.0])
print("L2 norm of [3, 4] =", np.linalg.norm(w), "(sqrt(3^2 + 4^2), the length)")
print("L1 norm of [3, 4] =", np.linalg.norm(w, 1), "(sum of absolute values)")
print("unit vector:", w / np.linalg.norm(w))
a, b = np.array([1.0, 0.0]), np.array([1.0, 1.0])
cos = a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
print("cosine similarity of [1,0] and [1,1] =", round(float(cos), 4), "(1 = same direction)")

# ===== SECTION 5: WORKED EXAMPLE - ONE NEURAL-NETWORK LAYER =====
print("\n=== SECTION 5: worked example, a neural-net layer is matmul + bias ===")
# 2 samples, 3 features each; layer maps 3 inputs -> 2 outputs.
X = np.array([[1.0, 2.0, 3.0], [0.0, 1.0, 0.5]])  # shape (2, 3)
W = np.array([[0.1, 0.4], [0.2, -0.5], [0.3, 0.6]])  # shape (3, 2)
bias = np.array([0.1, -0.1])  # shape (2,)
Z = X @ W + bias  # (2,3)@(3,2) -> (2,2), bias broadcasts
print("X shape", X.shape, " W shape", W.shape, " Z shape", Z.shape)
print("Z = X @ W + b =\n", Z, sep="")
print("by hand, sample 0 output 0: 1*0.1 + 2*0.2 + 3*0.3 + 0.1 =", 1 * 0.1 + 2 * 0.2 + 3 * 0.3 + 0.1)
A_out = np.maximum(0, Z)  # ReLU activation
print("after ReLU =\n", A_out, sep="")
print("Training a network = adjusting W and bias; every layer is this same matmul.")
