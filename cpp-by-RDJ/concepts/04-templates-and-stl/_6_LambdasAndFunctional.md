# `_6_LambdasAndFunctional.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A lambda is an inline, unnamed function object: `[captures](params) { body }`. The compiler turns it into a small class whose `operator()` is the body and whose members are the captured variables. Captures decide whether the lambda holds copies or references to variables from the surrounding scope, and that choice is where nearly all lambda bugs come from.

`std::function` is a general wrapper that can store any callable with a given signature.

## Full Line-by-Line Breakdown

### SECTION 1: lambda syntax and capture by value / reference
`byValue` copied `factor` (3) when it was created, so after `factor = 10` it still multiplies by 3; `byRef` refers to the variable and sees 10. `[=]` and `[&]` capture everything used, by value or by reference. The `sizeof` line shows what a lambda is: with no captures it is a 1-byte empty object, with one int captured it is 4 bytes (these sizes are for this compiler/platform).

Output from a real run:

```text
===== SECTION 1: lambda syntax and capture by value / reference =====
after factor = 10: byValue(2) = 6 (still used 3), byRef(2) = 20 (sees 10)
addAll(1) = 11, addRef(1) = 11
sizeof captureless lambda is 1, lambda capturing one int is 4 (a lambda is an object holding its captures)
```

### SECTION 2: mutable and init-captures
Lambdas are `const` by default: a by-value capture cannot be changed unless you write `mutable`. `[n = start]` is an init-capture: it creates a new variable `n` inside the lambda, initialized from `start`. The counter prints 6, 7, 8 and leaves `start` at 5. Copying a lambda copies its captured state, so after `auto copy = counter` the copy and the original count independently (both print 9 on their next call, because each had state 8). Init-capture is also the way to move a move-only object (`unique_ptr`) into a lambda: afterward the original pointer is null.

Output from a real run:

```text
===== SECTION 2: mutable and init-captures =====
counter() x3: 6 7 8
outer `start` is untouched: 5 (mutable lets the lambda modify its OWN copy)
copy() = 9, counter() = 9 (they now diverge)
unique_ptr moved into a lambda: size = 8, original is null: true
```

### SECTION 3: std::function
A `std::function<int(int)>` can hold a lambda, a lambda with captures, a functor (a struct with `operator()`), or another `std::function`. The vector stores all four kinds and calls them the same way. Calling an empty `std::function` throws `std::bad_function_call`. The price: type erasure means an indirect call, and possibly a heap allocation for large captures. When you merely accept a callable as a parameter, prefer a template parameter `template <typename F>`, which keeps the exact lambda type and can be inlined.

Output from a real run:

```text
===== SECTION 3: std::function =====
ops[0](6) = 7
ops[1](6) = 24
ops[2](6) = 36
ops[3](6) = -6
calling an empty std::function throws bad_function_call
std::function stores ANY callable with that signature (type erasure) at a cost: possible heap allocation and an indirect call.
For parameters you only call, prefer a template parameter (template <typename F>) which can be inlined.
```

### SECTION 4: dangling-capture trap
`makeBrokenCounter` captures a local by reference and returns the lambda. The local is gone when the function returns, so calling the lambda reads a dead stack slot: undefined behaviour. This is hidden behind `--trap` (and would be flagged by sanitizers, so it was run WITHOUT them). One real run of `--trap` printed `makeBrokenCounter()() = 21860`, instead of the expected 42; the value is indeterminate and may differ on each run or compiler. `makeSafeCounter` captures by value and prints 42. Rule: a lambda that outlives its scope (returned, stored, sent to another thread) must capture by value or by move.

Output from a real run (default, without the flag):

```text
===== SECTION 4: dangling-capture trap =====
makeSafeCounter()() = 42 (captured by value: correct)
makeBrokenCounter() is not called by default: it captures a local by reference and returns the lambda.
Run with --trap to call it (value is indeterminate; never rely on it).
Rule: a lambda that outlives its creating scope (returned, stored, sent to a thread) must capture by value or by move.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Lambdas capture only effectively-final locals, always by value (the reference, not the object, is copied) | You choose per variable: `[x]` copy, `[&x]` reference, `[x = std::move(y)]` move |
| A captured local can never dangle (objects live on the garbage-collected heap) | A reference capture can outlive the variable: undefined behaviour |
| Functional interface (`Function<T,R>`, `Runnable`) is the lambda's type | Each lambda has its own unique anonymous type; `std::function<R(Args...)>` is the "interface" |
| `Comparator<T>` is an interface with generics (erased at run time) | `std::function`/template parameter, with the type kept at compile time; no erasure |
| Lambda objects are heap objects | A lambda is a stack value; captures live inside it |
| Closures keep objects alive through GC | Closures hold copies or references; nothing keeps a referenced local alive |

Related Java points for this topic:
- Collections: passing `list.forEach(x -> ...)` or `list.sort((a, b) -> ...)` in Java corresponds to passing a lambda to `std::for_each` or `std::sort`.
- equals/hashCode: a lambda has no `equals`/`hashCode` identity you can rely on; in C++ two lambdas, even with identical text, have different unrelated types and are not comparable.

## Key Rules / Gotchas Recap
- `[&]` is fine for lambdas used immediately (like `std::sort`); dangerous when stored or returned.
- By-value captures are `const` unless the lambda is `mutable`.
- Capturing `this` implicitly (`[=]` captures `this` pointer) can dangle too; copy the data you need.
- Move-only objects need init-captures.
- `std::function` has overhead; use it for storage, templates for parameters.
- Do not rely on values read through dangling references; there is no reliable symptom.

## Why This Structure Exists
Callbacks, comparators, thread tasks and pipeline stages are all lambdas in modern C++. Dangling captures are a real source of use-after-return and use-after-free bugs, including exploitable ones, so it is worth learning the lifetime rule now.
