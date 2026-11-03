# 🐍 python-by-RDJ — Complete Study Notes

> One consolidated reference covering every topic in this repository, with detailed explanations.
> Source: all 5 completed concept modules (45 topics) and the 3 completed projects.
> Every script here runs on Python 3.13 with exit 0 — no keyboard input, no internet (network code is loopback-only).

---

## 📑 Table of Contents

1. [Module 01 — Python Basics](#module-01--python-basics)
2. [Module 02 — OOP and Modules](#module-02--oop-and-modules)
3. [Module 03 — File I/O and JSON](#module-03--file-io-and-json)
4. [Module 04 — Network Sockets](#module-04--network-sockets)
5. [Module 05 — Data Science Core](#module-05--data-science-core)
6. [Project 01 — Java Ports](#project-01--java-ports)
7. [Project 02 — Network Scanner](#project-02--network-scanner)
8. [Project 03 — Perceptron From Scratch](#project-03--perceptron-from-scratch)

---

# Module 01 — Python Basics

*Folder:* [`concepts/01-basics`](./concepts/01-basics) · ✅ Complete · **11 topics** · written by RDJ himself

### 1. Hello World
```python
print("Hello World")
```
- No class boilerplate, no semicolons — the program *is* the script.
- `print` adds a newline; `end=""` suppresses it.
- Everything runs top to bottom; indentation (4 spaces) defines blocks instead of braces.

### 2. Variables & Data Types
- **Dynamically typed:** a variable is just a name bound to an object; the *object* has the type, not the variable.
- Core types: `int` (arbitrary precision — no overflow, ever), `float` (64-bit, has `inf`/`nan`), `complex`, `bool` (subclass of `int`: `True + True == 2`), `str` (immutable), `bytes`, `None`.
- `type(x)` reports the type; `isinstance(x, int)` checks it.
- **Everything is an object** — even functions and classes can be assigned to variables and passed around.
- Python vs Java: no declarations (`int x;` doesn't exist), no primitives, `None` replaces `null`.

### 3. Operators
- **Arithmetic:** `+ - * / %` — `/` is always **float** division (`7 / 2 == 3.5`), `//` is floor division (`7 // 2 == 3`, careful with negatives: `-7 // 2 == -4`), `**` is power.
- **Comparison:** `==`, `!=`, `<`, `>`, `<=`, `>=` — can be chained: `0 <= x < 10`.
- **Logical:** `and`, `or`, `not` (words, not symbols). Short-circuit, and they **return an operand, not a bool**: `x or default` is the idiomatic fallback pattern.
- **Identity vs equality:** `is` compares object identity (same memory), `==` compares value. Use `is` only for `None` and singletons.
- **Membership:** `in` — works on strings, lists, dicts (keys), sets. **Walrus `:=`** assigns inside an expression (Python 3.8+).

### 4. Type Casting
- Explicit conversions: `int("42")`, `float("3.5")`, `str(99)`, `bool(0)` → `False`.
- **Falsy values:** `0`, `0.0`, `""`, `[]`, `{}`, `None`, `False` — everything else is truthy.
- `int("3.5")` raises `ValueError` (go through `float` first); `int("abc")` raises too.
- Division always floats; convert back with `int()`/`round()`.

### 5. Control Flow
- `if` / `elif` / `else` — conditions can be any object (truthiness applies).
- **Ternary is an expression:** `status = "pass" if score >= 60 else "fail"`.
- `match` statement (Python 3.10+) — structural pattern matching, not just a switch: `case {"cmd": "add", "x": x}:` destructures.
- No `switch` keyword — `match` is the replacement, and `dict` dispatch is the other idiom.

### 6. Loops
- `for x in iterable:` — Python's for is a **for-each** over any iterable; `range(5)` supplies numbers when needed.
- `while cond:` — same as anywhere, with `break` / `continue`.
- **`for...else`:** the `else` block runs only if the loop completed without `break` — the search-found-flag pattern.
- `enumerate(iterable)` gives `(index, item)`; `zip(a, b)` walks two iterables in lockstep.
- Comprehensions: `[x*x for x in range(10) if x % 2 == 0]` — loops as expressions.

### 7. Arrays (Lists)
- `list` is Python's growable array — no fixed size, mixed types allowed.
- **Everything is a reference:** `b = a` copies the *name*, not the list; `b = a[:]` or `a.copy()` makes a shallow copy.
- Core ops: `append`, `extend`, `insert`, `remove`, `pop()`, `sort()`, `sorted()`, `len`, `in`, `+`, `*`.
- **Slicing** `a[1:4]`, `a[::-1]` (reverse), `a[:n]`, `a[-1]` (last).
- **Copy traps:** `list.sort()` mutates in place and returns `None`; `==` on lists compares element-wise (unlike Java's reference compare).
- Tuples `(1, 2)` — immutable, unpackable: `x, y = point`.

### 8. Strings
- Immutable; every "modification" returns a new string (same idea as Java).
- f-strings: `f"Hello {name}, score={score:.1f}"` — the modern formatting tool (replaces `%` and `.format`).
- Useful methods: `split`, `join` ( `" ".join(words)` — the reverse of split), `strip`, `replace`, `startswith`, `find`, `upper`/`lower`, `isdigit`.
- **`in` for substrings:** `"ell" in "hello"` — no `.contains` method.
- Raw strings `r"\n"` for regex/paths; `*` repetition: `"ab" * 3`.

### 9. Functions
- `def name(args):` — first-class objects: assign, pass, return them.
- **Default arguments are evaluated once** — the mutable-default trap (`def f(x, acc=[])` shares one list across calls; use `acc=None` then `acc = [] or []`).
- Keyword args: `f(x=1, y=2)`; `*args` (tuple of extras), `**kwargs` (dict of keyword extras).
- `lambda x: x * 2` — one-expression anonymous functions for `key=` and callbacks.
- Type hints (optional but valuable): `def add(a: int, b: int) -> int:`.
- Docstrings: the first string in a function, shown by `help()`.

### 10. User Input
- `name = input("Name: ")` — **always returns a string**; convert with `int(...)` inside `try/except ValueError`.
- No Scanner newline-buffer trap like Java — `input` reads the whole line.
- `input()` blocks and reads stdin; scripts here avoid it so they run unattended.

### 11. Output Formatting
- `print` with `sep=` and `end=`: `print("a", "b", sep=", ")`.
- f-string format specifiers: `{x:.2f}` (2 decimals), `{x:>10}` (right-align), `{x:,}` (thousands), `{pct:.1%}` (percent).
- f-strings can hold expressions: `f"{total/count:.2f}"`.

---

# Module 02 — OOP and Modules

*Folder:* [`concepts/02-oop-and-modules`](./concepts/02-oop-and-modules) · ✅ Complete · **10 topics**

### 1. Classes & Objects
- `class Dog:` — no `public` keyword; `__init__(self, name)` is the constructor (self is explicit).
- Instance attributes live on the object (often set in `__init__`); class attributes are shared.
- `d = Dog("Rex")` — no `new` keyword; Python instantiates directly.

### 2. Encapsulation
- No `private` keyword — **convention:** `_name` means "internal, hands off", `__name` triggers name mangling (`_ClassName__name`) to avoid accidental access.
- `@property` turns a method into a read-only attribute: `d.name` calls `name()`; `@name.setter` adds validated assignment — the Pythonic getter/setter.
- Encapsulation here is about a clean API, not compiler-enforced privacy.

### 3. Inheritance
- `class Dog(Animal):` — call `super().__init__(...)` to run the parent constructor.
- `issubclass(Dog, Animal)` / `isinstance(d, Dog)`; **multiple inheritance is allowed**: `class A(B, C)` — MRO (Method Resolution Order) decides lookup order; `A.__mro__` shows it.
- Every class inherits from `object`.

### 4. Polymorphism & Duck Typing
- **Duck typing:** "if it quacks like a duck…" — no interface needed; any object with the right method works. Duck typing replaces Java interfaces.
- The file is deliberately interface-free: a `Dog`, `Robot`, and `Parrot` all "speak" because they each define `speak()`, with no shared parent.
- Contrast with Java: compile-time type checks are gone; errors surface at runtime — Python's flexibility and its cost.

### 5. Abstract Classes
- `abc.ABC` + `@abstractmethod`: a subclass must implement the abstract methods or instantiation fails (`TypeError`).
- The Python replacement for Java abstract classes — when you *do* want enforced structure.
- `@abstractmethod` can stack with `@property`, `@classmethod`, `@staticmethod`.

### 6. Dunder Methods
- `__init__` (constructor), `__str__`/`__repr__` (string forms — `repr` should be unambiguous, `str` readable), `__eq__`, `__hash__`, `__len__`, `__add__`, `__lt__` (enables sorting), `__getitem__` (indexing), `__iter__`/`__next__` (iteration), `__enter__`/`__exit__` (context managers), `__call__` (make instances callable).
- Dunder methods are how Python's syntax dispatches: `a + b` calls `a.__add__(b)`; `for x in obj` calls `__iter__`.
- This is operator overloading, Python-style — and it's everywhere in the standard library.

### 7. Dataclasses
- `@dataclass` writes `__init__`, `__repr__`, `__eq__` for you — the killer feature for record-like classes.
- `field(default_factory=list)` for mutable defaults (fixes the shared-list trap properly).
- `frozen=True` → immutable with `__hash__`; `@dataclass(frozen=True, slots=True)` for memory-efficient immutable records.
- Python 3.7+; the closest thing to Java records (Module 09 over there).

### 8. Decorators
- A decorator is a **function that takes a function and returns a function**; `@cache` above `def` means `f = cache(f)`.
- Built-ins you'll use daily: `@staticmethod`, `@classmethod` (first arg is the class — alternative constructors), `@property`, `functools.wraps` (preserves the wrapped function's name/docstring — always use it in custom decorators).
- Writing one: an outer function takes the target, defines an inner wrapper, returns it. Closures capture the arguments.
- Decorators stack bottom-up: closest to the function wraps first.

### 9. Modules & Packages
- A module = one `.py` file; a package = a directory with `__init__.py`.
- Imports: `import os`, `from pathlib import Path`, `from . import sibling` (relative), `from mypkg import mod`.
- `if __name__ == "__main__":` — the script-vs-module guard: the block runs only when the file is executed directly, not imported.
- `__name__`, `__file__`, `sys.path` (where imports look), `pip` and virtual environments (`python -m venv .venv`) for dependencies.

### 10. Iterators, Generators & Context Managers
- **Iterator protocol:** `__iter__` returns an object with `__next__`; `StopIteration` ends the loop.
- **Generators:** `def gen(): yield x` — a function that produces values lazily, one at a time, pausing between `yield`s. A generator is both iterable and an iterator.
- Generator expressions: `(x*x for x in range(10))` — like list comprehensions but lazy.
- **Context managers:** `with open(f) as fh:` guarantees cleanup (like try-with-resources); `contextlib.contextmanager` makes one from a generator (`yield` splits setup from teardown).

---

# Module 03 — File I/O and JSON

*Folder:* [`concepts/03-file-io-and-json`](./concepts/03-file-io-and-json) · ✅ Complete · **8 topics**

### 1. `open()` and the `with` Statement
- `with open(path, "r", encoding="utf-8") as f:` — the context manager **always closes** the file, even on exception. Never use bare `open` without `with`.
- Modes: `"r"` read, `"w"` truncate-write, `"a"` append, `"x"` create-exclusive, `"b"` binary, `"+"` read-write.
- Always pass `encoding="utf-8"` — the default is platform-dependent and a classic source of mojibake.

### 2. Reading & Writing Text
- Reading: `f.read()` (whole file), `f.readlines()`, or best — `for line in f:` (streams line by line, memory-friendly for big files).
- Writing: `f.write(s)` (no newline added — `print(s, file=f)` adds one), `f.writelines(list)`.
- The `with` block auto-flushes on exit; inside it, `f.flush()` forces the write out.

### 3. `pathlib`
- `Path` objects replace string paths: `Path("data") / "file.txt"` (the `/` operator joins).
- `p.exists()`, `p.is_file()`, `p.mkdir(parents=True, exist_ok=True)`, `p.read_text()`, `p.write_text()`, `p.iterdir()`, `p.glob("*.csv")`, `p.name`, `p.stem`, `p.suffix`, `p.parent`.
- `Path` is the modern answer to Java's `Path`/`Files` — one object, method-chained, cross-platform.

### 4. CSV Files
- `csv.reader` / `csv.writer` handle quoting and commas correctly — never `line.split(",")` for real data.
- `csv.DictReader` / `DictWriter` map rows to dicts: `row["name"]`.
- `newline=""` on `open()` is required on Windows for correct line endings — a classic gotcha.

### 5. JSON Handling
- `json.load(f)` (file → object), `json.loads(s)` (string → object), `json.dump(obj, f)`, `json.dumps(obj)` — dumps/load**s** = string.
- Types map naturally: dict ↔ object, list ↔ array, str, int/float, bool, None.
- **Gotchas:** JSON keys are always strings; tuples become lists; `json.dumps` fails on sets and datetimes unless you write a `default=` handler; duplicate keys silently keep the last.
- `indent=2` for readable output, `sort_keys=True` for stable diffs.

### 6. Exceptions & Custom Errors
- `try / except SpecificError as e / else / finally` — `else` runs when no exception occurred (unlike Java).
- Catch **specific** exceptions; `except Exception` is the blanket catch that hides bugs.
- Built-ins you'll raise yourself: `ValueError` (bad value), `TypeError` (wrong type), `KeyError`, `IndexError`, `FileNotFoundError`.
- Custom: `class InvalidGradeError(ValueError): pass` — cheap and self-documenting.
- `raise ... from e` preserves the cause (Java's exception chaining); exceptions are objects with `args` and a traceback.

### 7. `os`, `sys`, `shutil` & `subprocess`
- `os`: environment (`os.environ`), `os.getcwd`, `os.remove`, `os.listdir` (prefer `pathlib` for paths).
- `sys`: `sys.argv` (command-line args), `sys.exit(code)`, `sys.stdin/stdout/stderr`, `sys.path`.
- `shutil`: `copy`, `copytree`, `rmtree`, `move` — the high-level file operations.
- `subprocess.run(["ls", "-l"], capture_output=True, text=True)` — run external commands safely; **never `shell=True` with unsanitized input** (shell-injection risk).

### 8. Logging & argparse
- **Logging levels:** `DEBUG < INFO < WARNING < ERROR < CRITICAL`; `logging.basicConfig(level=..., format=...)` once at the top.
- `log = logging.getLogger(__name__)` — per-module loggers; use `%(levelname)s %(name)s %(message)s` format.
- Why not `print`: log levels, timestamps, streams (file vs stderr), and silencing per severity.
- **argparse:** `parser.add_argument("-n", "--count", type=int, default=1)`; `parser.parse_args()` → `args.count`; `--help` is generated free.
- The standard pattern for a CLI: `def main() -> int:` returning an exit code, guarded by `if __name__ == "__main__": sys.exit(main())`.

---

# Module 04 — Network Sockets

*Folder:* [`concepts/04-network-sockets`](./concepts/04-network-sockets) · ✅ Complete · **7 topics** · **loopback only — every socket binds or connects to 127.0.0.1**

### 1. TCP Echo Server & Client
- `socket.socket(AF_INET, SOCK_STREAM)`; server: `bind(("127.0.0.1", port))` → `listen()` → `accept()` → `recv()`/`sendall()`; client: `connect()` → `send()` → `recv()`.
- **TCP is a stream, not messages:** `recv(1024)` returns *whatever arrived*, not "one message" — framing is your job.
- `sendall` loops until all bytes are sent (plain `send` may send partially).
- The demo is a real echo round-trip: client sends, server echoes, both close cleanly.

### 2. UDP Sockets
- `SOCK_DGRAM` — no connect/listen/accept; `sendto((data, addr))` and `recvfrom()` return the sender's address.
- Fire-and-forget: no delivery guarantee, no order, no connection state — faster, simpler, lossy.
- Use when a lost packet is acceptable (games, metrics) or when you build reliability yourself (DNS, QUIC).

### 3. Threaded Server, Multiple Clients
- One client per connection blocks the accept loop — the fix: `threading.Thread(target=handle, args=(conn,)).start()` per client.
- Shared state needs a `threading.Lock` (same race-condition lesson as Java Module 05).
- This is exactly how simple production servers worked before `asyncio` and thread pools.

### 4. HTTP with stdlib & `requests`
- `http.server` serves files with a few lines; `http.client` / `urllib.request` fetch pages — the standard library's no-dependency options.
- `requests.get(url, timeout=5)` — the ergonomic third-party client: `.status_code`, `.json()`, `.headers`, sessions, params.
- Always set a **timeout** — a hung server otherwise blocks forever.
- A GET is just a TCP connection plus text: `GET /path HTTP/1.1\r\nHost: ...` — the module shows the raw protocol under the library.

### 5. Binary Protocols with `struct`
- `struct.pack(">H", 258)` → bytes in **network byte order** (big-endian): `b'\x01\x02'`.
- Formats: `>` big-endian, `H` uint16, `I` uint32, `s` bytes, `f`/`d` floats; `unpack` reverses it.
- Length-prefixed framing: send a uint16 length, then the payload — the classic fix for TCP's "where does my message end?" problem.
- `!` (network order) and `>` are the same; always be explicit about endianness.

### 6. Port Checking on Localhost
- A port scan is just a connect attempt: `socket.create_connection(("127.0.0.1", port), timeout=0.5)` — success means open, refused/timeout means closed.
- The ethical rule baked into the module: only ever probe **your own machine** — this is the seed of project-02's scanner and its safety checks.
- Connect scans vs SYN scans (which need raw sockets and privileges) — theory only here.

### 7. Socket Errors & Timeouts
- `ConnectionRefusedError` (nothing listening), `TimeoutError` (no answer in time), `ConnectionResetError` (peer died), `BrokenPipeError` (writing to a closed socket), `GAIerror` (DNS).
- `sock.settimeout(5)` makes any blocking call time out — without it, `recv` can hang forever.
- **Client-server versioning:** the client sends a 2-byte version; the server closes politely on a mismatch — a real-world handshake pattern.

---

# Module 05 — Data Science Core

*Folder:* [`concepts/05-data-science-core`](./concepts/05-data-science-core) · ✅ Complete · **9 topics** · run on NumPy 2 and pandas 3

### 1. NumPy Arrays
- `np.array([1, 2, 3])` — the ndarray: homogeneous, contiguous, fixed-type (dtype), the substrate of all numeric Python.
- vs lists: no per-element object overhead → 10-100x faster math, less memory.
- `zeros`, `ones`, `arange`, `linspace`, `dtype` (`int64`, `float64`, `bool`), `.shape`, `.size`, `.ndim`.
- Creating from ranges and reshaping: `arange(12).reshape(3, 4)`.

### 2. Indexing, Slicing, Broadcasting
- Indexing: `a[0]`, `a[1:4]`, 2-D `a[1, 2]`, `a[:, 0]` (whole first column), `a[1:3, :]`.
- **Views, not copies:** a slice shares memory with the original — mutate the slice, mutate the source. `a.copy()` when you need independence.
- Boolean masks: `a[a > 5]` — filter with a condition array; `np.where(cond, x, y)` is the ternary.
- **Broadcasting:** shapes align from the right; size-1 or missing dims stretch. `(3, 4) + (4,)` works; `(3, 4) + (3,)` fails. This is how a row vector adds to every row of a matrix without a loop.

### 3. Vectorization & Performance
- Replace Python loops with whole-array operations: `a * 2 + b` — C-speed, no interpreter per element.
- Measured in the repo: a loop-based sum vs `np.sum` — the array version is dramatically faster (the walkthrough prints both timings).
- `np.vectorize` is a convenience, **not** a speedup — it's still a Python loop inside.
- Rules of thumb: no `for` over array elements; use built-ins (`sum`, `mean`, `dot`); allocate with `zeros` instead of appending.

### 4. Linear Algebra
- `A @ B` (matrix multiply), `A.T` (transpose), `np.dot`, `A @ x` (matrix-vector).
- `np.linalg`: `solve(A, b)` (Ax = b), `inv(A)`, `det(A)`, `norm`, `eig` (eigenvalues/vectors), `lstsq` (least squares).
- The geometry that matters for ML: `w @ x` is the net input of a neuron; least squares is linear regression in closed form; eigenvectors point along the axes of a transformation.

### 5. Pandas Series & DataFrame
- `Series` = labeled 1-D column (index + values); `DataFrame` = table (dict of Series sharing an index).
- Construction: `pd.DataFrame({"name": [...], "score": [...]})`; inspection: `df.head()`, `df.info()`, `df.describe()`, `df.shape`, `df.columns`, `df.dtypes`.
- `df.set_index("name")` — meaningful row labels; `df.rename`, `df.drop(columns=...)`, `df.sort_values("score", ascending=False)`.

### 6. Selecting, Filtering, GroupBy
- Columns: `df["col"]` (Series), `df[["a", "b"]]` (DataFrame); rows by label: `df.loc[...]`; by position: `df.iloc[...]`; boolean: `df[df.score >= 60]`.
- Chained conditions need parentheses: `df[(df.a > 1) & (df.b < 5)]` — `and`/`or` don't work (they're ambiguous for arrays).
- **GroupBy = split-apply-combine:** `df.groupby("city")["score"].mean()`; `agg(["mean", "max"])`, `transform` (broadcast back per row), `value_counts`.
- `df.merge(other, on="id")` — SQL-style joins; `pivot_table` — spreadsheet-style reshaping.

### 7. Cleaning Missing Data
- Missing data is `NaN` (float) or `None`; `df.isna()`, `df.isna().sum()` (per column), `df.dropna()`, `df.fillna(value)`.
- Options per column: drop, fill with mean/median/mode, forward-fill (`ffill`) for time series, or a sentinel + flag column.
- **`NaN` poisons arithmetic:** `NaN + 1 == NaN`; `df.mean()` skips it (`skipna=True` default) — know which behavior you're getting.
- Duplicates: `df.duplicated()`, `df.drop_duplicates()`; type fixes: `pd.to_datetime`, `astype`.

### 8. Statistics Basics
- `np.mean`, `np.median`, `np.std` (population — pass `ddof=1` for sample), `np.var`, `np.percentile`, `np.min`/`max`, `np.corrcoef` (correlation matrix).
- **Mean vs median:** mean is dragged by outliers; median isn't — check both.
- **Correlation ≠ causation**, and `corr` only sees *linear* relationships (r close to 0 can still hide a pattern).
- Distributions: `np.random.default_rng(seed)` — the modern seeded RNG; `normal`, `uniform`, `randint`; histograms with `np.histogram`.

### 9. Gradient Descent by Hand
- The target: minimize `L(w, b) = mean((w*x + b - y)**2)` — the same MSE a linear regression minimizes.
- **The gradient:** `dL/dw = mean(2*(y_hat - y)*x)`, `dL/db = mean(2*(y_hat - y))` — the file derives these on screen, then codes them.
- The loop: `w -= lr * dL/dw; b -= lr * dL/db` — walk downhill on the loss surface; `lr` (learning rate) too big diverges, too small crawls.
- Convergence: the gradient → 0 at the minimum; the walkthrough compares the learned `(w, b)` against the closed-form least-squares answer — they match.
- This single file is the bridge to project-03's perceptron and to every neural network trained since.

---

# Project 01 — Java Ports

*Folder:* [`projects/project-01-java-ports`](./projects/project-01-java-ports) · ✅ Complete · **184 pytest tests passing**

Four Java-lab programs rebuilt in Python — the direct Java-to-Python translation exercise:
- **`grade_manager.py`** — the Module-01 capstone again: menu loop, list-of-lists (or dataclass) storage, input validation, formatted tables. Same behavior, a third of the code.
- **`calculator.py`** — expression parsing and evaluation with functions; exceptions replace Java's error returns.
- **`todo_app.py`** — CRUD over an in-memory list with persistence; functions and a dataclass replace a class hierarchy.
- **`bank_system.py`** — accounts, deposits, withdrawals with custom exceptions (`InsufficientFundsError`); the same domain as Java project-03, idiomatically ported.
- Each program has a matching walkthrough `.md` and a `test_*.py` — the tests *are* the definition of done.

**The porting lesson:** Java's classes become dataclasses; `switch` becomes `match` or dict-dispatch; checked exceptions become duck-typed `except`; and the code shrinks.

---

# Project 02 — Network Scanner

*Folder:* [`projects/project-02-network-scanner`](./projects/project-02-network-scanner) · ✅ Complete · **35 pytest tests passing**

A threaded TCP port scanner with banner grabbing — and a **hard safety boundary**.

### How it works
- Resolve the target, **check it before any packet is sent**: `ipaddress` verifies the address is loopback (`127.0.0.0/8`) or RFC 1918 private (`10/8`, `172.16/12`, `192.168/16`). Anything else is **REFUSED** — and there is no override flag, by design.
- Port spec parsing: `"80"`, `"22,80"`, `"1-1024"` → a list of ports.
- Scan: a thread pool of connect attempts with timeouts (`create_connection`, ~0.5 s), open ports collected, then optional banner grab (`recv` on the open socket).
- Clean CLI: `argparse` for target/ports/threads; refused targets exit with code 2 and a message.

### The tests prove the safety
- `is_allowed("127.0.0.1")` is True; `is_allowed("8.8.8.8")` is False — a public IP is refused before any connect.
- Port parsing edge cases (empty, reversed ranges, out of range) are all tested.
- **Ethics, engineered:** the refusal isn't a comment in the README, it's a tested code path. Scanning hosts you don't own or lack written permission to test is illegal — the tool cannot be pointed there.

---

# Project 03 — Perceptron From Scratch

*Folder:* [`projects/project-03-perceptron-from-scratch`](./projects/project-03-perceptron-from-scratch) · ✅ Complete · **12 pytest tests passing** · standard library only (no NumPy — a test enforces it)

### The model
A perceptron is the simplest artificial neuron:
- Net input: `z = w1*x1 + w2*x2 + ... + b` (a dot product plus bias).
- Step activation: `prediction = 1 if z >= 0 else 0`.
- Learning rule, per sample: `error = y - prediction`; `w_j += lr * error * x_j`; `b += lr * error`. Right predictions change nothing (`error = 0`).
- Geometry: `z = 0` is a straight line — the decision boundary. Mistakes nudge the line toward the misclassified point.
- **Perceptron convergence theorem:** if the classes are linearly separable, this rule reaches zero mistakes in finitely many updates. If not, it never settles.

### Measured results (seed 42, lr 0.1)
- **AND and OR: converge to 100% accuracy** — both are linearly separable.
- **A seeded separable dataset: 100% train accuracy and 100% held-out accuracy.**
- **XOR: does not converge in 1000 epochs** — measured and printed, not asserted. XOR is not linearly separable; a single straight line cannot separate its classes. This is the project's headline lesson: *the single-layer perceptron's hard limit, and the reason hidden layers (multilayer networks) exist.*

### Engineering details
- A private `random.Random(seed)` keeps runs reproducible and leaves the global RNG untouched; weights start small-random in `[-0.5, 0.5]`.
- `FitResult` (a dataclass) records `converged`, `epochs`, and `errors_per_epoch` — training is observable, not just "done".
- `_validate` checks shapes and labels with clear `ValueError`s; `max_epochs` prevents infinite loops on non-separable data.
- Known limits (stated in the README): linearly separable problems only; finds *some* separating line, not the maximum-margin one; binary 0/1 labels, no probabilities; pure-Python lists, slow at scale; results are for one seed.

---

## How to Study These Notes

1. **Predict** the output before running a snippet.
2. **Run** the matching file in the concept folder (`python3 _N_Name.py` — every one exits 0).
3. **Break** it on purpose and explain the traceback.
4. **Explain** the topic in plain English; if you can't, reread the section.
5. **Ship** — the repo's method: write, run, break, explain, ship.

*Consolidated from the completed files in this repository. Every claim here is checkable against the source files next to it.*
