# `_6_ErrorHandling.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
C++ has several error-handling styles and a good programmer knows when to use each. Exceptions (`throw` / `try` / `catch`) unwind the stack and run destructors, so RAII cleans up automatically. `noexcept` is a promise that a function will not throw, and breaking it terminates the program. Error codes and result types (like the tiny `Result<T, E>` built here, a stand-in for `std::expected`, which is C++23 and not available in g++ 13) make failure part of the return value. Exception safety guarantees describe what state your data is in after a failure.

## Full Line-by-Line Breakdown

### SECTION 1: EXCEPTIONS
`parse_percent_throwing` throws `std::invalid_argument` for bad input. `catch (const std::invalid_argument& e)` catches it; the first `parse` succeeds and the second fails, so the `not reached` line never prints. `vector::at()` is the bounds-checked accessor and throws `std::out_of_range` (the exact message text is implementation-specific, so it is not printed). A bare `throw;` rethrows the same exception object. TRAP: catch by `const&`; catching a derived exception by value (`catch (std::exception e)`) slices it and loses the derived part. Stack unwinding runs destructors: `risky_cleanup_demo` allocates a `Tracer` in a `unique_ptr`, throws, and `Tracer::alive` is 0 afterwards, so cleanup ran.

Output from a real run:

```text
===== SECTION 1: EXCEPTIONS =====
parse '42' -> 42
parse 'abc' -> caught invalid_argument: bad percent 'abc': NotANumber
vector::at threw std::out_of_range (message is implementation specific)
inner caught 'boom' and rethrows with a bare 'throw;'
outer caught runtime_error: boom
TRAP: catch by const reference. 'catch (std::exception e)' by value would slice a derived exception.
Stack unwinding runs destructors: Tracer::alive after unwinding = 0 (0 means the unique_ptr cleaned up)
```

### SECTION 2: noexcept
`noexcept(expr)` is a compile-time query that answers whether an expression can throw. A function marked `noexcept` can be optimized and lets containers use moves (see the move semantics file). TRAP: if an exception escapes a `noexcept` function, `std::terminate` is called. By default this is skipped. With `--terminate` the program really does that; the real run printed `terminate called after throwing an instance of 'std::runtime_error'  what():  boom` and exited with code 134 (SIGABRT). The throw goes through a function pointer so the compiler cannot warn about the obvious bug at build time.

Output from a real run:

```text
===== SECTION 2: noexcept =====
noexcept(promise_not_to_throw()) = true
noexcept(might_throw())          = false
is_nothrow_move_constructible<std::string> = true
TRAP: if a noexcept function lets an exception escape, std::terminate is called (the program aborts).
(skipped; run with --terminate to watch std::terminate happen, exit code is 134)
```

### SECTION 3: ERROR CODES AND Result<T,E>
The C-style version returns a `bool` and an out-parameter: the caller can ignore the `false` and keep using stale `out` (it still holds 55). `Result<int, ParseError>` wraps a `std::variant<T, E>`: it holds either the value or an error enum, and `ok()` / `fail()` build it. A caller has to look inside it to get the value, so failure is hard to ignore. The four loop lines show success and all three error kinds. Rule of thumb: exceptions for rare, truly exceptional failures; results or codes for expected failures (user input) or where exceptions are disabled (kernels, many embedded and game codebases).

Output from a real run:

```text
===== SECTION 3: ERROR CODES AND Result<T,E> =====
error-code style: parse_percent_code("55", out) -> true, out=55
error-code style: parse_percent_code("", out)   -> false, out stays 55 (caller can forget to check the bool)
Result "75" -> ok 75
Result "" -> error Empty
Result "12x" -> error NotANumber
Result "250" -> error OutOfRange
value_or: -1
Use exceptions for rare, truly exceptional failures; use Result/codes where failure is routine (parsing user input) or exceptions are banned (kernels, embedded, hot loops).
```

### SECTION 4: EXCEPTION SAFETY GUARANTEES
Exception safety levels describe the state after something throws. NO-THROW: `swap_nothrow` can never fail. BASIC: `append_basic` adds items one by one and the third throws; nothing leaks and `dst` is valid, but it changed (now 3 elements). STRONG: `append_strong` works on a temporary copy and only swaps it in at the end (the commit step is `noexcept`), so after the same failure `dst` is exactly what it was (2 elements). Strong costs an extra copy, so use it where rollback matters. Destructors are implicitly `noexcept`; throwing from one during unwinding terminates the program.

Output from a real run:

```text
===== SECTION 4: EXCEPTION SAFETY GUARANTEES =====
basic guarantee:  dst was {a,b}; after the failed append it has 3 elements (the 'c' stayed: changed, but valid)
strong guarantee: dst was {a,b}; after the failed append it has 2 elements (rolled back, as if nothing happened)
nothrow guarantee: swap_nothrow(1,2) -> 2,1 (never throws, so it can be the commit step)
Levels: no-throw > strong (all or nothing) > basic (valid, no leaks) > none (leaks/corruption).
Destructors are implicitly noexcept: never throw from one.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| Checked and unchecked exceptions; `throws` clauses. | No checked exceptions. `noexcept` is the only exception specification left. |
| `catch (Exception e)` catches by reference automatically. | Catch by `const&`; by value slices. |
| `finally` and try-with-resources for cleanup. | RAII: destructors run during unwinding, so no `finally` is needed. |
| Throwing is a common, ordinary way to report errors. | Exceptions are often avoided in hot paths and some codebases; `std::optional` / `Result` / error codes are common. |
| `Optional` or a custom class for result types. | `std::expected` (C++23, not in g++ 13) or a small `Result` like this one. |
| Any `Throwable` including `Error` can be caught. | You can throw any type, but throw `std::exception` subclasses by convention. |
| An uncaught exception ends the thread with a stack trace. | An uncaught exception or a `noexcept` violation calls `std::terminate` (abort). |

## Key Rules / Gotchas Recap
- Throw by value, catch by `const&`, rethrow with bare `throw;`.
- Use RAII (smart pointers, containers, lock guards) so unwinding cleans up for you.
- Mark functions `noexcept` only if they truly cannot throw; violating it terminates.
- Never throw from a destructor.
- Basic guarantee: valid and leak-free. Strong: all-or-nothing. No-throw: cannot fail.
- Copy-then-swap is the standard way to get the strong guarantee.
- `at()` throws; `operator[]` does not check.
- Do not use `std::expected` here: it is C++23 and not in g++ 13; the tiny `Result` is a teaching version.

## Why This Structure Exists
Parsers and network code deal with bad input constantly, so choosing between exceptions and result types is a daily design decision. Exception safety and `noexcept` also decide whether your containers move or copy and whether a failure leaves data half-updated, which matters in both performance work and security (partial updates are bug and vulnerability fodder).
