# `_8_InputOutput.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
C++ uses stream objects for text input and output: `std::cout` writes, `std::istringstream` reads from a string, `std::ostringstream` builds a string. `<iomanip>` manipulators (`setw`, `setprecision`, `fixed`) control formatting, and some of them are "sticky" (they stay in effect) while others apply once. Reading a value from a stream never throws by default: it sets a failure flag you must check.

## Full Line-by-Line Breakdown

### SECTION 1: STREAMS AND cout vs cerr
`cout` is buffered standard output, `cerr` is unbuffered standard error for diagnostics. `'\n'` just writes a newline, while `std::endl` also flushes the buffer, which is slow inside loops. `std::boolalpha` prints `true` instead of `1`, and `std::noboolalpha` switches back, showing that manipulators change the stream's state.

Output from a real run:

```text
===== SECTION 1: STREAMS AND cout vs cerr =====
cout is buffered stdout; cerr is unbuffered stderr (not shown below).
A newline '\n' is cheap; std::endl also flushes, which is slow in loops.
true 1
```

### SECTION 2: FORMATTING WITH <iomanip>
`std::fixed` plus `std::setprecision(2)` prints exactly two decimals; both are sticky, so the next line stays at 5 places until the code resets them with `std::defaultfloat`. `std::hex`, `std::oct` and `std::dec` change the number base and `std::showbase` adds `0x`. The table uses `setw` for column width, `left`/`right` for alignment and `setfill('-')` for the rule. `setw` is NOT sticky: it affects only the next output item, which the last line proves.

Output from a real run:

```text
===== SECTION 2: FORMATTING WITH <iomanip> =====
default:          3.14159
fixed, 2 places:  3.14
fixed, 5 places:  3.14159 (setprecision and fixed are STICKY)
scientific:       1.234568e+04
hex/oct/dec of 255: ff 377 255
with showbase: 0xff
table:
item         price
------------------
coffee        3.50
bagel         2.25
juice        12.00
setw is NOT sticky: [   42][42]
```

### SECTION 3: PARSING WITH istringstream
`std::istringstream` turns a string into an input stream, so the same `>>` code that would read the keyboard (not used in this curriculum) reads text you already have. `while (csv >> name >> age >> score)` works because the stream converts to `false` when a read fails, which happens at the end of the data. After the loop, `eof` and `fail` are both true: the last attempted read hit the end.

Output from a real run:

```text
===== SECTION 3: PARSING WITH istringstream =====
parsed alice, age 30, score 4.5
parsed bob, age 25, score 3
parsed carol, age 41, score 5
total score = 12.5
stream at end: eof=true, fail=true
```

### SECTION 4: getline, SPLITTING AND BAD INPUT
`std::getline` reads a whole line, and `find('=')` plus `substr` splits it; a line without `=` is detected and skipped rather than crashing. The trap: parsing `"12abc"` as an int succeeds with 12 and leaves `abc` unread, and parsing `"abc"` sets the failure flag and stores 0. Streams do not throw, so always test the stream (or use `std::from_chars`/`std::stoi` when you need strict parsing).

Output from a real run:

```text
===== SECTION 4: getline, SPLITTING AND BAD INPUT =====
key=key value=value
key=name value=RDJ
skipping malformed line: "broken line"
key=lang value=C++
read '12abc' as int: n=12, leftover="abc"
read 'abc' as int: m=0, fail=true (m is set to 0 since C++11; always check the stream)
```

### SECTION 5: BUILDING TEXT WITH ostringstream
`std::ostringstream` accepts the same `<<` formatting as `cout` but collects the result in a string you get with `.str()`. Here it builds a zero-padded id and a bool.

Output from a real run:

```text
===== SECTION 5: BUILDING TEXT WITH ostringstream =====
id=0007;ok=true
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `System.out.println(x)` | `std::cout << x << '\n'` |
| `String.format("%.2f", x)` / `printf` | `std::fixed << std::setprecision(2) << x` (stateful) or `std::format` in C++20 libraries that support it |
| `Scanner` / `BufferedReader` | `std::cin`, `std::getline`, `std::istringstream` |
| `Integer.parseInt("abc")` throws `NumberFormatException` | `stream >> n` silently sets `failbit`; `std::stoi` throws |
| `StringBuilder` | `std::ostringstream` or `std::string` with `+=` |
| Formatting is per call | Many manipulators persist on the stream until you reset them |

## Key Rules / Gotchas Recap
- `'\n'` is cheap; `std::endl` flushes.
- `fixed`, `setprecision`, `hex`, `left` etc. are sticky; `setw` applies once.
- A failed `>>` does not throw: check the stream or its return value.
- `istringstream` lets you test parsing code without any keyboard or file.
- Reset formatting you changed, especially on shared streams like `std::cout`.

## Why This Structure Exists
Every tool that reads logs, configs or protocol text must parse untrusted input without crashing, which means checking failure states instead of assuming success. Controlled formatting is how you produce reproducible reports, benchmark tables and evaluation output in AI projects.
