# `_8_Chrono_Random_Filesystem.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`std::chrono` represents time as typed durations (`90min`, `30s`) and clocks, so unit mix-ups become compile errors instead of bugs. `std::mt19937` is the standard Mersenne Twister random engine; with a fixed seed it produces the same sequence every run, which makes experiments and tests reproducible. `std::filesystem` gives portable path and directory operations. The demo does all its file work inside a temporary directory that a RAII class deletes at the end.

## Full Line-by-Line Breakdown

### SECTION 1: chrono DURATIONS
Literals such as `90min` and `30s` (from `std::chrono_literals`) are `std::chrono::duration` objects. Adding them gives the common type, seconds: 5430. `duration_cast<minutes>` converts but truncates toward zero (90 here). A `duration<double, ratio<3600>>` converts implicitly to fractional hours (1.5083). TRAP: `duration_cast<seconds>(1500ms)` is 1, not 1.5; integer durations truncate. A duration is just an integer inside (8 bytes for nanoseconds), but the type tracks the unit.

Output from a real run:

```text
===== SECTION 1: chrono DURATIONS =====
90min + 30s = 5430 seconds
as minutes (duration_cast truncates): 90
as fractional hours: 1.5083
1500ms in seconds (int, truncated): 1
TRAP: duration_cast<seconds>(1500ms) is 1, not 1.5; integer durations truncate toward zero.
2h == 120min? true
sizeof(std::chrono::nanoseconds) = 8 bytes (just an integer)
```

### SECTION 2: CLOCKS (MEASUREMENT)
`steady_clock` is monotonic, so it is the clock for timing code; `system_clock` is wall-clock time that can jump (NTP, manual changes). The program times a loop but prints ONLY a deterministic result (`acc`) and a boolean about the measurement, because real timings change every run; it does not claim any speed. The `epoch` line shows a default-constructed `system_clock::time_point` is the Unix epoch (0 seconds).

Output from a real run:

```text
===== SECTION 2: CLOCKS (MEASUREMENT) =====
loop result (deterministic): 333332833333500000
MEASUREMENT (varies every run, do not rely on it): elapsed >= 0 us? true
Use steady_clock to time code (never goes backwards); system_clock is wall time and can jump.
steady_clock is_steady=true, system_clock is_steady=false
default system_clock time_point is the epoch: seconds since epoch = 0
```

### SECTION 3: mt19937 WITH A FIXED SEED
A `std::mt19937` seeded with 42 produces the same raw sequence on every run and on every conforming platform (its first output for seed 42 is 1608637542). Re-seeding restarts the sequence. `uniform_int_distribution` turns raw bits into dice rolls. TRAP: `std::random_device` gives a different seed each time, so use it only to choose a seed that you then print or log. TRAP: the engine's raw output is specified exactly by the standard, but distribution classes and `std::shuffle` are NOT; other standard libraries may give different dice rolls or shuffles for the same seed. The shuffle line is labelled as libstdc++-specific for that reason. `mt19937` is not cryptographically secure.

Output from a real run:

```text
===== SECTION 3: mt19937 WITH A FIXED SEED =====
first 5 raw outputs (seed 42): 1608637542 3421126067 4083286876 787846414 3143890026
after re-seeding with 42, first output again: 1608637542
ten dice rolls (seed 2024): 4 5 5 5 2 4 1 6 2 6
shuffle with seed 7 (std::shuffle order is implementation-specific, so this is libstdc++ only): 3 8 7 5 2 6 4 1
TRAP: std::random_device gives a different seed each run, so output is not reproducible; use it only to pick a seed you then log.
TRAP: mt19937 raw values are fixed by the standard, but distributions (uniform_int_distribution) are NOT guaranteed identical across compilers.
mt19937 is NOT cryptographically secure; never use it for passwords or keys.
```

### SECTION 4: filesystem IN A TEMP DIRECTORY
`TempDir` creates `<system temp>/cpp_by_rdj_chrono_demo` and removes it in its destructor (using the `error_code` overload because destructors must not throw). Inside, the program creates directories with `create_directories`, writes files, reads sizes with `file_size`, walks everything with `recursive_directory_iterator` (sorted before printing because directory order is unspecified), renames a file, and splits a path into `filename`, `stem`, `extension` and `parent_path`. Every filesystem function has a throwing form and an `error_code` form; the demo shows both on a missing file (the error-code form returns `-1` as `uintmax_t`, 18446744073709551615, with the error set). The last line proves the directory was deleted when the object went out of scope.

Output from a real run:

```text
===== SECTION 4: filesystem IN A TEMP DIRECTORY =====
temp dir exists: true
notes.txt size: 17 bytes
is_directory(logs): true, is_regular_file(notes.txt): true
recursive listing (sorted):
  logs/
  logs/2024/
  logs/2024/b.log
  logs/a.log
  notes.txt
after rename: notes.txt exists=false, renamed.txt exists=true
path parts: filename=file.tar.gz stem=file.tar extension=.gz parent=dir/sub
error_code overload on a missing file: failed=true, returned 18446744073709551615 (no exception thrown)
throwing overload raised std::filesystem::filesystem_error
after the TempDir went out of scope, directory still exists? false
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `Duration.ofMinutes(90)`, `Instant`, `System.nanoTime()` | `90min`, `steady_clock::now()`; units are part of the type, conversions are explicit when lossy. |
| `Duration` arithmetic always uses `long` seconds plus nanos. | `duration<Rep, Period>` is templated; integer-to-integer conversions truncate and need `duration_cast`. |
| `new Random(42)` (LCG; same seed same sequence across all JVMs). | `std::mt19937 rng(42)` plus a separate distribution; raw output portable, distributions not. |
| `SecureRandom` for security. | `std::random_device` is only an entropy hint; use OS crypto APIs or a vetted library for keys. |
| `java.nio.file.Path`, `Files.walk`, `Files.createTempDirectory`, `Files.delete`. | `std::filesystem::path`, `recursive_directory_iterator`, manual temp dir with RAII cleanup (no standard "create unique temp dir" function). |
| `try (Stream<Path> s = Files.walk(p))` | Iterators are plain objects; no stream to close. |

## Key Rules / Gotchas Recap
- Keep units in the type: `std::chrono::seconds`, not a bare `int`.
- `duration_cast` truncates; use floating-point durations when you need fractions.
- Time code with `steady_clock`; never print timings as if they were facts.
- Fixed-seed `mt19937` for reproducible tests; log the seed if you used `random_device`.
- Do not use `mt19937` for secrets.
- `std::filesystem` throws `filesystem_error` unless you pass an `std::error_code`.
- Directory iteration order is unspecified; sort when you need stable output.
- Always clean up temp files (RAII), and never run tests against real data directories.

## Why This Structure Exists
Reproducible random seeds are essential for ML experiments and tests, correct time units and clocks matter in benchmarks and timeouts, and filesystem code is the backbone of data loaders and tooling. Doing it inside a self-cleaning temp directory is the habit you want when writing tests or tools that touch the disk.
