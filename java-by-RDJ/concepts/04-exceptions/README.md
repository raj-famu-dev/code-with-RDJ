# 04 · Exceptions

**Priority: NOW.** Project 03 (bank system) cannot be built properly without this.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

## Planned files

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_ExceptionHandlingBasics` | try / catch / finally, multi-catch, `throw` basics. **`.java` is your own code; the `.md` was drafted by Claude** | 📘 |
| 2 | `_2_CheckedVsUnchecked` | What does the compiler force on you, and why was the line drawn there? | 📘 |
| 3 | `_3_ThrowAndThrows` | Declaring vs triggering; how an exception travels up the call stack | 📘 |
| 4 | `_4_CustomExceptions` | When to extend `Exception` vs `RuntimeException`; adding fields like an error code | 📘 |
| 5 | `_5_TryWithResources` | `AutoCloseable`, close order, suppressed exceptions | 📘 |
| 6 | `_6_ExceptionChaining` | Wrapping with a cause, `getCause()`, why dropping the cause loses the real bug | 📘 |
| 7 | `_7_FinallyGotchas` | What happens if `finally` contains a `return`, or itself throws? | 📘 |
| 8 | `_8_ExceptionsCapstone` | Validated input pipeline with a custom exception hierarchy | 📘 |

## Traps to hit on purpose
- Empty `catch` block that hides a bug
- Catching `Exception` or `Throwable` when a specific type is meant
- `return` inside `finally` swallowing an exception
- Rethrowing a new exception without the original cause
- Catch order: general type above specific type (compile error, see why)

## Exit test (answer from memory)
1. Checked vs unchecked: give two examples of each and defend the design choice for your own custom exception.
2. What is printed, and why, for a method with `try { return 1; } finally { System.out.println("x"); }`?
3. When should a method catch an exception, and when should it let it propagate?

📘 = reference file and walkthrough committed (compiled and run). Do not mark a row ✅ until you have retyped the file, broken it on purpose, and rewritten its `.md` in your own words.
