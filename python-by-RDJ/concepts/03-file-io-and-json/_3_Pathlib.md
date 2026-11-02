# `_3_Pathlib.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`pathlib.Path` represents a file-system location as an object instead of a plain string, so you build, inspect, create, search and read paths with methods and the `/` operator rather than string concatenation. It works across Windows, macOS and Linux without you caring about `\` vs `/`. It is the modern replacement for most of `os.path` and is the closest thing Python has to Java's `java.nio.file.Path` plus parts of `Files`.

## Full Line-by-Line Breakdown

Everything happens inside a temporary directory, deleted at the end. A few lines print values that differ by operating system (for instance `PosixPath` vs `WindowsPath`); the sections say so.

### SECTION 1: building paths with / and joinpath
`base / "project" / "config" / "app.json"` uses the overloaded `/` operator to join parts; `base.joinpath("project", "config", "app.json")` does the same with a method. `relative_to(base)` strips a prefix. The **trap**: if the right-hand side is an absolute path, it silently replaces everything on the left (`PurePosixPath("/a/b") / "/etc"` is just `/etc`). This matters when joining a user-supplied filename to a base directory.

```text
=== SECTION 1: building paths with / and joinpath ===
/ operator == joinpath(): True
relative path: project/config/app.json
type: PosixPath (PosixPath on Linux/macOS, WindowsPath on Windows)
base / '/etc' -> /etc <- left side discarded!

```

### SECTION 2: path anatomy
`PurePosixPath` and `PureWindowsPath` do path arithmetic with no disk access, which makes them ideal for demonstrations. `.name` is the final component, `.stem` is the name without the last suffix, `.suffix` is the last extension, `.suffixes` lists all of them (`.2024`, `.log`, `.gz`), `.parent` is the containing directory and `.parts` is a tuple of components. `.with_suffix()` and `.with_name()` return new paths; paths are immutable.

```text
=== SECTION 2: path anatomy ===
name  : server.2024.log.gz
stem  : server.2024.log
suffix: .gz
suffixes: ['.2024', '.log', '.gz']
parent: /data/logs
parts : ('/', 'data', 'logs', 'server.2024.log.gz')
with_suffix('.txt'): /data/logs/server.2024.log.txt
with_name('x.bin') : /data/logs/x.bin
Windows flavour    : C:\Users\rdj\file.txt | drive: C:

```

### SECTION 3: mkdir(parents=True, exist_ok=True)
`mkdir()` creates one directory and fails with `FileNotFoundError` if the parent is missing. `parents=True` creates the whole chain (like Java's `Files.createDirectories`), and `exist_ok=True` makes it safe to call twice.

```text
=== SECTION 3: mkdir(parents=True, exist_ok=True) ===
mkdir() without parents -> FileNotFoundError
created: a/b/c | is_dir: True

```

### SECTION 4: exists / is_file / is_dir / stat
`exists()`, `is_file()` and `is_dir()` query the disk. `write_text()` / `read_text()` / `read_bytes()` are one-line helpers that open, read or write and close for you. `stat()` returns an object with `st_size` (bytes) and `st_mtime` (modification time as a float number of seconds since the epoch). The text `"hello, pathlib\n"` is 15 bytes.

```text
=== SECTION 4: exists / is_file / is_dir / stat ===
exists before write: False
exists: True | is_file: True | is_dir: False
size in bytes: 15
mtime is a float seconds-since-epoch: True
read_text: 'hello, pathlib\n'
read_bytes: b'hello, pathlib\n'

```

### SECTION 5: glob, rglob, iterdir
`iterdir()` lists the direct children, `glob("*.py")` matches names in one directory, and `rglob("*.py")` searches recursively. All of them return lazy iterators, so wrap them in `sorted(...)` or `list(...)` when you need a list or a stable order (the order from the OS is not guaranteed).

```text
=== SECTION 5: glob, rglob, iterdir ===
iterdir (sorted): ['a', 'sub', 'x.py', 'y.py', 'z.txt']
glob('*.py')    : ['x.py', 'y.py']
rglob('*.py')   : ['sub/deep.py', 'x.py', 'y.py']
glob() returns a lazy iterator, not a list: True

```

### SECTION 6: rename, delete
`rename()` moves or renames, `unlink()` deletes a file (`missing_ok=True` tolerates a file that is already gone) and `rmdir()` removes an **empty** directory only. For non-empty trees you need `shutil.rmtree` (see `_7_OsSysShutilAndSubprocess.py`).

```text
=== SECTION 6: rename, delete ===
after rename x.py exists: False | renamed.py exists: True
after unlink exists: False
unlink(missing_ok=True) did not raise
rmdir on empty dir ok

```

### SECTION 7: pathlib vs os.path
The same operations in the older style: `os.path.join(...)`, `os.path.basename`, `os.path.splitext`, `os.path.exists`. They work on strings, so there is no object to chain methods on. `os.fspath(path)` converts a `Path` to a `str` for APIs that still want strings.

```text
=== SECTION 7: pathlib vs os.path ===
os.path.join == Path /: True
os.path.basename: hello.txt | Path.name: hello.txt
os.path.splitext: .txt | Path.suffix: .txt
os.path.exists: True | Path.exists: True
os.fspath(Path) gives a str: True

```

### SECTION 8: resolve and the current directory
`resolve()` makes a path absolute and collapses `..` segments (and follows symlinks). `Path.cwd()` is the current working directory; `Path("rel").is_absolute()` is `False` because it depends on where the program is run.

```text
=== SECTION 8: resolve and the current directory ===
unresolved contains '..': True
resolved equals plain path: True
Path.cwd() is absolute: True
Path('rel').is_absolute(): False

temp dir removed: True
```

## Key Differences From Java

| Task | Java NIO.2 | Python pathlib |
|---|---|---|
| Create a path | `Path.of("a", "b", "c.txt")` | `Path("a") / "b" / "c.txt"` |
| Join | `base.resolve("x")` (absolute arg replaces base, same trap) | `base / "x"` |
| File name / parent | `p.getFileName()`, `p.getParent()` | `p.name`, `p.parent` |
| Exists | `Files.exists(p)` (static helper) | `p.exists()` (method on the object) |
| Make directories | `Files.createDirectories(p)` | `p.mkdir(parents=True, exist_ok=True)` |
| Read a whole file | `Files.readString(p)` | `p.read_text(encoding="utf-8")` |
| Size / times | `Files.size(p)`, `Files.getLastModifiedTime(p)` | `p.stat().st_size`, `p.stat().st_mtime` |
| Walk a tree | `Files.walk(p)` (a `Stream`, must be closed) | `p.rglob("*")` |
| Glob | `Files.newDirectoryStream(p, "*.py")` or `PathMatcher` | `p.glob("*.py")` |
| Legacy API | `java.io.File` | `os.path` string functions |
| Design | `Path` is a lean value type; the work lives in static `Files.*` methods | The `Path` object itself carries most operations |

## Key Rules / Gotchas Recap

- Use `/` to join, never string concatenation or manual `"\\"`.
- A right-hand absolute path wipes out the left side; validate user-supplied names.
- `glob`/`rglob`/`iterdir` are lazy and unordered; use `sorted()`.
- `rmdir()` only removes empty directories; `unlink()` only removes files.
- `suffix` is only the last extension; `.tar.gz` needs `suffixes`.
- Pass `encoding="utf-8"` to `read_text`/`write_text` too.

## Why This Structure Exists
Scripts that organise datasets, find logs or write outputs need paths that work on every operating system. Treating a path as an object removes a whole class of string bugs, and it is what modern Python libraries expect (almost all accept `Path` objects directly).
