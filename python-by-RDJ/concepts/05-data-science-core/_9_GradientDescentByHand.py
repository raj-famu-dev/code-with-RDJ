# Tags: #Python #DataScience #NumPy #Pandas #GradientDescentByHand | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Linear regression trained by gradient descent in NumPy, on seeded synthetic
data: loss, gradient, learning rate, convergence, and a comparison with the
closed-form least-squares answer from np.linalg.lstsq."""

import numpy as np

np.set_printoptions(precision=4, suppress=True)

# ===== SECTION 1: SEEDED SYNTHETIC DATA =====
print("=== SECTION 1: synthetic data ===")
TRUE_W, TRUE_B = 3.0, 2.0
rng = np.random.default_rng(7)
x = rng.uniform(-2, 2, size=100)
y = TRUE_W * x + TRUE_B + rng.normal(0, 0.5, size=100)  # line + noise
print(f"truth used to generate data: y = {TRUE_W} * x + {TRUE_B} + noise(sd 0.5)")
print("first 3 samples (x, y):", [(round(float(a), 3), round(float(b), 3)) for a, b in zip(x[:3], y[:3])])

# ===== SECTION 2: LOSS AND GRADIENT =====
print("\n=== SECTION 2: loss and gradient ===")
print("model: y_hat = w*x + b")
print("loss (mean squared error): L = mean((y_hat - y)^2)")
print("gradient: dL/dw = mean(2*(y_hat - y)*x), dL/db = mean(2*(y_hat - y))")


def loss(w: float, b: float) -> float:
    return float(np.mean((w * x + b - y) ** 2))


def gradient(w: float, b: float) -> tuple[float, float]:
    err = w * x + b - y
    return float(np.mean(2 * err * x)), float(np.mean(2 * err))


# Check the analytic gradient against a numerical estimate (finite differences).
w0, b0, h = 0.5, -1.0, 1e-6
gw, gb = gradient(w0, b0)
num_gw = (loss(w0 + h, b0) - loss(w0 - h, b0)) / (2 * h)
num_gb = (loss(w0, b0 + h) - loss(w0, b0 - h)) / (2 * h)
print(f"at (w={w0}, b={b0}): analytic grad = ({gw:.5f}, {gb:.5f}) | numerical = ({num_gw:.5f}, {num_gb:.5f})")
print("gradients agree:", bool(np.allclose([gw, gb], [num_gw, num_gb], atol=1e-4)))


# ===== SECTION 3: THE DESCENT LOOP =====
print("\n=== SECTION 3: gradient descent ===")


def train(lr: float, steps: int, tol: float = 1e-10):
    """Return (w, b, loss_history, steps_used). Stops early when loss stops improving."""
    w, b = 0.0, 0.0
    hist = [loss(w, b)]
    for step in range(1, steps + 1):
        gw, gb = gradient(w, b)
        w -= lr * gw
        b -= lr * gb
        hist.append(loss(w, b))
        if abs(hist[-2] - hist[-1]) < tol:
            return w, b, hist, step
    return w, b, hist, steps


w, b, hist, used = train(lr=0.1, steps=5000)
print(f"lr=0.1 start loss = {hist[0]:.4f}")
for s in (1, 5, 10, 25, 50):
    if s < len(hist):
        print(f"  loss after step {s:>3} = {hist[s]:.6f}")
print(f"stopped after {used} steps; final loss = {hist[-1]:.6f}")
print(f"learned w = {w:.4f}, b = {b:.4f}  (truth {TRUE_W}, {TRUE_B})")
print("loss never increased:", all(hist[i + 1] <= hist[i] + 1e-12 for i in range(len(hist) - 1)))

# ===== SECTION 4: LEARNING RATE =====
print("\n=== SECTION 4: learning rate ===")
for lr in (0.001, 0.01, 0.1, 0.5):
    _, _, h_, n_ = train(lr, steps=300)
    print(f"lr={lr:<6} final loss after {n_:>3} steps = {h_[-1]:.6f}")
print("Too small: still far away after the step budget. Reasonable: converges.")
_, _, h_big, _ = train(1.2, steps=30)
print(f"TRAP lr=1.2: loss after 30 steps = {h_big[-1]:.3e} (diverged: each step overshoots more)")
print("FIX: lower the learning rate (or scale the features).")

# ===== SECTION 5: COMPARE WITH CLOSED FORM =====
print("\n=== SECTION 5: compare with np.linalg.lstsq ===")
X = np.column_stack([x, np.ones_like(x)])  # design matrix [x, 1]
coef, *_ = np.linalg.lstsq(X, y, rcond=None)
print(f"lstsq (exact least squares): w = {coef[0]:.4f}, b = {coef[1]:.4f}")
print(f"gradient descent:            w = {w:.4f}, b = {b:.4f}")
print("max abs difference =", f"{max(abs(w - coef[0]), abs(b - coef[1])):.2e}")
print("Both minimise the same loss; descent reaches the answer iteratively.")
print(f"loss at lstsq = {loss(coef[0], coef[1]):.6f} | loss at descent = {loss(w, b):.6f}")
print("Why use descent at all? Neural nets have no closed form; this loop IS how they train.")
