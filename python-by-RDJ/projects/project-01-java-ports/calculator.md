# `calculator.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A calculator that never crashes: basic operations (add, subtract, multiply, divide, modulus), extras (power, square root, percentage), a 10-item history, one memory slot, and the "Possible Extension" from the Java spec, expression parsing (`2 + 3 * 4`) with correct operator precedence. The expression evaluator is a hand-written recursive-descent parser. It does not use `eval()`, which would execute arbitrary Python code typed by the user.

## Full Line-by-Line Breakdown

### SECTION 1: operations
- `CalculatorError(ValueError)` marks problems caused by the user's input (not program bugs). The CLI catches only this and prints `Error: ...`.
- Each operation is its own small function (Java: "each operation is its own method"). `divide` and `modulus` check for zero first. `sqrt` rejects negatives. Nothing returns `inf` or `nan` silently: `_finite()` raises if a result overflows.
- `power` uses `math.pow`, not `**`. Gotcha: `(-8) ** 0.5` in Python returns a complex number instead of failing, and `0 ** -1` raises `ZeroDivisionError`. `math.pow` raises `ValueError`/`OverflowError`, which are converted to clear messages.
- `modulus` uses `math.fmod`, so `-7 % 4` is `-3` like Java. Python's own `%` would give `1` (floored). Tests lock this in.
- `percent(200, 15)` means "15 percent of 200" = 30.
- `format_number` prints 12 significant digits (`f"{x:.12g}"`), which hides float noise: `0.1 + 0.2` is really `0.30000000000000004` but shows as `0.3`. Negative zero shows as `0`. Design note (the Java spec asks "why `double`"): Python's `float` is a 64-bit IEEE double, the same as Java's `double`, so the same `0.1 + 0.2` effect exists and is handled by display rounding.

### SECTION 2: tokenizer and parser
- `tokenize` uses one regex to produce `(kind, value)` tokens: numbers (`12`, `3.`, `.5`), the word `sqrt`, and the operators `+ - * / % ^ ( )`. Any other character raises `CalculatorError("Unexpected character ...")`.
- `_Parser` implements the grammar written in its docstring. Precedence comes from the call chain: `_expr` (+, -) calls `_term` (*, /, %) calls `_unary` calls `_power` calls `_atom`. The deeper the function, the tighter the binding, so `2+3*4` multiplies first.
- `+`/`-`/`*`/`/` loops (`while op := ...`) are left-associative: `10-4-3` is `(10-4)-3 = 3`.
- `^` is right-associative: `2^3^2` is `2^(3^2) = 512`. Unary minus is looser than `^`, so `-2^2` is `-(2^2) = -4` (same as Python). `(-2)^2` is 4.
- Division by zero etc. are reported by the same operation functions, so `1/0` inside an expression gives the same message.
- Missing parentheses, trailing tokens (`2 3`), empty input and `2**3` all raise `CalculatorError`. A pathological 5000-deep nesting triggers `RecursionError`, which is caught and reported.
- `parse_number` is for the menu prompts. `float("nan")` and `float("inf")` are valid in Python, so a regex check is used before converting.

### SECTION 3: stateful calculator
`Calculator` holds `history = deque(maxlen=10)`: when full, appending drops the oldest entry automatically (the Java spec asks what happens when the history is full: oldest is dropped). Only successful calculations are recorded. Memory is `None` (empty) or a float; `0.0` is a legitimate stored value, which is why emptiness is tested with `is None`, not truthiness.

### SECTION 4: interactive layer
`run(read, write)` prints the menu and routes each choice. Every operation runs inside one `try/except CalculatorError`, so a bad entry prints `Error: ...` and the loop continues.

Real output from `printf '4\n1\n0\n7\n-4\n1\nabc\n1\n0.1\n0.2\n9\n2+3*4^2\n9\n-2^2\n9\n(1+2\n10\n11\n42\n12\n0\n' | python3 calculator.py` (menu text removed for length; exit code 0):

```text
Choose an option: First number: Second number: Error: Cannot divide by zero.

Choose an option: Number: Error: Cannot take the square root of a negative number.

Choose an option: First number: Error: That's not a number.

Choose an option: First number: Second number: Result: 0.3

Choose an option: Expression: Result: 50

Choose an option: Expression: Result: -4

Choose an option: Expression: Error: Missing ')'.

Choose an option: 1. 0.1 + 0.2 = 0.3
2. 2+3*4^2 = 50
3. -2^2 = -4

Choose an option: Value to store: Stored.

Choose an option: Memory: 42

Choose an option: Goodbye!
```

### Requirements self-check
| Requirement | Where |
|---|---|
| Basic ops, extra ops | `add` ... `percent`, menu 1-8 |
| Divide by zero / sqrt negative reported, no `inf`/`nan` | `divide`, `modulus`, `sqrt`, `_finite`, tests `test_math_errors` |
| History of last 10 | `Calculator.history` (`deque(maxlen=10)`) |
| Memory store/recall/clear | `memory_*`, menu 11-13 |
| Exit | menu `0` |
| Non-numeric input recovers | `parse_number` + `except CalculatorError` |
| No `3.0000000000000004` shown | `format_number` |
| Expression parsing with precedence | `_Parser`, `evaluate`, menu 9 |

## Key Differences From Java

| Java | Python |
|---|---|
| `hasNextDouble()` pattern | regex + `parse_number`, raise on failure |
| `%` is truncating remainder | Python `%` floors; `math.fmod` reproduces Java |
| fixed array + counter for history | `collections.deque(maxlen=10)` |
| `Math.sqrt(-1)` returns `NaN` silently | `math.sqrt(-1)` raises `ValueError`; we raise our own message first |
| `Math.pow` returns `NaN`/`Infinity` | `math.pow` raises; `**` can return a complex number |
| `Double.POSITIVE_INFINITY` from overflow | `float` overflow can give `inf` on `*`/`+`: checked with `math.isfinite` |
| no `eval` in Java | Python has `eval()`: never use it on user input |

## Key Rules / Gotchas Recap
- Never use `eval()` on typed input; write a parser.
- `x ** y` can return `complex`; `math.pow` cannot.
- `float("nan")`, `float("inf")` and `float("1e999")` parse successfully: check `math.isfinite`.
- Python `%` is floored, Java `%` is truncated; pick on purpose.
- Precedence is encoded in which function calls which; left- vs right-associativity is a loop vs a recursive call.
- `bool(0.0)` is `False`: test `memory is None`, not `if memory`.

## Why This Structure Exists
Tokenize, parse, evaluate is the same pipeline behind query languages, config parsers and tool-calling argument validators. Parsing untrusted text with your own small grammar instead of `eval()` is also a basic security habit.
