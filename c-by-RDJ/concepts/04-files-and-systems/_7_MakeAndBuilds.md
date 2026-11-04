# `_7_MakeAndBuilds.c` and `_7_Makefile`

## Concept
`make` reads rules that say **how** to build each file and **when** it needs rebuilding. It is the original incremental build system — the ancestor of CMake, Gradle, and every "build" button — and it still powers the C/C++ world.

## The Makefile

```makefile
CC      = gcc
CFLAGS  = -std=c17 -Wall -Wextra -Wpedantic -O0 -g
TARGET  = _7_demo

all: $(TARGET)

$(TARGET): _7_MakeAndBuilds.c
	$(CC) $(CFLAGS) -o $(TARGET) _7_MakeAndBuilds.c

test: $(TARGET)
	./$(TARGET)

sanitize: _7_MakeAndBuilds.c
	$(CC) -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o $(TARGET)_s _7_MakeAndBuilds.c
	./$(TARGET)_s

clean:
	rm -f $(TARGET) $(TARGET)_s
```

## Rule-by-Rule Breakdown

### Variables: `CC`, `CFLAGS`, `TARGET`
Text substitution (yes, like macros). One place to change the compiler or flags — `make CFLAGS="-O2"` overrides on the command line.

### `$(TARGET): _7_MakeAndBuilds.c` — the dependency rule
**Target: dependencies, TAB-indented recipe.** make's whole logic: a target is out of date if any dependency's **timestamp** is newer. Edit the `.c` → rebuild. Touch nothing → "make: Nothing to be done" (a no-op build that took one stat call). This is incremental building — and with `%.o: %.c` pattern rules, it scales to hundreds of files (compile only what changed, then relink — exactly topic 8's pipeline).

### The TAB requirement
The recipe line **must** start with a real tab. Spaces produce `*** missing separator`. The single most-asked make question in history.

### `all: $(TARGET)`
The first target in the file is the default — `make` with no arguments builds `all`. Convention: `all` should build everything, be first, and be `.PHONY`.

### `test:` — a phony target
`test` isn't a file; it's a *command* that runs the built program. **Problem:** if a file named `test` ever exists, make thinks the target is up to date and does nothing. `.PHONY: all test sanitize clean` declares "these are always commands, never files" — the fix every real Makefile carries.

### `sanitize:` — the same build under ASan/UBSan
The repo's convention (matching `cpp-by-RDJ`'s projects): every Makefile exposes `make` (normal build), `make test`, `make sanitize`, and `make clean`. The sanitizer build gets its own target so it's one command away, always.

### `clean:`
`rm -f` the build products — the git-ignorable outputs. Build artifacts never get committed; only sources do.

## Traps
- **Missing separator** — spaces instead of a tab.
- Timestamp granularity: extremely fast builds can confuse make (rare on modern filesystems).
- Recursive make (`cd subdir && make`) is the classic scale-up — and the classic "why is my build slow" — beyond this file's scope.

## Run It
```bash
make -f _7_Makefile          # build
make -f _7_Makefile test     # build + run
make -f _7_Makefile          # "Nothing to be done" — incremental no-op
touch _7_MakeAndBuilds.c && make -f _7_Makefile   # detects the change, rebuilds
make -f _7_Makefile sanitize
make -f _7_Makefile clean
```

## Why This Structure Exists
Compile-then-link (topic 8) invites the question "which files do I have to rebuild?" make's dependency graph answers it from timestamps alone — a 50-line Makefile replaces a 5-line shell script *and* rebuilds only what changed, which is the entire economic argument for every build system since.
