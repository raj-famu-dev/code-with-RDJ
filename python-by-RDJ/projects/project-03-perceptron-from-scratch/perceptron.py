# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Single-layer perceptron from scratch (standard library only, no numpy).

Learning rule (Rosenblatt): for each sample (x, y) with y in {0, 1},
    prediction = 1 if w.x + b >= 0 else 0
    w <- w + lr * (y - prediction) * x
    b <- b + lr * (y - prediction)
Weights change only when the prediction is wrong.

Run `python3 perceptron.py` to train on AND, OR, a seeded linearly separable
2-D dataset, and to see that XOR cannot be learned by a single layer.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

Sample = list[float]


def _validate(X: list[Sample], y: list[int], n_inputs: int) -> None:
    """Raise ValueError if the data is malformed."""
    if len(X) != len(y):
        raise ValueError(f"X has {len(X)} rows but y has {len(y)} labels")
    if not X:
        raise ValueError("need at least one sample")
    for row in X:
        if len(row) != n_inputs:
            raise ValueError(f"each sample needs {n_inputs} features, got {len(row)}")
    if any(label not in (0, 1) for label in y):
        raise ValueError("labels must be 0 or 1")


@dataclass
class FitResult:
    """What fit() reports back."""

    converged: bool
    epochs: int  # epochs run; if converged, the last one had zero mistakes
    errors_per_epoch: list[int] = field(default_factory=list)

    @property
    def updates_epochs(self) -> int:
        """Number of epochs that actually changed the weights."""
        return sum(1 for e in self.errors_per_epoch if e > 0)


class Perceptron:
    """A single neuron with a step activation and the perceptron learning rule."""

    def __init__(self, n_inputs: int, lr: float = 0.1, seed: int = 0) -> None:
        if n_inputs < 1:
            raise ValueError("n_inputs must be >= 1")
        if lr <= 0:
            raise ValueError("lr must be > 0")
        self.n_inputs = n_inputs
        self.lr = lr
        self._rng = random.Random(seed)  # private seeded RNG, never the global one
        self.weights: list[float] = [self._rng.uniform(-0.5, 0.5) for _ in range(n_inputs)]
        self.bias: float = self._rng.uniform(-0.5, 0.5)

    def net_input(self, x: Sample) -> float:
        """w . x + b"""
        if len(x) != self.n_inputs:
            raise ValueError(f"expected {self.n_inputs} features, got {len(x)}")
        return sum(w * xi for w, xi in zip(self.weights, x)) + self.bias

    def predict_one(self, x: Sample) -> int:
        """Step activation: 1 if net input >= 0 else 0."""
        return 1 if self.net_input(x) >= 0 else 0

    def predict(self, X: list[Sample]) -> list[int]:
        return [self.predict_one(x) for x in X]

    def accuracy(self, X: list[Sample], y: list[int]) -> float:
        """Fraction of samples classified correctly (0.0 to 1.0)."""
        _validate(X, y, self.n_inputs)
        correct = sum(1 for p, t in zip(self.predict(X), y) if p == t)
        return correct / len(y)

    def fit(self, X: list[Sample], y: list[int], max_epochs: int = 100, shuffle: bool = True) -> FitResult:
        """Train with the perceptron rule. Stops at the first epoch with zero mistakes."""
        _validate(X, y, self.n_inputs)
        order = list(range(len(X)))
        errors_per_epoch: list[int] = []
        for epoch in range(1, max_epochs + 1):
            if shuffle:
                self._rng.shuffle(order)
            mistakes = 0
            for i in order:
                delta = y[i] - self.predict_one(X[i])  # -1, 0 or +1
                if delta != 0:
                    mistakes += 1
                    for j in range(self.n_inputs):
                        self.weights[j] += self.lr * delta * X[i][j]
                    self.bias += self.lr * delta
            errors_per_epoch.append(mistakes)
            if mistakes == 0:
                return FitResult(True, epoch, errors_per_epoch)
        return FitResult(False, max_epochs, errors_per_epoch)


