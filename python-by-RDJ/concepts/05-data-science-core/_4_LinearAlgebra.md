# `_4_LinearAlgebra.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Linear algebra is the maths of vectors (lists of numbers) and matrices (grids of numbers), and NumPy provides it directly: `dot` and `@` for multiplication, `.T` for transpose, `np.linalg.inv`, `solve` and `norm`. It matters because a neural network layer is nothing more than a matrix multiplication plus a bias followed by a simple function, so every model you will train or run is built from these operations. The file ends with a small worked example computed both by NumPy and by hand.

## Full Line-by-Line Breakdown

### SECTION 1: dot product
The dot product multiplies matching elements and adds them: for `[1,2,3]` and `[4,5,6]` it is 1x4 + 2x5 + 3x6 = 32. For 1-D arrays `np.dot(u, v)` and `u @ v` give the same answer. The trap is `u * v`, which is element-wise multiplication and returns a vector `[4, 10, 18]`, not a single number. A dot product measures how aligned two vectors are.

```text
=== SECTION 1: dot product ===
u . v = 32.0 = 1*4 + 2*5 + 3*6 = 32.0
u @ v = 32.0 (same thing for 1-D)
TRAP: u * v is element-wise, NOT a dot product: [ 4. 10. 18.]
```

### SECTION 2: matmul and transpose
`A @ B` is matrix multiplication: each output cell is the dot product of a row of `A` with a column of `B`. It is not commutative, so `A @ B` differs from `B @ A` here. `A * B` is still element-wise. The transpose `.T` swaps rows and columns, so shape `(2,3)` becomes `(3,2)`. For multiplication the inner dimensions must match: `(2,3) @ (3,2)` works and gives `(2,2)`, while `(2,3) @ (2,3)` raises an error.

```text
=== SECTION 2: matmul and transpose ===
A @ B =
[[2. 1.]
 [4. 3.]]
B @ A =
[[3. 4.]
 [1. 2.]]
A @ B == B @ A ? False (matrix multiplication is NOT commutative)
A * B (element-wise) =
[[0. 2.]
 [3. 0.]]
M.shape = (2, 3)  M.T.shape = (3, 2)
M @ M.T =
[[14 32]
 [32 77]]
TRAP shapes (2,3) @ (2,3) fail: inner dims must match -> matmul: Input operand 1 has a mismatch in its core...
```

### SECTION 3: inverse and solve
To solve `S x = rhs` (here 2x + y = 5 and x + 3y = 10), you can compute `inv(S) @ rhs`, but `np.linalg.solve(S, rhs)` is the recommended way: it avoids forming the inverse, which is generally faster and numerically safer. Both give `x = 1, y = 3`, and multiplying back (`S @ x`) reproduces the right-hand side. A matrix whose rows are multiples of each other (a singular matrix, determinant 0) has no inverse, and NumPy raises `LinAlgError`.

```text
=== SECTION 3: inverse and solve ===
inv(S) =
[[ 0.6 -0.2]
 [-0.2  0.4]]
x via inv(S) @ rhs  = [1. 3.]
x via solve(S, rhs) = [1. 3.] (preferred: faster and more accurate)
check S @ x = [ 5. 10.] == rhs [ 5. 10.]
S @ inv(S) ~ identity: True
det(singular) = 0.0
TRAP inverse of singular matrix: Singular matrix
```

### SECTION 4: norms
A norm is the "size" of a vector. The L2 norm is the ordinary length (`sqrt(3^2 + 4^2) = 5`); the L1 norm is the sum of absolute values. Dividing a vector by its L2 norm gives a unit vector. Cosine similarity, `a @ b / (|a| |b|)`, measures the angle between vectors and is used to compare text embeddings.

```text
=== SECTION 4: norms ===
L2 norm of [3, 4] = 5.0 (sqrt(3^2 + 4^2), the length)
L1 norm of [3, 4] = 7.0 (sum of absolute values)
unit vector: [0.6 0.8]
cosine similarity of [1,0] and [1,1] = 0.7071 (1 = same direction)
```

### SECTION 5: worked example, a neural-network layer
Two samples with three features each form `X` with shape `(2,3)`. A layer that maps 3 inputs to 2 outputs has a weight matrix `W` of shape `(3,2)` and a bias of length 2. The layer computes `Z = X @ W + bias`: `(2,3) @ (3,2)` gives `(2,2)`, and the bias is broadcast across both rows. The file checks one output by hand: 1x0.1 + 2x0.2 + 3x0.3 + 0.1 = 1.5. ReLU (`np.maximum(0, Z)`) then replaces negative numbers by 0. Training a network is the process of adjusting `W` and `bias`.

```text
=== SECTION 5: worked example, a neural-net layer is matmul + bias ===
X shape (2, 3)  W shape (3, 2)  Z shape (2, 2)
Z = X @ W + b =
[[ 1.5   1.1 ]
 [ 0.45 -0.3 ]]
by hand, sample 0 output 0: 1*0.1 + 2*0.2 + 3*0.3 + 0.1 = 1.5
after ReLU =
[[1.5  1.1 ]
 [0.45 0.  ]]
Training a network = adjusting W and bias; every layer is this same matmul.
```

## Key Differences From Java
| Idea | Java | Python with NumPy |
|---|---|---|
| Matrix | `double[][]` | `np.ndarray` with 2 dimensions |
| Multiply | Triple nested loop you write | `A @ B` |
| Dot product | Loop with accumulator | `u @ v` |
| Solve linear system | Write Gaussian elimination, or use EJML / Apache Commons Math | `np.linalg.solve(A, b)` |
| Operators | `*` is always number multiplication | `*` is element-wise, `@` is matrix multiplication |

How you would do this in Java: the JDK has no matrix type, so you write nested loops over `double[][]` or add a library such as EJML, Apache Commons Math or ND4J.

## Key Rules / Gotchas Recap
- `*` is element-wise; `@` is the matrix product.
- Matrix multiplication needs matching inner dimensions and is not commutative.
- Prefer `solve(A, b)` to `inv(A) @ b`.
- A singular matrix has no inverse (`LinAlgError`).
- A layer is `X @ W + b`, then an activation function.

## Why This Structure Exists
Embeddings, attention and every dense layer are matrix products. If you can predict the shape of `X @ W` in your head, you can debug most shape errors in model code, and cosine similarity is the core of semantic search in retrieval (RAG) systems.
