# Tags: #Python #Project #MachineLearning #NeuralNetworks #Tests #perceptron | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""pytest tests for perceptron.py."""

import ast
from pathlib import Path

import pytest

from perceptron import (
    GATE_INPUTS,
    GATES,
    Perceptron,
    best_linear_accuracy_grid,
    make_separable_data,
)


def test_init_is_seeded_and_deterministic():
    a, b = Perceptron(2, seed=1), Perceptron(2, seed=1)
    assert a.weights == b.weights and a.bias == b.bias
    assert Perceptron(2, seed=2).weights != a.weights


@pytest.mark.parametrize("gate", ["AND", "OR"])
def test_learns_linearly_separable_gates(gate):
    p = Perceptron(2, lr=0.1, seed=42)
    res = p.fit(GATE_INPUTS, GATES[gate], max_epochs=100)
    assert res.converged
    assert res.errors_per_epoch[-1] == 0
    assert p.predict(GATE_INPUTS) == GATES[gate]
    assert p.accuracy(GATE_INPUTS, GATES[gate]) == 1.0


def test_xor_is_not_learned():
    p = Perceptron(2, lr=0.1, seed=42)
    res = p.fit(GATE_INPUTS, GATES["XOR"], max_epochs=500)
    assert not res.converged
    assert res.epochs == 500
    assert p.accuracy(GATE_INPUTS, GATES["XOR"]) < 1.0


def test_xor_grid_search_never_reaches_100_percent():
    assert best_linear_accuracy_grid(GATE_INPUTS, GATES["XOR"], steps=20) < 1.0
    assert best_linear_accuracy_grid(GATE_INPUTS, GATES["AND"], steps=20) == 1.0


def test_separable_dataset_converges_and_generalises():
    X, y = make_separable_data(200, seed=42)
    Xt, yt = make_separable_data(200, seed=43)
    p = Perceptron(2, seed=42)
    res = p.fit(X, y, max_epochs=200)
    assert res.converged
    assert p.accuracy(X, y) == 1.0
    assert p.accuracy(Xt, yt) >= 0.9  # held-out data from the same rule


def test_same_seed_gives_identical_training():
    X, y = make_separable_data(100, seed=5)
    r1 = Perceptron(2, seed=9)
    r2 = Perceptron(2, seed=9)
    f1, f2 = r1.fit(X, y), r2.fit(X, y)
    assert f1.errors_per_epoch == f2.errors_per_epoch
    assert r1.weights == r2.weights and r1.bias == r2.bias


def test_update_rule_by_hand():
    p = Perceptron(2, lr=0.5, seed=0)
    p.weights, p.bias = [0.0, 0.0], 0.0
    # net input 0 -> predicts 1, true label 0 -> delta = -1
    res = p.fit([[1.0, 2.0]], [0], max_epochs=1, shuffle=False)
    assert res.errors_per_epoch == [1]
    assert p.weights == [-0.5, -1.0]
    assert p.bias == -0.5


def test_no_update_when_correct():
    p = Perceptron(2, lr=0.5, seed=0)
    p.weights, p.bias = [1.0, 1.0], 0.0
    res = p.fit([[1.0, 1.0]], [1], max_epochs=5, shuffle=False)
    assert res.converged and res.epochs == 1
    assert p.weights == [1.0, 1.0] and p.bias == 0.0


def test_separable_data_respects_margin_and_labels():
    X, y = make_separable_data(50, seed=3, margin=0.1)
    assert len(X) == len(y) == 50
    assert set(y) <= {0, 1}
    norm = 5**0.5
    for (x1, x2), label in zip(X, y):
        score = 2 * x1 - x2 + 0.3
        assert abs(score) / norm >= 0.1
        assert label == (1 if score > 0 else 0)


def test_input_validation():
    with pytest.raises(ValueError):
        Perceptron(0)
    with pytest.raises(ValueError):
        Perceptron(2, lr=0)
    p = Perceptron(2)
    with pytest.raises(ValueError):
        p.fit([[0.0, 0.0]], [0, 1])  # length mismatch
    with pytest.raises(ValueError):
        p.fit([[0.0]], [0])  # wrong feature count
    with pytest.raises(ValueError):
        p.fit([[0.0, 0.0]], [2])  # bad label
    with pytest.raises(ValueError):
        p.predict_one([1.0])


def test_module_uses_only_standard_library():
    """Guard the project rule: no numpy / ML libraries in perceptron.py."""
    tree = ast.parse((Path(__file__).parent / "perceptron.py").read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"__future__", "random", "dataclasses"}
