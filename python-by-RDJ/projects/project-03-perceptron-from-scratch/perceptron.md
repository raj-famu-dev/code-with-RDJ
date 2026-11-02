# `perceptron.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A perceptron is the simplest artificial neuron: it multiplies each input by a weight, adds a bias, and outputs 1 if the total is zero or more, otherwise 0. Training means adjusting the weights whenever the neuron gets a sample wrong. It can only draw one straight line (in 2-D) between two classes, so it learns AND and OR but can never learn XOR. This project builds one in plain Python (standard library only, no NumPy) so every step of learning is visible.

## The maths
- Net input: `z = w1*x1 + w2*x2 + ... + b` (a dot product plus a bias).
- Activation (step function): `prediction = 1 if z >= 0 else 0`.
- Learning rule, applied to each training sample with true label `y`:
  - `error = y - prediction` (this is -1, 0 or +1)
  - `w_j = w_j + lr * error * x_j`
  - `b = b + lr * error`
- `lr` is the learning rate (step size). If the prediction is right, `error = 0` and nothing changes.
- Geometry: `z = 0` is a line. Points above it are class 1, points below are class 0. A wrong prediction nudges the line toward the misclassified point.
- Perceptron convergence theorem: if the two classes can be separated by a straight line, this rule reaches zero mistakes in a finite number of updates. If they cannot (XOR), it never settles.

Tiny worked example (the same one used in `test_update_rule_by_hand`): start with `w = [0, 0]`, `b = 0`, `lr = 0.5`, and one sample `x = [1, 2]` with label 0. Net input is 0, so the prediction is 1 (wrong). Error is `0 - 1 = -1`, so `w = [0 + 0.5*(-1)*1, 0 + 0.5*(-1)*2] = [-0.5, -1.0]` and `b = -0.5`. Net input is now `-0.5 - 2.0 - 0.5 = -3`, so the prediction is 0 (right).

## Line-by-Line Breakdown

### Imports and types (lines 14-19)
`random` gives a seedable random number generator, `dataclass` writes the boilerplate for a small result class. `Sample = list[float]` is just a readable name for one data row. Nothing outside the standard library is imported (a test enforces this).

### `_validate` (lines 22-32)
Checks that `X` and `y` have equal length, that there is at least one sample, that every row has the right number of features, and that labels are 0 or 1. It raises `ValueError` with a clear message instead of failing later with a confusing error.

### `FitResult` (lines 35-46)
A small record of how training went: `converged` (did an epoch with zero mistakes occur), `epochs` (how many epochs ran; if converged, the final one is the clean pass with zero mistakes, so it is counted), and `errors_per_epoch` (a list of mistake counts). `updates_epochs` counts epochs where the weights changed.

### `Perceptron.__init__` (lines 52-61)
Creates a private `random.Random(seed)` so results are reproducible and the global random state is untouched. Weights and bias start as small random numbers in [-0.5, 0.5]. Bad arguments raise `ValueError`.

### `net_input`, `predict_one`, `predict`, `accuracy` (lines 63-80)
`net_input` is `sum(w * x) + bias`. `predict_one` applies the step function. `predict` maps it over many samples. `accuracy` is the fraction of correct predictions, from 0.0 to 1.0.

### `fit` (lines 82-101)
The training loop. Each epoch (one pass over all samples) optionally shuffles the visiting order with the seeded RNG. For every sample it computes `delta = y - prediction`; if `delta` is not 0 it counts a mistake and updates every weight and the bias with the rule above. If an entire epoch has zero mistakes, it stops and reports success. If `max_epochs` is reached first, it reports `converged=False`.

### `make_separable_data` (lines 104-121)
Generates points uniformly in the square [-1, 1] x [-1, 1] using a seeded RNG, and labels each by which side of the line `2*x1 - x2 + 0.3 = 0` it falls on. Points within `margin` of the line are thrown away, which guarantees a gap between the classes so convergence is guaranteed by the theorem. Different seeds give different datasets drawn from the same rule, which is how the test set is made.

### Gates and `best_linear_accuracy_grid` (lines 124-144)
`GATE_INPUTS` and `GATES` hold the four input pairs and the truth tables for AND, OR and XOR. `best_linear_accuracy_grid` tries 41 x 41 x 41 = 68,921 combinations of `(w1, w2, b)` between -2 and 2 and returns the best accuracy any of them achieves. This is an illustration that supports the XOR claim, not a mathematical proof (it only tests grid points).

### `main` (lines 147-185)
Trains on AND, OR, a 200-sample separable dataset (tested on a different 200-sample set), and XOR (1000 epochs), printing results.

## Real output
Copied from `python3 perceptron.py` (seed 42; two runs produced identical output):

```text
Seed = 42; learning rate = 0.1; max epochs = 100 (XOR: 1000)

--- Logic gates (4 samples each) ---
AND: converged=True epochs=8 (epochs with updates=7) accuracy=100% weights=(0.139, 0.125) bias=-0.225
OR: converged=True epochs=6 (epochs with updates=5) accuracy=100% weights=(0.239, 0.025) bias=-0.025

--- Seeded linearly separable 2-D dataset ---
train samples=200 test samples=200 (disjoint seeds)
converged=True epochs=2 mistakes per epoch=[5, 0]
train accuracy=100.0% test accuracy=100.0%
learned weights=(0.448, -0.265) bias=0.075
true boundary direction is (2, -1) with bias 0.3: compare ratios, not raw values
learned w1/w2 = -1.693 (true -2.000); bias/|w2| = 0.284 (true 0.300)

--- XOR: a single layer cannot learn it ---
XOR: converged=False epochs run=1000
mistakes per epoch: min=1 max=4 last=3
final accuracy=75% (4 points, so only 0%, 25%, 50%, 75% or 100% are possible)
grid search over 41^3 = 68921 weight settings: best XOR accuracy = 75% (illustration, not a proof)
Why: XOR needs the points (0,1),(1,0) on one side of a line and (0,0),(1,1) on the other;
no straight line does that. A hidden layer (multi-layer network) is needed.
```

How to read it:
- AND and OR converge in a handful of epochs. Exact counts depend on the seed and starting weights.
- On the separable dataset the first epoch had 5 mistakes and the second had 0, so it converged after 2 epochs, with 100% train and test accuracy on this seed. The learned line is close to, not identical to, the generating line, because the perceptron stops at the first line that separates the training data, not the best line.
- XOR: 1000 epochs, never converged, and mistakes never reached 0 (the minimum in any epoch was 1). The final weights classify 3 of 4 points correctly. The grid search also found no setting above 75%.

## Limitations
- Only linearly separable problems can be learned. XOR (and any problem needing a curved boundary) is impossible for a single layer; fixing it needs a hidden layer and a smoother activation trained with backpropagation.
- Convergence is guaranteed only for separable data. On noisy, overlapping data the weights keep changing and the result depends on when you stop.
- It finds some separating line, not the best one (no margin maximisation, unlike an SVM).
- Binary labels 0/1 only; no probabilities (unlike logistic regression).
- Features are not scaled; badly scaled data can slow learning.
- Pure Python lists are slow for large datasets; this is for understanding, not for production.
- Results here are for one seed (42). Other seeds give other epoch counts. Nothing here claims a general average.

## Tests
`python3 -m pytest -q` in this folder: `12 passed in 0.03s`. See `README.md` for what is covered.
