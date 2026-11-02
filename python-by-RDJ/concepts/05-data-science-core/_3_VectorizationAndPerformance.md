# `_3_VectorizationAndPerformance.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Vectorisation means replacing a Python `for` loop with one whole-array operation so the looping happens inside NumPy's compiled C code. On typical hardware that is dramatically faster, but how much faster depends on the machine and the operation, so this file measures instead of claiming numbers. Every timing printed here is labelled `MEASURED` and will differ each time you run the file.

## Full Line-by-Line Breakdown

### SECTION 1: loop vs vectorised (correctness first)
A fast wrong answer is useless, so the file first checks that a plain Python loop (`total += v * v`) and the NumPy expression `np.sum(x * x)` agree on one million seeded random numbers. The data are generated with `default_rng(0)`, so the printed sum is the same on every run (to 6 decimals).

```text
=== SECTION 1: loop vs vectorised (correctness first) ===
loop result      = 333560.615743
vectorised result= 333560.615743
same to 6 places? True
```

### SECTION 2: measured timings
`best_of` runs a function three times with `time.perf_counter()` and keeps the smallest time, which reduces noise from other programs on the machine. The numbers below are one real run on the machine that built this walkthrough. Run the file yourself: your numbers will differ, and so will a second run of the same file. The only thing to take from them is the rough shape (the loop is much slower than the array operation), not the digits.

```text
=== SECTION 2: measured timings (MEASUREMENT, varies per run) ===
MEASURED python loop : 18.60 ms (best of 3, N=1,000,000)
MEASURED numpy       : 1.44 ms (best of 3, N=1,000,000)
MEASURED ratio loop/numpy: about 13x on this run only
```

### SECTION 3: why
The NumPy version loops in compiled code over a contiguous block of raw 64-bit floats. The Python loop interprets bytecode for every step and handles a boxed float object each time.

```text
=== SECTION 3: why ===
The numpy loop runs in compiled C over contiguous typed memory;
the Python loop runs bytecode and creates/unpacks a float object per step.
```

### SECTION 4: trap - np.vectorize is a loop in disguise
`np.vectorize(f)` looks like it speeds a function up, but its own documentation describes it as a convenience that is essentially a Python `for` loop. The file measures it against the genuine array operation `small * small`; the vectorised-in-name version is far slower than the real one.

```text
=== SECTION 4: trap - np.vectorize is a loop in disguise ===
same answer? True
MEASURED np.vectorize : 18.20 ms (n=200,000)
MEASURED small * small: 0.14 ms (n=200,000)
np.vectorize is a convenience wrapper, NOT a speed-up. Use real array operations.
```

### SECTION 5: trap - looping over an ndarray element by element
Writing `for v in arr:` over an ndarray hands you a NumPy scalar each step, which has more overhead than a plain Python float. The measurement here shows it is slower than looping over `arr.tolist()`. The lesson: do not loop over arrays in Python; look for the whole-array form.

```text
=== SECTION 5: trap - looping over an ndarray element by element ===
MEASURED loop over ndarray: 19.47 ms
MEASURED loop over list   : 6.81 ms
Iterating an ndarray in Python is usually no better than a list, often worse.
Rule: if you write 'for' over array elements, look for a vectorised form.
```

### SECTION 6: when a loop is OK
Some work is inherently sequential (each training step depends on the previous one), or small. Loop over those outer steps, but keep the inner maths vectorised.

```text
=== SECTION 6: when a loop is OK ===
Loop over a handful of items, or when each step depends on the previous one
(e.g. training epochs). Vectorise the INNER work, loop over the outer steps.
```

## Key Differences From Java
| Idea | Java | Python with NumPy |
|---|---|---|
| Plain loops | Fast: the JIT compiler turns a `for` loop over `double[]` into efficient machine code | Slow in pure Python (interpreted bytecode, boxed objects) |
| How to go fast | Write the loop; the JIT does the work | Avoid the Python loop: use whole-array operations |
| Array-wide maths | Not in the JDK (loops, streams, or a library such as ND4J) | `x * x`, `np.sum`, `np.dot` |
| Timing | `System.nanoTime()` (and JMH for serious benchmarks) | `time.perf_counter()` (and `timeit` for serious benchmarks) |

How you would do this in Java: a plain `for` loop over a `double[]` is already compiled to fast code by the JIT, so Java programmers are not forced to "vectorise" for speed. In Python the loop itself is the slow part, which is why the habit has to change. Do not assume this file's ratio applies to Java; it compares Python to NumPy only.

## Key Rules / Gotchas Recap
- Write a Python `for` over array elements only as a last resort.
- `np.vectorize` does not make code fast.
- Iterating an ndarray element by element can be slower than iterating a list.
- Always check correctness (here with a result comparison) before comparing speed.
- Report timings as measurements with the conditions; never as constants.

## Why This Structure Exists
Training and running models means doing the same maths over millions of numbers. If you accidentally write a Python loop where a vectorised form exists, a job that should take seconds can take far longer, and this is one of the first performance problems every AI engineer meets.