def make_separable_data(n: int, seed: int, margin: float = 0.1) -> tuple[list[Sample], list[int]]:
    """Seeded 2-D points labelled by the line 2*x1 - x2 + 0.3 = 0.

    Points closer than `margin` to the line are rejected, which guarantees the
    classes are separable with a gap (so the perceptron convergence theorem applies).
    """
    rng = random.Random(seed)
    norm = (2.0**2 + 1.0**2) ** 0.5
    X: list[Sample] = []
    y: list[int] = []
    while len(X) < n:
        x1, x2 = rng.uniform(-1, 1), rng.uniform(-1, 1)
        score = 2.0 * x1 - x2 + 0.3
        if abs(score) / norm < margin:
            continue
        X.append([x1, x2])
        y.append(1 if score > 0 else 0)
    return X, y


GATE_INPUTS: list[Sample] = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
GATES: dict[str, list[int]] = {
    "AND": [0, 0, 0, 1],
    "OR": [0, 1, 1, 1],
    "XOR": [0, 1, 1, 0],
}


def best_linear_accuracy_grid(X: list[Sample], y: list[int], steps: int = 40, span: float = 2.0) -> float:
    """Brute-force check: best accuracy over a grid of (w1, w2, b) in [-span, span].

    This is an illustration, NOT a proof: it only tries grid points.
    """
    best = 0.0
    vals = [-span + 2 * span * i / steps for i in range(steps + 1)]
    for w1 in vals:
        for w2 in vals:
            for b in vals:
                correct = sum(1 for (a, c), t in zip(X, y) if (1 if w1 * a + w2 * c + b >= 0 else 0) == t)
                best = max(best, correct / len(y))
    return best


def main() -> None:
    SEED = 42
    print(f"Seed = {SEED}; learning rate = 0.1; max epochs = 100 (XOR: 1000)")

    print("\n--- Logic gates (4 samples each) ---")
    for name in ("AND", "OR"):
        p = Perceptron(2, lr=0.1, seed=SEED)
        res = p.fit(GATE_INPUTS, GATES[name], max_epochs=100)
        acc = p.accuracy(GATE_INPUTS, GATES[name])
        print(
            f"{name}: converged={res.converged} epochs={res.epochs} "
            f"(epochs with updates={res.updates_epochs}) accuracy={acc:.0%} "
            f"weights=({p.weights[0]:.3f}, {p.weights[1]:.3f}) bias={p.bias:.3f}"
        )

    print("\n--- Seeded linearly separable 2-D dataset ---")
    X_train, y_train = make_separable_data(200, seed=SEED)
    X_test, y_test = make_separable_data(200, seed=SEED + 1)
    p = Perceptron(2, lr=0.1, seed=SEED)
    res = p.fit(X_train, y_train, max_epochs=100)
    print(f"train samples={len(X_train)} test samples={len(X_test)} (disjoint seeds)")
    print(f"converged={res.converged} epochs={res.epochs} mistakes per epoch={res.errors_per_epoch}")
    print(f"train accuracy={p.accuracy(X_train, y_train):.1%} test accuracy={p.accuracy(X_test, y_test):.1%}")
    print(f"learned weights=({p.weights[0]:.3f}, {p.weights[1]:.3f}) bias={p.bias:.3f}")
    print("true boundary direction is (2, -1) with bias 0.3: compare ratios, not raw values")
    print(f"learned w1/w2 = {p.weights[0] / p.weights[1]:.3f} (true -2.000); bias/|w2| = {p.bias / abs(p.weights[1]):.3f} (true 0.300)")

    print("\n--- XOR: a single layer cannot learn it ---")
    p = Perceptron(2, lr=0.1, seed=SEED)
    res = p.fit(GATE_INPUTS, GATES["XOR"], max_epochs=1000)
    acc = p.accuracy(GATE_INPUTS, GATES["XOR"])
    print(f"XOR: converged={res.converged} epochs run={res.epochs}")
    print(f"mistakes per epoch: min={min(res.errors_per_epoch)} max={max(res.errors_per_epoch)} last={res.errors_per_epoch[-1]}")
    print(f"final accuracy={acc:.0%} (4 points, so only 0%, 25%, 50%, 75% or 100% are possible)")
    best = best_linear_accuracy_grid(GATE_INPUTS, GATES["XOR"])
    print(f"grid search over 41^3 = {41**3} weight settings: best XOR accuracy = {best:.0%} (illustration, not a proof)")
    print("Why: XOR needs the points (0,1),(1,0) on one side of a line and (0,0),(1,1) on the other;")
    print("no straight line does that. A hidden layer (multi-layer network) is needed.")


if __name__ == "__main__":
    main()
