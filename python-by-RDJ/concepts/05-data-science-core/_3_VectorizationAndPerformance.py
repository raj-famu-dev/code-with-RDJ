# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Vectorisation: replacing Python loops with whole-array operations.
All timings printed here are MEASUREMENTS from this run on this machine.
They vary run to run; no number in this file is a claimed constant."""

import time

import numpy as np

N = 1_000_000


def best_of(fn, repeats: int = 3) -> float:
    """Return the smallest wall-clock time (seconds) over several runs."""
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best


# ===== SECTION 1: SAME RESULT, TWO STYLES =====
print("=== SECTION 1: loop vs vectorised (correctness first) ===")
rng = np.random.default_rng(0)
x = rng.random(N)
x_list = x.tolist()


def loop_sum_squares() -> float:
    total = 0.0
    for v in x_list:
        total += v * v
    return total


def vec_sum_squares() -> float:
    return float(np.sum(x * x))


a, b = loop_sum_squares(), vec_sum_squares()
print("loop result      =", round(a, 6))
print("vectorised result=", round(b, 6))
print("same to 6 places?", round(a, 6) == round(b, 6))

# ===== SECTION 2: MEASURED TIMINGS =====
print("\n=== SECTION 2: measured timings (MEASUREMENT, varies per run) ===")
t_loop = best_of(loop_sum_squares)
t_vec = best_of(vec_sum_squares)
print(f"MEASURED python loop : {t_loop * 1000:.2f} ms (best of 3, N={N:,})")
print(f"MEASURED numpy       : {t_vec * 1000:.2f} ms (best of 3, N={N:,})")
print(f"MEASURED ratio loop/numpy: about {t_loop / t_vec:.0f}x on this run only")

# ===== SECTION 3: WHY IT IS FASTER =====
print("\n=== SECTION 3: why ===")
print("The numpy loop runs in compiled C over contiguous typed memory;")
print("the Python loop runs bytecode and creates/unpacks a float object per step.")

# ===== SECTION 4: TRAP - HIDDEN PYTHON LOOPS =====
print("\n=== SECTION 4: trap - np.vectorize is a loop in disguise ===")
small = x[:200_000]


def py_square(v: float) -> float:
    return v * v


slow = np.vectorize(py_square)
t_vz = best_of(lambda: slow(small))
t_real = best_of(lambda: small * small)
print("same answer?", bool(np.allclose(slow(small), small * small)))
print(f"MEASURED np.vectorize : {t_vz * 1000:.2f} ms (n={len(small):,})")
print(f"MEASURED small * small: {t_real * 1000:.2f} ms (n={len(small):,})")
print("np.vectorize is a convenience wrapper, NOT a speed-up. Use real array operations.")

# ===== SECTION 5: TRAP - TEMPORARIES AND ITERATING OVER AN ARRAY =====
print("\n=== SECTION 5: trap - looping over an ndarray element by element ===")
arr = x[:200_000]


def loop_over_ndarray() -> float:
    total = 0.0
    for v in arr:  # each v is a numpy float64 scalar: boxing overhead
        total += v * v
    return total


def loop_over_list() -> float:
    total = 0.0
    for v in arr.tolist():
        total += v * v
    return total


print(f"MEASURED loop over ndarray: {best_of(loop_over_ndarray) * 1000:.2f} ms")
print(f"MEASURED loop over list   : {best_of(loop_over_list) * 1000:.2f} ms")
print("Iterating an ndarray in Python is usually no better than a list, often worse.")
print("Rule: if you write 'for' over array elements, look for a vectorised form.")

# ===== SECTION 6: WHEN LOOPS ARE STILL FINE =====
print("\n=== SECTION 6: when a loop is OK ===")
print("Loop over a handful of items, or when each step depends on the previous one")
print("(e.g. training epochs). Vectorise the INNER work, loop over the outer steps.")
