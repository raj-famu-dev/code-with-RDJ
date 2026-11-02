# `_2_ReadingAndWritingText.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Python gives you several ways to read a text file (`read()`, `readline()`, `readlines()`, or looping over the file object) and to write one (`write()`, `writelines()`, `print(file=...)`). They differ in how much memory they use and in one crucial detail: **Python never adds or removes newline characters for you** when you read or write lines. Knowing which method to use, and where the `\n` goes, is the difference between clean data and subtly broken files.

## Full Line-by-Line Breakdown

All files are created in a temporary directory that is deleted at the end.

### SECTION 1: write() and the missing-newline trap
`f.write(text)` writes exactly the string you give it and returns the number of characters written (13 for `"roses are red"`). Two consecutive writes without `\n` glue together into `'roses are redviolets are blue'`. The fix is to put `\n` at the end of each line yourself.

```text
=== SECTION 1: write() and the missing-newline trap ===
write() returned: 13
content: 'roses are redviolets are blue'
fixed content: 'roses are red\nviolets are blue\npython is neat\n'

```

### SECTION 2: read(), readline(), readlines()
- `read()` returns the entire remaining content as one string; a second `read()` returns `''` because the file position is at the end (EOF).
- `seek(0)` moves back to the start.
- `readline()` returns one line **including its trailing `\n`**; at EOF it returns `''`.
- `read(5)` reads at most 5 characters.
- `readlines()` returns a list of all lines, each still ending in `\n`.

```text
=== SECTION 2: read(), readline(), readlines() ===
read(): 'roses are red\nviolets are blue\npython is neat\n'
read() again (at EOF): ''
readline(): 'roses are red\n'
readline(): 'violets are blue\n'
read(5): 'roses' <- 5 characters only
readlines(): ['roses are red\n', 'violets are blue\n', 'python is neat\n']

```

### SECTION 3: iterating a file (the idiomatic way)
A file object is itself an iterator over its lines, so `for line in f:` is the standard loop. It is **lazy**: only one line is held in memory at a time. `enumerate(f, start=1)` adds line numbers. The trap is that every `line` still contains `\n`; strip it with `line.rstrip("\n")` (or `.strip()` if you also want to drop spaces).

```text
=== SECTION 3: iterating a file (the idiomatic way) ===
1 'roses are red\n'
2 'violets are blue\n'
3 'python is neat\n'
TRAP: each line keeps its trailing '\n'. Use .rstrip('\n') or .strip():
['roses are red', 'violets are blue', 'python is neat']

```

### SECTION 4: writelines() adds NO newlines
Despite its name, `writelines()` does not add line endings; it just writes each string in the iterable back to back, so `["alpha","beta","gamma"]` becomes `alphabetagamma`. Either add `"\n"` to each item, or use `print(*lines, sep="\n", file=f)`, which writes a newline after every print.

```text
=== SECTION 4: writelines() adds NO newlines ===
writelines(no \n): 'alphabetagamma'
writelines(with \n): 'alpha\nbeta\ngamma\n'
print(file=f): 'alpha\nbeta\ngamma\n'

```

### SECTION 5: append mode
`"a"` keeps existing content and writes at the end. The trap shown here is opening with `"w"` by mistake, which silently wipes the file; the output shows the list collapsing to `['only this']`.

```text
=== SECTION 5: append mode ===
after append: ['alpha', 'beta', 'gamma', 'delta']
after accidental 'w': ['only this']

```

### SECTION 6: newline handling (\n vs \r\n)
Windows traditionally ends lines with `\r\n`, Unix with `\n`. In text mode Python uses *universal newlines*: on reading it converts `\r\n` (and lone `\r`) to `\n`, and on writing it converts `\n` to the OS default. The script writes raw bytes with `\r\n`, then reads them in three ways: text mode (converted to `\n`), binary mode (untouched) and `newline=""` (translation disabled, bytes kept as-is). `newline="\n"` on a writer forces Unix endings on every OS, which is useful for reproducible files. `str.splitlines()` understands all newline styles.

```text
=== SECTION 6: newline handling (\n vs \r\n) ===
text mode read: 'one\ntwo\nthree'
binary mode read: b'one\r\ntwo\r\nthree'
newline='' read: 'one\r\ntwo\r\nthree'
bytes written with newline='\n': b'a\nb\n'
splitlines(): ['x', 'y', 'z'] <- handles all newline styles

```

### SECTION 7: reading a big file safely
`read()` and `readlines()` load everything into memory; for large files that can exhaust RAM. Iterating line by line never holds more than one line. The script writes 1000 rows and counts them lazily.

```text
=== SECTION 7: reading a big file safely ===
counted lines lazily: 1000
read() / readlines() load EVERYTHING into memory; iteration does not.

temp dir removed: True
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Read all lines | `Files.readAllLines(path)` returns `List<String>` **without** line terminators | `f.readlines()` keeps the `\n` on every line |
| Stream lines lazily | `Files.lines(path)` (a `Stream`, must be closed) or `BufferedReader.readLine()` | `for line in f:` (plain iteration, lazy) |
| `readLine()` result | Strips the terminator; returns `null` at EOF | `readline()` keeps `\n`; returns `''` at EOF |
| Write a line | `writer.write(s); writer.newLine();` or `PrintWriter.println` | `f.write(s + "\n")` or `print(s, file=f)` |
| Write a whole string | `Files.writeString(p, s)` | `Path.write_text(s)` or `f.write(s)` |
| Append | `Files.write(p, bytes, StandardOpenOption.APPEND)` | mode `"a"` |
| Line separator | `System.lineSeparator()`, `newLine()` is platform-aware | Text mode translates `\n` to the platform ending automatically |

## Key Rules / Gotchas Recap

- `write()` and `writelines()` never add newlines; you do.
- Lines read from a file keep their `\n`; strip it before comparing or splitting.
- `read()` twice returns `''` the second time (the position is at EOF); use `seek(0)` to rewind.
- Iterate the file object instead of `readlines()` for big files.
- `"w"` truncates immediately; use `"a"` to add to a file.
- Use `newline=""` when you need exact bytes (CSV), and `newline="\n"` to force Unix endings when writing.

## Why This Structure Exists
Log files, datasets and text corpora are routinely larger than memory, so streaming line by line is an essential habit in data and AI work. The explicit newline behaviour keeps text files portable between operating systems, which matters when scripts run on both your laptop and a Linux server.
