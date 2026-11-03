# `_5_RAII.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
RAII (Resource Acquisition Is Initialisation) is the most important idiom in C++: a resource such as memory, a file, a lock or a socket is acquired in an object's constructor and released in its destructor. Because C++ destroys stack objects automatically at the end of their scope, even when an exception is thrown, cleanup can never be forgotten or skipped. It replaces Java's `try`/`finally` and `try-with-resources` with something that works for every resource and needs no special syntax at the call site.

## Full Line-by-Line Breakdown

### SECTION 1: ScopeGuard
`ScopeGuard` stores any callable and runs it in its destructor, so "do this when the scope ends" is one line. The output shows the work happening first and the cleanup after. When two guards are alive, they run in REVERSE order of creation (second, then first). `dismiss()` cancels the cleanup, which is the "commit" pattern: do a rollback unless the operation succeeded. Copying is deleted so there is only ever one owner of the cleanup duty.

Output from a real run:

```text
===== SECTION 1: ScopeGuard =====
  doing work inside the scope
  guard ran: cleanup at scope exit
  second created, runs FIRST
  first created, runs LAST
  work succeeded, committing
```

### SECTION 2: DESTRUCTORS RUN WHEN AN EXCEPTION FLIES
When `throw` executes, C++ unwinds the stack and destroys every local object on the way out, running their destructors. The guard's message prints before the `catch` block runs. This is the guarantee that makes RAII safe: cleanup is attached to the object, not to the code path.

Output from a real run:

```text
===== SECTION 2: DESTRUCTORS RUN WHEN AN EXCEPTION FLIES =====
  about to throw
  guard ran during stack unwinding
  caught: failure in the middle
```

### SECTION 3: FileHandle
`FileHandle` wraps a `FILE*`: the constructor opens (and throws if it cannot, so a half-constructed handle never exists), the destructor closes. The first block writes two lines and the file is closed and flushed at the closing brace without any `close()` call. The second block reads them back. In the third, an exception is thrown while the file is open and the output shows `closed` BEFORE the `caught` line. The fourth shows a constructor that fails: no object exists, so there is nothing to close. The temp file path is built with `std::filesystem::temp_directory_path()` and removed at the end.

Output from a real run:

```text
===== SECTION 3: FileHandle =====
  [FileHandle opened]
  [FileHandle closed]
  [FileHandle opened]
  read back: hello raii
  read back: second line
  [FileHandle closed]
  [FileHandle opened]
  [FileHandle closed]
  caught: something went wrong while the file is open (file was closed before this catch ran)
  constructor failure: cannot open /nonexistent-dir-rdj/nope.txt (no handle, nothing to close)
```

### SECTION 4: MOVING OWNERSHIP
A resource should have exactly one owner. Copying is deleted; moving is allowed: the move constructor takes the `FILE*` and leaves the source holding `nullptr` (via `std::exchange`), so only the destination closes it. The output shows one `opened` and exactly one `closed`.

Output from a real run:

```text
===== SECTION 4: MOVING OWNERSHIP =====
  [FileHandle opened]
  moved; exactly one close will follow
  [FileHandle closed]
```

### SECTION 5: THE MANUAL STYLE FOR COMPARISON
`manual_style` opens, writes and closes by hand. It works only because the author remembered to write `fclose` on BOTH the failure path and the success path; every new early return or throw added later is a new chance to leak the handle. RAII needs the close written zero times at the call site. The final `ScopeGuard` in `main` removes the temp file even if something earlier had thrown.

Output from a real run:

```text
===== SECTION 5: THE MANUAL STYLE FOR COMPARISON =====
  manual: had to remember to close before throwing
  (it only worked because the author wrote fclose twice; RAII needs it zero times)

temp file removed by a ScopeGuard
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `try (var in = new FileInputStream(f)) { }` closes at the end of the block | Any object with a destructor does this: `{ FileHandle in(path, "r"); }` |
| `finally { cleanup(); }` for everything else | A destructor or a `ScopeGuard` |
| Must remember to use try-with-resources; forgetting leaks until GC/finalisation | Cleanup is built into the type: callers cannot forget |
| Only works for `AutoCloseable` types | Works for memory, files, locks (`std::lock_guard`), sockets, transactions |
| `close()` may throw, with suppressed-exception rules | Destructors should not throw (they are `noexcept` by default) |
| GC frees memory later, at an unpredictable time | Destruction is deterministic: exactly at the closing brace |

## Key Rules / Gotchas Recap
- Acquire in the constructor, release in the destructor.
- Destructors run on normal exit AND during exception unwinding.
- Locals are destroyed in reverse order of construction.
- Make RAII types non-copyable (or deep-copy), and movable when ownership can transfer.
- If the constructor throws, the destructor does NOT run: acquire in one step per object so nothing leaks.
- Destructors must not throw.
- Prefer standard RAII types: `std::vector`, `std::string`, `std::unique_ptr`, `std::lock_guard`, `std::ifstream`.

## Why This Structure Exists
RAII is how C++ code stays correct as it grows: locks are released, files are closed and memory is freed on every path, including error paths. That reliability matters in long-running services and inference servers, and the same pattern is how security-sensitive code makes sure secrets are wiped and handles are closed even when something fails.
