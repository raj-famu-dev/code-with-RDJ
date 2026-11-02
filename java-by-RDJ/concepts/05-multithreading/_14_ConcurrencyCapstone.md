> 📘 Reference material drafted with Claude. Not yet learned: retype `_14_ConcurrencyCapstone.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Concurrency Capstone: Concurrent Word Counter

## Concept

Combine the folder: threads, a pool, `Callable`/`Future`, `ConcurrentHashMap`, and safe cleanup. The program counts words in 12 generated files and proves the parallel answers match a trusted single-threaded one.

## Full Line-by-Line Breakdown

**Setup.** `Files.createTempDirectory` makes a temp folder; `createFiles` writes 12 files of 20,000 words from a 10-word vocabulary using `new Random(42)`. The seed makes every run identical.

**`countFile(path)`** counts words in one file into a private `TreeMap`.

**Three ways to count the same files:**
1. `countSequential`: one thread; the trusted answer.
2. `countWithFutures`: one `Callable` per file, each returns its **own** map, `main` merges them. Nothing is shared while counting, so no race is possible.
3. `countWithSharedMap`: all tasks update one `ConcurrentHashMap` using `merge()`. Safe because `merge` is atomic.

**`finally`.** The pool is shut down (`shutdown`, `awaitTermination`, then `shutdownNow` if needed) and the temp folder is deleted recursively (`Files.walk` sorted in reverse so files go before their folders).

**Real output:**

```
created 12 files of 20000 words in a temp folder
total words counted: 240000 (expected 240000)
top words (count desc, then alphabetical):
  java = 24196
  queue = 24087
  pool = 24059
  atomic = 24030
  monitor = 24026
futures result equals sequential:   true
shared map result equals sequential: true
cleanup done, temp folder still exists: false
```

The counts are the same on every run because of the fixed seed (stated for this JDK's `Random` algorithm).

## Key Rules

1. Prefer designs that share nothing while working, then merge.
2. If you share, use atomic operations (`merge`).
3. Always test a concurrent version against a simple sequential one.
4. Pool shutdown and cleanup belong in `finally`.
5. Use timeouts on `get()`.

## Gotchas Recap

- A task's exception is hidden until you call `get()` (the file calls it for every future).
- Sorting needs a tie-break (`thenComparing`) for a deterministic top-5.
- Deleting files before their folder fails; sort the walk in reverse.

## Why This Structure Exists

One small realistic job, solved two ways, with an equality check: it ties the whole folder together and teaches the habit of verifying parallel code.
