# `_2_ReferencesVsPointers.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A reference is an alias for an existing object: it must be bound when created, can never be null, and can never be re-bound to a different object. A pointer is a separate variable that can be null and can be reassigned. Use a reference when the object is required and fixed, and a pointer (or `std::optional`) when "nothing" is a valid answer or the target changes.

## Full Line-by-Line Breakdown

### SECTION 1: RULES OF A REFERENCE
`int& r = a;` makes `r` another name for `a`, so `r = 5` sets `a`. Taking `&r` gives the address of `a`, proving it is not a separate object. A reference must be initialised and there is no null reference (both illegal lines are commented out). A `const` reference may bind to a temporary and extends its life, which is why `const int& tmp = 3 + 4;` is safe.

Output from a real run:

```text
===== SECTION 1: RULES OF A REFERENCE =====
a = 5 after r = 5 (r is a, not a copy)
&r == &a: true (taking the address of a reference gives the target's address)
const int& bound to a temporary: 7
```

### SECTION 2: RESEATING (THE BIG DIFFERENCE)
A pointer can be re-pointed (`p = &b`). A reference cannot: the line `r = b;` does NOT make `r` refer to `b`; it copies `b`'s value (100) into `a`, the object `r` still aliases. Changing `b` afterwards leaves `a` at 100, proving `r` never moved. This is the most common beginner misunderstanding.

Output from a real run:

```text
===== SECTION 2: RESEATING (THE BIG DIFFERENCE) =====
pointer reseated: *p = 100
r = b copied the value: a = 100, still aliasing a: true
changing b to 7 leaves a = 100 (r never moved)
```

### SECTION 3: WHEN TO USE WHICH
`bump_ref(int&)` can assume a real object. `bump_ptr(int*)` must handle null (it does, so `bump_ptr(nullptr)` is harmless). `find_name` returns a pointer because "not found" is a normal outcome: `nullptr`. `std::optional<size_t>` is the modern way to say "maybe a value" without pointers; `value_or` supplies a default. Rule of thumb: reference = required, non-null, fixed; pointer = optional or reseatable.

Output from a real run:

```text
===== SECTION 3: WHEN TO USE WHICH =====
n = 2 (reference param: caller cannot pass 'nothing')
found: linus
grace: nullptr means not found
find_index("linus") = 1, find_index("x") = 999
Rule of thumb: reference = required, non-null, same object for life; pointer = optional or reseatable.
```

### SECTION 4: REFERENCES IN CONTAINERS
A `std::vector<int&>` does not compile because references are not assignable objects. `std::reference_wrapper<int>` is a copyable, reseatable wrapper that can live in a container. Modifying through it changes the originals (`u` and `v`), and assigning a new wrapper (`refs[0] = w`) reseats it to point at `w`.

Output from a real run:

```text
===== SECTION 4: REFERENCES IN CONTAINERS =====
u = 10, v = 20 (modified through reference_wrapper)
after reseat: u = 10, w = 4
```

### SECTION 5: DANGLING REFERENCE TRAP
Returning a reference to a local variable is the classic bug: the local dies when the function returns and the reference points at nothing (g++ warns). Described in the comment but never run. The fix is to return by value, which is safe and, thanks to copy elision, usually free.

Output from a real run:

```text
===== SECTION 5: DANGLING REFERENCE TRAP =====
returning by value is safe: 1
```

## Key Differences From Java
| Java | C++ |
|---|---|
| All object variables are reference-like, always re-assignable, may be `null` | A C++ reference is a permanent alias that cannot be null or reseated |
| `Object o = x; o = y;` re-points `o` | `T& r = x; r = y;` copies `y` into `x` |
| Parameter passing hides the distinction | `T&` (alias), `T*` (address, optional), `T` (copy) are three explicit choices |
| `Optional<T>` | `std::optional<T>`; or `T*` / `nullptr` for non-owning optional |
| Nothing to dangle: the GC keeps objects alive | A reference/pointer to a dead object is a dangling reference (undefined behaviour) |

## Key Rules / Gotchas Recap
- A reference must be initialised, cannot be null, and can never be reseated.
- `r = x` assigns through the reference; it does not rebind it.
- Use references for required parameters, pointers or `std::optional` for optional ones.
- Use `const T&` to avoid copies; a const reference may bind to a temporary.
- Never return a reference to a local variable.
- Need references in a container? Use `std::reference_wrapper` (or pointers).

## Why This Structure Exists
Choosing between reference and pointer communicates intent in an API: who may be null, who may change. Clear intent is what stops null-dereference bugs in production services and is also what code reviewers look for when auditing C++.
