# `_9_GradientDescentByHand.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Gradient descent trains a model by repeatedly nudging its parameters in the direction that reduces a loss (a number measuring how wrong the model is). Here the model is a straight line `y_hat = w*x + b`, the loss is mean squared error, and the gradient (the slope of the loss with respect to `w` and `b`) is computed with NumPy. Linear regression also has an exact closed-form answer, so the file checks the descent result against `np.linalg.lstsq`. The same loop, with more parameters and a longer gradient, is how neural networks are trained.

## Full Line-by-Line Breakdown

### SECTION 1: synthetic data
The data are made up on purpose so the true answer is known: `y = 3x + 2` plus Gaussian noise with standard deviation 0.5, generated with a seeded generator (`default_rng(7)`), so the same 100 points appear on every run.

```text
=== SECTION 1: synthetic data ===
truth used to generate data: y = 3.0 * x + 2.0 + noise(sd 0.5)
first 3 samples (x, y): [(0.5, 2.483), (1.589, 6.614), (1.103, 4.858)]
```

### SECTION 2: loss and gradient
Mean squared error is `mean((w*x + b - y)^2)`. Using calculus, its derivatives are `mean(2*err*x)` for `w` and `mean(2*err)` for `b`, where `err = y_hat - y`. Rather than trust the formula, the file compares it with a numerical estimate (central finite differences: nudge `w` up and down by a tiny `h` and see how the loss changes). They agree to five decimals, which is the standard way to check a gradient (a "gradient check").

```text
=== SECTION 2: loss and gradient ===
model: y_hat = w*x + b
loss (mean squared error): L = mean((y_hat - y)^2)
gradient: dL/dw = mean(2*(y_hat - y)*x), dL/db = mean(2*(y_hat - y))
at (w=0.5, b=-1.0): analytic grad = (-6.23083, -5.55113) | numerical = (-6.23083, -5.55113)
gradients agree: True
```

### SECTION 3: the descent loop
Start at `w = 0, b = 0`. Each step does `w -= lr * gradient_w` and `b -= lr * gradient_b`: move a small step downhill. The learning rate `lr` sets the step size. The loop stops when the loss improves by less than `1e-10` (convergence). The printout shows loss falling fast, then flattening. The learned parameters are close to, but not exactly, the truth (3 and 2), because the noise in the 100 samples shifts the best-fit line slightly; that is expected, not a bug.

```text
=== SECTION 3: gradient descent ===
lr=0.1 start loss = 14.9781
  loss after step   1 = 8.714805
  loss after step   5 = 1.219016
  loss after step  10 = 0.277190
  loss after step  25 = 0.189265
  loss after step  50 = 0.189166
stopped after 55 steps; final loss = 0.189166
learned w = 2.9652, b = 1.9345  (truth 3.0, 2.0)
loss never increased: True
```

### SECTION 4: learning rate
Four learning rates are tried with a 300-step budget. 0.001 is too small to get there in time (loss still high); 0.01 gets close; 0.1 and 0.5 converge in tens of steps. The trap: 1.2 is too large, each step overshoots the minimum by more than the last, and the loss explodes (the printed value is huge). The fix is a smaller learning rate or scaled features. The exact step counts depend on this dataset and seed.

```text
=== SECTION 4: learning rate ===
lr=0.001  final loss after 300 steps = 3.736330
lr=0.01   final loss after 300 steps = 0.189204
lr=0.1    final loss after  55 steps = 0.189166
lr=0.5    final loss after  14 steps = 0.189166
Too small: still far away after the step budget. Reasonable: converges.
TRAP lr=1.2: loss after 30 steps = 1.070e+22 (diverged: each step overshoots more)
FIX: lower the learning rate (or scale the features).
```

### SECTION 5: compare with np.linalg.lstsq
Linear regression can be solved directly: stack `x` with a column of ones to form a design matrix and ask `lstsq` for the least-squares solution. Gradient descent lands on the same `w` and `b` (difference printed, about 1e-5) and the same loss. The point of doing it the slow way: models such as neural networks have no closed form, so iterative descent is the only practical method.

```text
=== SECTION 5: compare with np.linalg.lstsq ===
lstsq (exact least squares): w = 2.9652, b = 1.9345
gradient descent:            w = 2.9652, b = 1.9345
max abs difference = 1.32e-05
Both minimise the same loss; descent reaches the answer iteratively.
loss at lstsq = 0.189166 | loss at descent = 0.189166
Why use descent at all? Neural nets have no closed form; this loop IS how they train.
```

## Key Differences From Java
| Idea | Java | Python with NumPy |
|---|---|---|
| Vector maths per step | Loops over `double[]` for predictions and gradients | `w * x + b`, `np.mean(...)` on whole arrays |
| Least squares | Apache Commons Math `OLSMultipleLinearRegression` or EJML | `np.linalg.lstsq` |
| Seeded randomness | `new Random(7)` | `np.random.default_rng(7)` |
| Returning several values | Wrap them in a record or class | Return a tuple: `return w, b, hist, steps` |

How you would do this in Java: the loop and the update rule are identical, but predictions and gradients become explicit `for` loops over `double[]`, and an exact solution needs a library such as Apache Commons Math. Java is fine for the algorithm; it just lacks the array maths built in.

## Key Rules / Gotchas Recap
- Loss measures error; the gradient points uphill, so you subtract it.
- Check a hand-derived gradient against finite differences.
- Learning rate too small is slow; too large diverges.
- Seed all randomness so a run can be reproduced.
- The result is close to, not equal to, the true parameters because of noise in the sample.
- Gradient descent and `lstsq` minimise the same loss, so they should agree on this problem.

## Why This Structure Exists
This is a miniature version of model training: define a loss, compute gradients, update parameters, watch the loss, tune the learning rate. Frameworks like PyTorch automate the gradient step, but the loop and the failure modes (divergence, slow convergence) are the same.
