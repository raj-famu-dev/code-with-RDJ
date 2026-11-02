# `_8_LoggingAndArgparse.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`logging` replaces scattered `print()` calls with leveled messages (DEBUG, INFO, WARNING, ERROR, CRITICAL) that you can route to the console, a file or elsewhere and filter without changing the code that produces them. `argparse` turns command-line text into validated Python values and generates `--help` and error messages for free. Together they are the standard skeleton of any command-line tool. In this file argparse always parses an explicit list of strings instead of the real command line, so the output is the same every run.

## Full Line-by-Line Breakdown

### SECTION 1: logging levels and the default threshold
The five levels are numbers (10, 20, 30, 40, 50). The root logger's default threshold is `WARNING`, so `debug()` and `info()` messages are discarded unless you configure otherwise, a common surprise for beginners.

```text
=== SECTION 1: logging levels and the default threshold ===
levels: {10: 'DEBUG', 20: 'INFO', 30: 'WARNING', 40: 'ERROR', 50: 'CRITICAL'}
root logger default level: WARNING <- DEBUG/INFO hidden by default

```

### SECTION 2: a logger with a handler and format
A **logger** (`getLogger("rdj.demo")`) creates messages; a **handler** (`StreamHandler`) decides where they go; a **formatter** decides how they look (`%(levelname)-8s %(name)s: %(message)s`). Here the handler writes to an in-memory `StringIO` so the output is captured and printed in a controlled way. `setLevel(DEBUG)` lets everything through; `propagate = False` stops messages also reaching the root logger. Arguments are passed lazily (`log.warning("disk at %d%%", 91)`), so the string is only built if the message will actually be emitted; avoid f-strings inside log calls.

```text
=== SECTION 2: a logger with a handler and format ===
DEBUG    rdj.demo: debug message
INFO     rdj.demo: info message
WARNING  rdj.demo: disk at 91%
ERROR    rdj.demo: something failed
TRAP: use log.info('x=%s', x), not f-strings: formatting is skipped when the level is off.

```

### SECTION 3: handler level vs logger level
A message must pass **two** filters: the logger's level and each handler's level. The logger lets everything through, but the handler's `WARNING` level drops the debug and info lines. This is how you send everything to a file but only warnings to the console.

```text
=== SECTION 3: handler level vs logger level ===
[WARNING] shown
[CRITICAL] shown too

```

### SECTION 4: logging to a file and exceptions
`FileHandler` appends to a file. The format `%(levelname)s|%(funcName)s|%(message)s` avoids timestamps so the output is reproducible (in real apps you would add `%(asctime)s`). `logger.exception("...")` logs at ERROR and automatically appends the current traceback; call it only inside an `except` block. The script closes and removes the handler so the file can be cleaned up.

```text
=== SECTION 4: logging to a file and exceptions ===
first line : INFO|<module>|starting
second line: ERROR|risky|caught a problem
traceback present: True

```

### SECTION 5: logger hierarchy (dots)
Logger names form a tree: `shop.cart` is a child of `shop`. A child with no handler passes records up to its parent (propagation), and with no level of its own it inherits the parent's effective level. The convention is `logging.getLogger(__name__)` in every module, with handlers configured once in the application entry point.

```text
=== SECTION 5: logger hierarchy (dots) ===
child.parent is parent: True
shop.cart INFO item added
effective level of child: INFO
Libraries should call getLogger(__name__) and never configure handlers.

```

### SECTION 6: argparse basics
`ArgumentParser` describes the interface. `add_argument("filename")` is a required positional; `-n/--count` is an optional argument with `type=int` (conversion and validation); `action="store_true"` makes a flag; `choices=` restricts values; `action="append"` lets an option repeat. `parse_args(list)` returns a `Namespace`. Passing a list instead of reading `sys.argv` makes the code testable.

```text
=== SECTION 6: argparse basics ===
parsed: Namespace(filename='data.txt', count=3, verbose=True, mode='fast', tag=['a', 'b'])
args.count is int: True | args.verbose: True
defaults: {'filename': 'only.txt', 'count': 1, 'verbose': False, 'mode': 'fast', 'tag': []}
sys.argv was NOT used; we passed a list.

```

### SECTION 7: argparse errors exit with code 2
On bad input argparse prints a usage message to stderr and calls `sys.exit(2)`, which raises `SystemExit`. The script catches it and redirects stderr into a buffer to show the last line of each error: missing required argument, wrong type, invalid choice. When testing an argparse program, catch `SystemExit` (or use `parser.error` overrides).

```text
=== SECTION 7: argparse errors exit with code 2 ===
argv=[] -> exit code 2
    tool: error: the following arguments are required: filename
argv=['f.txt', '-n', 'abc'] -> exit code 2
    tool: error: argument -n/--count: invalid int value: 'abc'
argv=['f.txt', '--mode', 'medium'] -> exit code 2
    tool: error: argument --mode: invalid choice: 'medium' (choose from 'fast', 'slow')
TRAP: parse_args() calls sys.exit() on bad input; tests must catch SystemExit.

```

### SECTION 8: subcommands
`add_subparsers` gives a `git`-style interface (`add`, `commit`), where each subcommand has its own arguments and `dest="command"` records which was chosen.

```text
=== SECTION 8: subcommands ===
Namespace(command='add', path='file.py')
Namespace(command='commit', message='first')

```

### SECTION 9: wiring both together
A `-v/--verbose` flag switches the logger between `DEBUG` and `WARNING`. This is the standard pattern: one flag controls how chatty the program is.

```text
=== SECTION 9: wiring both together ===
without -v: 'WARNING heads up\n'
with -v   : 'DEBUG detail\nWARNING heads up\n'

temp dir removed: True
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Logging library | `java.util.logging` in the JDK; most projects use SLF4J + Logback/Log4j2 | `logging` in the standard library; the de-facto standard |
| Level names | `SEVERE, WARNING, INFO, FINE, FINER, FINEST` (JUL) | `CRITICAL, ERROR, WARNING, INFO, DEBUG` |
| Getting a logger | `Logger.getLogger(Foo.class.getName())` | `logging.getLogger(__name__)` |
| Lazy messages | SLF4J `log.info("x={}", x)` | `log.info("x=%s", x)` |
| Exception with trace | `log.error("msg", ex)` | `log.exception("msg")` (inside `except`) |
| CLI arguments | `main(String[] args)` parsed by hand, or picocli / Apache Commons CLI | `argparse` is built in |
| `--help` and error text | You write it (or the library generates it) | Generated automatically |
| Bad input | Your code decides (exceptions, exit codes) | `parse_args` prints usage and calls `sys.exit(2)` |

## Key Rules / Gotchas Recap

- The default level is `WARNING`; `info`/`debug` vanish unless you set a level and a handler.
- A record must pass the logger level and the handler level.
- Use `log.info("x=%s", x)` instead of an f-string.
- Libraries create loggers with `getLogger(__name__)` and never add handlers; applications configure them once.
- Remove or close handlers you add in scripts and tests to avoid duplicate output.
- `parse_args()` exits the program on error; pass a list to test.
- Never log secrets or passwords.

## Why This Structure Exists
Every serious tool (an AI service, a scanner, a data pipeline) needs configurable diagnostics and a predictable command-line interface. Logging lets you debug a running system without code changes, and argparse gives users a self-documenting way to control it.
