# `_4_ConstexprAndCompileTime.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`constexpr` marks functions and variables that the compiler may evaluate at compile time, so the answer is baked into the executable. `consteval` forces compile-time evaluation, and `static_assert` makes the compiler check a condition and refuse to build when it fails. You can build whole lookup tables (squares, primes, a CRC checksum table) at compile time, which means zero start-up cost and bugs caught before the program ever runs.

## Full Line-by-Line Breakdown

### SECTION 1: constexpr AT COMPILE TIME AND RUN TIME
`factorial` is a normal-looking function marked `constexpr`. Assigning its result to a `constexpr` variable forces the compiler to compute `factorial(10)` during compilation. Calling it with `runtime_n` (an ordinary non-constant variable) runs the very same function at run time. One function, two modes: that is the key idea of `constexpr`. `is_prime` is also `constexpr`; `91 = 7 * 13` is not prime.

Output from a real run:

```text
===== SECTION 1: constexpr AT COMPILE TIME AND RUN TIME =====
factorial(10) computed at compile time = 3628800
factorial(12) computed at run time = 479001600
is_prime(97)=true is_prime(91)=false (91 = 7 * 13)
```

### SECTION 2: consteval
`consteval` functions (an "immediate function") MUST be evaluated at compile time. `square_ct(12)` is fine because 12 is a constant. Calling `square_ct(runtime_n)` with a run-time value is a compile error (the file text says so; this was verified by compiling a tiny test that failed with "the value of 'n' is not usable in a constant expression"). Use `consteval` when a run-time call would be a bug.

Output from a real run:

```text
===== SECTION 2: consteval =====
square_ct(12) = 144
square_ct(runtime_n) would be a COMPILE ERROR: consteval functions only accept constants.
```

### SECTION 3: static_assert
The `static_assert` lines at the top of the file are checked while compiling. They assert `5! = 120`, a primality fact, a table entry, the size of `uint32_t`, the count of primes below 50, and the standard CRC-8 check value. If any were false the build would stop. The program then prints a few platform facts with `sizeof`; `static_assert` is the tool that lets you pin down assumptions like "int is 4 bytes" instead of hoping.

Output from a real run:

```text
===== SECTION 3: static_assert =====
Six static_asserts at the top of the file already passed before main() could run.
TRAP: change a table entry or the CRC polynomial and the BUILD fails, not the program.
sizeof(int)=4 sizeof(long)=8 sizeof(void*)=8 (platform facts; static_assert is how you pin assumptions)
```

### SECTION 4: COMPILE-TIME TABLES
`make_squares()` fills a `std::array` inside a `constexpr` function and is stored in the constexpr variable `kSquares`. `make_primes<50>()` first counts primes with `count_primes`, which becomes the array size (a constexpr value used as a template argument), then fills it, giving the 15 primes below 50. `make_crc_table()` builds the 256-entry CRC-8 table for polynomial 0x07 once at compile time, and `crc8("123456789")` returns the well-known check value 0xF4 (this is checked by a `static_assert` too, so the table cannot be wrong without breaking the build). The printed CRC of `"RDJ"` is just the function's output for that input.

Output from a real run:

```text
===== SECTION 4: COMPILE-TIME TABLES =====
squares: 0 1 4 9 16 25 36 49 64 81
primes < 50 (15): 2 3 5 7 11 13 17 19 23 29 31 37 41 43 47
CRC table entries 0..7: 0 7 14 9 28 27 18 21
crc8("123456789") = 0xf4  (standard CRC-8 check value is 0xF4)
crc8("RDJ") = 12
The tables live in the executable's read-only data; no loop ran at start-up to build them.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `static final int N = 10;` constants are folded by the compiler, but methods cannot run at compile time. | `constexpr` functions run at compile time: loops, conditionals, local variables, arrays. |
| Lookup tables are built in a `static { ... }` block when the class loads (run time). | The table is computed by the compiler and stored in read-only memory; nothing runs at start-up. |
| `assert` is disabled by default at run time. | `static_assert` is checked at compile time, always, and costs nothing at run time. |
| Generics are erased; no value-level template parameters. | Templates take values (`make_primes<50>()`), and constexpr results can be array sizes. |
| No equivalent of `consteval`. | `consteval` guarantees compile-time-only evaluation. |

## Key Rules / Gotchas Recap
- `constexpr` means "can" run at compile time; it only runs at compile time when used in a constant expression (constexpr variable, array size, template argument, `static_assert`).
- `consteval` means "must"; a non-constant argument is a compile error.
- Undefined behaviour is not allowed in constant evaluation, so the compiler rejects it (a free bug check).
- `static_assert` needs a constant expression; its message is shown if it fails.
- Big compile-time tables increase compile time; use them where they pay off.
- Compile-time functions need all their called functions to be `constexpr` too.

## Why This Structure Exists
Precomputed tables (CRC, hash seeds, lookup tables for quantization or decoding) and compile-time checks of sizes and layouts are standard in performance-critical and embedded code. Security-sensitive code uses `static_assert` to lock down struct sizes and assumptions about types so a refactor cannot silently break them.
