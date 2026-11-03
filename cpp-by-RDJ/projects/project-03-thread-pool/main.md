# `main.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`main.cpp` demonstrates the pool and ends with a parallel word count over generated, in-memory text: it counts words once sequentially and once by splitting the text into slices that pool workers count in parallel, then **checks that both results are identical** before printing wall-clock timings. The counts are deterministic (seeded generator); the timings are measurements that change from run to run and machine to machine.

## Full Line-by-Line Breakdown

### Text generation
`generate_text(word_count, seed)` builds a vocabulary of 2000 distinct pseudo-words with a seeded `std::mt19937` (using `%` on its output, because the standard distributions are allowed to differ between libraries), then appends words by taking the smaller of two random indices, so some words are far more common than others. About one separator in 17 is a newline. There are no files and no keyboard input. The program takes an optional word count (`./main 300000`); the default is 2,000,000 words (about 20 MB of text).

### Counting and slicing
`count_words(std::string_view)` walks the slice, skips separators, and counts each word in an `unordered_map<string_view, size_t>` (the keys are views into the text, so no strings are copied). `split_on_boundaries` cuts the text into `workers x 4` slices and moves each cut forward to the next separator, so no word is split between two slices. More slices than threads evens out uneven slice costs.

### SECTIONS 1 to 3: the pool basics
```text
===== SECTION 1: submit returns a future; results are read in submission order =====
squares of 1..8 via 4 workers: 1 4 9 16 25 36 49 64

===== SECTION 2: an exception thrown inside a task is rethrown by future.get() =====
caught in the caller: task failed on purpose
the pool still works afterwards: 7

===== SECTION 3: shutdown() lets queued tasks finish =====
100 tasks submitted, pool destroyed immediately, tasks completed = 100
```

### SECTION 4: sequential vs pooled
Each slice becomes one `pool.submit(count_words, slice)`. The calling thread then reads the futures in order and merges each partial map into the final one. Equality is checked with `sequential == pooled` and by comparing the total word count with the number generated; the program returns exit code 1 if either differs.

```text
===== SECTION 4: parallel word count over generated in-memory text =====
generated 2000000 words, 20221153 bytes of text (seed 2024)
pool: 2 worker threads, text cut into 8 slices
CORRECTNESS: sequential result == pooled result : yes
total words counted = 2000000 (expected 2000000), distinct words = 1999
top 3 words: vufuffgqj15=2098 xbojree11=2084 bcqtl24=2061
MEASUREMENT (varies per machine and per run, not a result): sequential = 303.0 ms, pooled = 202.0 ms
MEASUREMENT: sequential/pooled time ratio on this run = 1.50 (2 hardware threads reported)
```

### Two consecutive full runs
The deterministic lines are identical between runs; the two timing lines are the only ones that differ (compare them):

```text
ThreadPool demo. std::thread::hardware_concurrency() on this machine = 2 (a measurement of THIS machine)

===== SECTION 1: submit returns a future; results are read in submission order =====
squares of 1..8 via 4 workers: 1 4 9 16 25 36 49 64

===== SECTION 2: an exception thrown inside a task is rethrown by future.get() =====
caught in the caller: task failed on purpose
the pool still works afterwards: 7

===== SECTION 3: shutdown() lets queued tasks finish =====
100 tasks submitted, pool destroyed immediately, tasks completed = 100

===== SECTION 4: parallel word count over generated in-memory text =====
generated 2000000 words, 20221153 bytes of text (seed 2024)
pool: 2 worker threads, text cut into 8 slices
CORRECTNESS: sequential result == pooled result : yes
total words counted = 2000000 (expected 2000000), distinct words = 1999
top 3 words: vufuffgqj15=2098 xbojree11=2084 bcqtl24=2061
MEASUREMENT (varies per machine and per run, not a result): sequential = 303.0 ms, pooled = 202.0 ms
MEASUREMENT: sequential/pooled time ratio on this run = 1.50 (2 hardware threads reported)
```

```text
ThreadPool demo. std::thread::hardware_concurrency() on this machine = 2 (a measurement of THIS machine)

===== SECTION 1: submit returns a future; results are read in submission order =====
squares of 1..8 via 4 workers: 1 4 9 16 25 36 49 64

===== SECTION 2: an exception thrown inside a task is rethrown by future.get() =====
caught in the caller: task failed on purpose
the pool still works afterwards: 7

===== SECTION 3: shutdown() lets queued tasks finish =====
100 tasks submitted, pool destroyed immediately, tasks completed = 100

===== SECTION 4: parallel word count over generated in-memory text =====
generated 2000000 words, 20221153 bytes of text (seed 2024)
pool: 2 worker threads, text cut into 8 slices
CORRECTNESS: sequential result == pooled result : yes
total words counted = 2000000 (expected 2000000), distinct words = 1999
top 3 words: vufuffgqj15=2098 xbojree11=2084 bcqtl24=2061
MEASUREMENT (varies per machine and per run, not a result): sequential = 294.8 ms, pooled = 157.4 ms
MEASUREMENT: sequential/pooled time ratio on this run = 1.87 (2 hardware threads reported)
```

## Key Differences From Java
| Java | C++ here |
|---|---|
| `parallelStream()` or an `ExecutorService` with `invokeAll` | Explicit slices, `submit` per slice, merge on the caller |
| Strings are objects; substrings may copy | `std::string_view` is a non-owning window: cheap, but the text must outlive every view |
| `System.nanoTime()` | `std::chrono::steady_clock` |
| `ConcurrentHashMap` for shared counts | No shared map at all: each task owns a private map and the caller merges, so no locking is needed |

## Key Rules / Gotchas Recap
- Check parallel results against a sequential reference before trusting any timing.
- Give each task its own data (a private map) and merge afterwards; sharing one map would need locks.
- A `string_view` is only valid while the text it points into is alive (the generated text lives for all of `main`).
- Timings are measurements of one machine at one moment, not facts about the code.

## Why This Structure Exists
"Split, process in parallel, merge" is the shape of batch jobs in data and AI pipelines, and the discipline of proving the parallel answer equals the sequential one is what separates a useful speedup from a fast bug.
