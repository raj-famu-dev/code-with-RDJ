> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# File I/O Capstone: Log Analyzer

## Concept

Read a log file, tolerate bad lines, produce statistics, and save a CSV summary safely. It combines `Path`/`Files`, buffered reading, custom exceptions, CSV output, safe saving and cleanup.

## Full Line-by-Line Breakdown

**The input.** The program writes a 10-line `app.log` into a temp folder: 7 valid lines and 3 broken ones (garbage, an unknown level `DEBUG`, a duration `fastms`). A valid line looks like `2026-03-01T10:15:30 INFO payments 120ms Payment accepted`.

**`LogEntry`** is a record. **`parse(line)`** splits with `split(" ", 5)` (the limit keeps spaces in the message) and checks, in order: 5 parts, a known level, a duration ending in `ms`, and a numeric duration. Any failure throws the checked `ParseException`.

**Reading.** A `BufferedReader` in try-with-resources reads line by line. Each line is parsed inside its own try/catch, so one bad line is **reported with its line number and skipped** instead of crashing the run:

```
parsed 7 valid lines, skipped 3
  skipped -> line 4: expected 5 parts but found 4
  skipped -> line 7: unknown level 'DEBUG'
  skipped -> line 9: duration is not a number: 'fastms'
```

**Analysis.** `Map.merge` counts per level and per service and sums durations; the slowest request is tracked in a loop:

```
entries per level: {ERROR=2, INFO=4, WARN=1}
slowest request: payments 2500ms (Card gateway timeout)
```

**Output.** The summary CSV uses `saveSafely` (temp file, then move):

```
service,requests,avg_ms
auth,2,24
payments,3,1173
search,2,48
```

Averages use integer division (for `auth`: (33 + 15) / 2 = 24).

**Verification and cleanup.** The CSV is read back and compared with what was written (`true`), no `.tmp` files are left, and `finally` deletes the temp folder (`cleanup done, temp folder still exists: false`).

## Key Rules

1. Bad input is expected: validate per line, report with a line number, carry on.
2. Stream the file so size does not matter.
3. Save results with temp-then-move.
4. Create experiments in a temp folder and delete them in `finally`.
5. Verify output by reading it back.

## Gotchas Recap

- `split(" ")` without a limit would shred the message text.
- Integer division truncates (`avg_ms` is rounded down).
- Catching the exception **outside** the loop would stop at the first bad line.

## Why This Structure Exists

It is the same shape as many real jobs (import, validate, summarize, export), and every earlier file in this folder appears in it once.
