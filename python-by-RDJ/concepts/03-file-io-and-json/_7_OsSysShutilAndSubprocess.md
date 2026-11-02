# `_7_OsSysShutilAndSubprocess.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Four standard-library modules connect a Python program to its surroundings: `os.environ` exposes environment variables (where secrets and configuration live), `sys` exposes command-line arguments and platform details, `shutil` copies, moves and deletes whole file trees, and `subprocess` runs other programs and captures their output. They are powerful and therefore dangerous when fed untrusted input; the key safety rule is to pass `subprocess` a **list** of arguments and never use `shell=True` with user-provided text.

## Full Line-by-Line Breakdown

Destructive operations run only inside a temporary directory the script creates. Values that depend on your machine are labelled "environment-dependent" in the output.

### SECTION 1: os.environ
`os.environ` behaves like a dictionary of strings. `os.environ["X"]` raises `KeyError` when missing, while `.get("X", default)` and `os.getenv("X")` do not. Values **must be strings**; assigning `5` raises `TypeError`. Changes affect only the current process and any child processes it starts, not your shell. The script uses a made-up variable name and deletes it afterwards.

```text
=== SECTION 1: os.environ ===
type: _Environ (dict-like, str -> str only)
os.environ['RDJ_DEMO_VAR']: hello
get with default: <default>
missing key via [] -> KeyError
non-str value -> TypeError: str expected, not int
getenv alias: hello
after del: None
Secrets (API keys) belong in env vars, never in source code.

```

### SECTION 2: sys.argv, sys.platform, sys.version_info
`sys.argv` is the list of command-line arguments, and `argv[0]` is the script name (not the first argument, unlike Java's `args[0]`). Run with no extra arguments, `argv[1:]` is empty. `sys.platform` (`linux`, `darwin`, `win32`) and `os.name` differ per machine. `sys.version_info` compares like a tuple. `sys.executable` is the path to the interpreter running the script, which is what you should use to launch another Python.

```text
=== SECTION 2: sys.argv, sys.platform, sys.version_info ===
sys.argv[0] ends with this file: True
extra args received: [] <- empty when run with no arguments
sys.platform (environment-dependent): linux
Python >= 3.10: True
os.name (environment-dependent): posix
sys.executable is a path to the running interpreter: True

```

### SECTION 3: shutil copy / move / rmtree on temp dirs
`shutil.copy` copies a file, `copytree` copies a directory recursively (and raises `FileExistsError` if the destination exists, unless `dirs_exist_ok=True`), `move` renames or relocates, and `os.remove` deletes one file. `os.rmdir` only deletes an empty directory, hence the error on a non-empty one. `shutil.rmtree` deletes a whole tree with no confirmation and no recycle bin, so only ever call it on paths you constructed yourself. `shutil.disk_usage` returns total/used/free bytes.

```text
=== SECTION 3: shutil copy / move / rmtree on temp dirs ===
copy: alpha
copytree: ['a.txt', 'nested', 'nested/b.txt']
copytree onto existing dir -> FileExistsError
dirs_exist_ok=True merges instead
move: old exists = False | new exists = True
os.rmdir on non-empty dir -> OSError
rmtree removed src: True
RULE: only rmtree paths you built yourself; never a path from user input.
disk usage keys: ['total', 'used', 'free']

```

### SECTION 4: subprocess.run with a list
`subprocess.run([sys.executable, "--version"], capture_output=True, text=True, timeout=10, check=True)` starts the same Python interpreter, waits, and returns a `CompletedProcess` with `returncode`, `stdout` and `stderr`. `text=True` decodes output to `str`. `check=True` raises `CalledProcessError` on a non-zero exit code. `timeout=` kills a child that runs too long (`TimeoutExpired`). A program that does not exist raises `FileNotFoundError`. The version string printed depends on your installation.

```text
=== SECTION 4: subprocess.run with a list ===
returncode: 0
stdout starts with 'Python': True
stdout (environment-dependent): Python 3.13.18
stderr empty: True
exit code: 3 | stdout: 'out\n' | stderr: 'err\n'
check=True raises CalledProcessError, returncode = 5
timeout=0.3 -> TimeoutExpired (child is killed)
unknown program -> FileNotFoundError

```

### SECTION 5: why never shell=True with user input
With a list, each element is passed to the program as one literal argument: the hostile-looking text `hello; echo INJECTED` arrives as a single string and nothing is executed. With `shell=True` the command string goes to a shell (`/bin/sh` or `cmd.exe`), where `;`, `&&`, `|` and backticks start new commands; that is **command injection**. The script deliberately does not demonstrate the vulnerable call.

```text
=== SECTION 5: why never shell=True with user input ===
list form passes it as ONE literal argument: ['hello; echo INJECTED']
With shell=True the string would go to /bin/sh, where ';' starts a second
command. That is command injection. We deliberately do NOT run that here.
Rule: pass a list, keep shell=False (the default), never build commands
with f-strings from untrusted text.

temp dir removed: True
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Environment variables | `System.getenv("X")` returns `null` if missing; the map is read-only | `os.environ["X"]` (KeyError) or `.get`; **writable** for the current process |
| Platform | `System.getProperty("os.name")` | `sys.platform`, `platform.system()` |
| Program arguments | `main(String[] args)`; `args[0]` is the first argument | `sys.argv`; `argv[0]` is the script, `argv[1:]` are the arguments |
| Copy / move | `Files.copy`, `Files.move` (one file; recursion is manual via `Files.walkFileTree`) | `shutil.copy`, `copytree`, `move`, `rmtree` |
| Run a program | `new ProcessBuilder(list).start()` then read streams, `waitFor()` | `subprocess.run(list, capture_output=True, text=True)` |
| Shell injection | `Runtime.exec(String)` tokenizes without a shell; `ProcessBuilder("sh","-c",...)` is the risky pattern | `shell=True` is the risky pattern; list form is safe |
| Exit | `System.exit(n)` | `sys.exit(n)` |
| Timeouts | `process.waitFor(timeout, unit)` | `timeout=` argument |

## Key Rules / Gotchas Recap

- Environment values are always strings; use `.get` for optional settings.
- Keep secrets in environment variables, not in code or Git.
- `sys.argv[0]` is the script name.
- `shutil.rmtree` is irreversible; never feed it a user-supplied path.
- `copytree` fails if the destination exists unless `dirs_exist_ok=True`.
- `subprocess.run`: use a list, keep `shell=False`, set `timeout`, and consider `check=True`.
- Use `sys.executable` to launch the same interpreter, not the string `"python"`.

## Why This Structure Exists
Automation, build scripts, security tools and ML pipelines all shell out to other programs and manipulate files. Using list-form `subprocess` and controlled deletion is the difference between a useful tool and one that can be turned into a command-injection or data-loss bug.
