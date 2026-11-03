# `_6_FileIoWithFstream.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`std::ofstream` and `std::ifstream` read and write files through the same stream interface as `std::cout` and `std::cin`. A stream is an RAII object: the destructor flushes and closes the file, even when an exception is thrown. You must check for errors yourself, because by default a failed open or read does not throw, it just sets state flags. This file shows text and binary I/O, line-by-line reading, error flags, and cleanup of a temporary directory.

## Full Line-by-Line Breakdown

### SECTION 1: WRITING AND READING TEXT
`write_lines` opens an `ofstream` (text mode, truncating), writes lines with `<<`, and returns `static_cast<bool>(out)`, which is true only if everything succeeded. `read_lines` opens an `ifstream`, throws if it did not open, and reads with `while (std::getline(in, line))`: the read IS the loop condition, so the loop stops exactly when a read fails. Four lines written (the third is empty) give 36 bytes on disk: the characters 10 + 11 + 0 + 11 = 32, plus 4 newline characters. An `std::ios::app` stream appends, and its destructor closes it with no `close()` call. `rdbuf()` into a `stringstream` slurps a whole file, and `operator>>` splits on whitespace (8 words).

Output from a real run:

```text
===== SECTION 1: WRITING AND READING TEXT =====
write_lines ok: true
read back 4 lines:
  [0] "first line"
  [1] "second line"
  [2] ""
  [3] "fourth line"
file size on disk: 36 bytes
lines after append: 5
whole-file read length: 50 characters
word count via operator>>: 8
```

### SECTION 2: BINARY VS TEXT
Text mode turns values into characters; binary mode (`std::ios::binary`) copies raw bytes with `write` / `read`. `Record` is `{int32_t id; double score;}`, which has 16 bytes on this machine because 4 bytes of padding are inserted before the double, so 3 records are 48 bytes. The number 1234567 takes 7 bytes as text and 4 as binary. TRAP: raw struct dumps depend on this machine's padding, byte order and type sizes; they are not a portable format, and you must never write structs containing pointers or `std::string` this way (you would save an address, not the data). Also, on Windows text mode translates `\n` to `\r\n`, so use binary for raw bytes.

Output from a real run:

```text
===== SECTION 2: BINARY VS TEXT =====
sizeof(Record) = 16 (includes padding), file size = 48 bytes
read back: (1, 91.5) (2, 78.25) (3, 100)
the number 1234567 takes 7 bytes as text and 4 bytes as binary
TRAP: binary files written this way are tied to this machine's byte order, padding and type sizes;
      they are not a portable file format. Never write structs that contain pointers or std::string.
TRAP: on Windows, text mode translates \n to \r\n; on Linux it makes no difference. Use std::ios::binary for raw bytes.
```

### SECTION 3: ERROR CHECKING
Opening a missing file sets `failbit`: `is_open()` and the stream's `bool` conversion are both false, with no exception. `read_lines` converts that into an exception. After a good read `good=true`, `eof=false`. Trying to read an `int` from the text `first` sets `failbit` and leaves `n` at 0. Asking for 10 bytes when 2 remain gives `gcount()=2` with `eof` and `fail` both set. TRAP: `while (!in.eof())` processes a bogus extra iteration because eof only becomes true after a read has already failed; test the read operation itself. Writing into a directory that does not exist fails (streams never create directories).

Output from a real run:

```text
===== SECTION 3: ERROR CHECKING =====
opening a missing file -> is_open: false, operator bool: false
read_lines threw: cannot open nope.txt
state after a good read: good=true eof=false fail=false
reading an int from text 'first': failbit set: true, n = 0
asked for 10 bytes with 2 left: gcount=2, eof=true, fail=true
TRAP: 'while (!in.eof()) { getline(in, s); use(s); }' processes a bogus last item; test the READ itself:
      'while (getline(in, s)) { use(s); }'.
writing into a missing directory -> opened: false (fstream never creates directories)
```

### SECTION 4: RAII AND EXCEPTIONS
When an exception is thrown after writing, the `ofstream` destructor still runs during stack unwinding, flushes and closes the file; the file contains the 27 bytes written before the failure. `stream.exceptions(std::ios::failbit)` opts in to exceptions (opening the missing file then throws `std::ios_base::failure`). TRAP: a destructor cannot report errors, so for data you cannot lose, call `flush()` or `close()` explicitly and check the stream. The `TempDir` object deletes the whole directory (5 files here) when `main` ends, using the non-throwing `error_code` overload because destructors must not throw.

Output from a real run:

```text
===== SECTION 4: RAII AND EXCEPTIONS =====
caught: something failed mid-write
ofstream destructor still flushed and closed it; file has 27 bytes
with exceptions(failbit) enabled, opening a missing file threw std::ios_base::failure
TRAP: the destructor closes the file but cannot report a failed flush; for data you cannot lose, call
      out.flush() or out.close() yourself and check the stream afterwards.
files in the temp directory before cleanup: 5
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `Files.readAllLines(path)`, `Files.writeString(path, text)`. | Write the loop yourself (`getline`), or `rdbuf()` into a `stringstream`. No one-line helper in the standard library. |
| `try (BufferedReader r = Files.newBufferedReader(p)) { ... }` | `std::ifstream in(p);` closing is automatic when `in` leaves scope (RAII, no try-with-resources). |
| `IOException` is checked and must be handled. | No exception by default; check `if (!in)` or enable `exceptions(...)`. |
| `FileInputStream` / `FileOutputStream` for bytes, `Reader` / `Writer` for chars with explicit charset. | Same stream type for both; `std::ios::binary` selects binary mode. No charset handling; bytes are bytes. |
| `DataOutputStream.writeInt` is big-endian and portable. | `write(reinterpret_cast<const char*>(&x), sizeof x)` is machine-dependent. |
| `Files.createTempDirectory`, `deleteOnExit`. | Build your own (here `TempDir` with `std::filesystem`). |

## Key Rules / Gotchas Recap
- Check every open and every read; the default is silent failure.
- Loop on the read (`while (getline(in, s))`), never on `eof()`.
- Streams close themselves (RAII); call `close()`/`flush()` and check when losing data matters.
- Use `std::ios::binary` for raw bytes; do not dump structs with pointers or `std::string`.
- Raw struct files are not portable (padding, endianness, sizes).
- Use `std::filesystem` for paths, temp dirs, sizes and cleanup; fstream does not create directories.
- Always test file code inside a temp directory you delete.

## Why This Structure Exists
Loading datasets, model weights, configuration and logs is the first step of nearly every AI pipeline, and parsers for files and file formats are a major attack surface in security work. Careful error checking and RAII cleanup are what keep such code robust against truncated, missing or malicious files.
