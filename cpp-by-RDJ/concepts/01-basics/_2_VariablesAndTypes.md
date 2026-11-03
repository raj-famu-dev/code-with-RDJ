# `_2_VariablesAndTypes.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
C++ gives you precise control over how many bits a number uses, and in exchange it trusts you not to break the rules. Plain `int` has an implementation-defined size, so use the fixed-width types from `<cstdint>` when size matters. The most important rule: unsigned overflow wraps around (defined), but signed overflow is undefined behaviour (the compiler may assume it never happens).

Braces `{}` give you safe initialisation that refuses narrowing conversions, `auto` lets the compiler deduce a type, and `constexpr` moves computation to compile time.

## Full Line-by-Line Breakdown

### SECTION 1: FIXED-WIDTH INTEGERS AND sizeof
`int8_t`, `uint8_t`, `int32_t`, `uint64_t` have exactly the stated number of bits. `sizeof(x)` gives the size in bytes of a type or object at compile time. The 8-bit types are `char` types underneath, so printing them directly would show a character; the code casts to `int` first. Sizes of plain `int`, `long` and pointers are what this platform does (4, 8 and 8 bytes here), not what the language promises. Digit separators (`2'000'000'000`) make literals readable.

Output from a real run:

```text
===== SECTION 1: FIXED-WIDTH INTEGERS AND sizeof =====
int8_t  100 (sizeof 1)
uint8_t 200 (sizeof 1)
int32_t -2000000000 (sizeof 4)
uint64_t 18446744073709551615 (sizeof 8)
plain int sizeof = 4, long = 8, long long = 8, pointer = 8 (platform-specific)
int max = 2147483647
```

### SECTION 2: OVERFLOW: SIGNED vs UNSIGNED
`uint8_t` 250 plus 10 gives 4 because unsigned arithmetic is modulo 2^N: that is defined and portable. Signed overflow (`INT_MAX + 1`) is undefined behaviour, so the code never executes it: it checks first and widens to `int64_t`. The trap at the end: when a signed and an unsigned value meet in a comparison, the signed one is converted to unsigned, so `-1` becomes 4294967295 and `-1 < 1u` is false.

Output from a real run:

```text
===== SECTION 2: OVERFLOW: SIGNED vs UNSIGNED =====
uint8_t 250 + 10 wraps to 4 (defined behaviour)
uint32_t 0 - 1 = 4294967295 (wraps to max)
int max + 1 would overflow: true (so we do not compute it)
widen to int64_t first: 2147483648
Trap: (-1 < 1u) is true when both are int, but (-1 < 1u) as written is false because -1 converts to 4294967295
```

### SECTION 3: auto, const, constexpr
`auto` deduces from the initialiser: `42` is `int`, `3.5` is `double`, but `"text"` is a `const char*`, not a `std::string` (a common surprise; the `sizeof` line proves a string object is larger than a pointer). `const` means "cannot change after initialisation" and may be set at run time; `constexpr` means "must be computable at compile time", so it can size an array and be checked with `static_assert`, with zero run-time cost.

Output from a real run:

```text
===== SECTION 3: auto, const, constexpr =====
auto i=42 f=3.5 s=hi lit=text
sizeof(s)=bigger than sizeof(lit) (a string object is not a pointer)
const 84, constexpr 49, array length from constexpr 5
```

### SECTION 4: INITIALIZATION FORMS AND NARROWING
There are four spellings of the same thing: `= 5`, `(5)`, `{5}`, `= {5}`. `{}` with nothing inside value-initialises to zero. Assigning `3.99` to an `int` with `=` compiles silently and truncates to 3; the same with braces is a compile error (the commented line), which forces you to write the explicit `static_cast`. Always initialise locals: reading an uninitialised `int` is undefined behaviour.

Output from a real run:

```text
===== SECTION 4: INITIALIZATION FORMS AND NARROWING =====
5 5 5 5 0
int truncated = 3.99 gives 3 (silent narrowing)
int fixed{static_cast<int>(pi)} gives 3 (explicit and visible)
value-initialised local: 0
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `int` is always 32 bits, `long` 64 | `int` is at least 16 bits and usually 32; use `int32_t`/`int64_t` for certainty |
| Overflow wraps for all integers (defined) | Unsigned wraps; signed overflow is undefined behaviour |
| No unsigned types (except via helper methods) | `unsigned` and `uint8_t` etc. are first class, and mixing them with signed is a bug source |
| `var x = 42;` (Java 10+, local only) | `auto x = 42;` works almost everywhere |
| `final int x` | `const int x` / `constexpr int x` |
| Local variables must be assigned before use (compiler enforces) | Locals are NOT zeroed; reading before assigning is undefined behaviour |
| `int x = 3.99;` is a compile error | Compiles and truncates, unless you use `int x{3.99};` which is an error |

## Key Rules / Gotchas Recap
- Use `<cstdint>` types (`std::int32_t`, `std::uint8_t`) when the width matters.
- Signed overflow is undefined behaviour; unsigned overflow wraps. Check before arithmetic or widen the type.
- Never compare signed with unsigned (`-1 < 1u` is false); the signed value converts to unsigned.
- Prefer `{}` initialisation: it rejects narrowing and `{}` alone zero-initialises.
- `auto x = "text"` is `const char*`, not `std::string`.
- `const` = cannot change; `constexpr` = known at compile time (can size arrays, used in `static_assert`).
- Always initialise locals.

## Why This Structure Exists
Binary file formats, network protocols, tensors and cryptography all depend on exact integer widths and defined overflow behaviour. Many real vulnerabilities (integer overflow leading to a too-small allocation) start with exactly the signed/unsigned mistakes shown here, and numerical code in AI libraries uses fixed-width types and `constexpr` tables for speed.
