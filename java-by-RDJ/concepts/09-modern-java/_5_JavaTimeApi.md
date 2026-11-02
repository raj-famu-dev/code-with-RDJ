> 📘 Reference material drafted with Claude. Not yet learned: retype `_5_JavaTimeApi.java`, break it on purpose, then rewrite this walkthrough in your own words.

# The java.time API

## Concept

`java.time` (Java 8) replaced `Date` and `Calendar`, which were mutable, counted months from 0 and years from 1900, and blurred "a date" with "a moment". Every type says what it represents and is **immutable**. The program uses fixed dates (not `now()`) so output is identical on every run.

## Full Line-by-Line Breakdown

**Section 2: one type per idea.**

| Type | Meaning |
|---|---|
| `LocalDate` | a calendar date (no time, no zone) |
| `LocalTime` | a clock time |
| `LocalDateTime` | date + time, no zone |
| `ZonedDateTime` | date + time + zone |
| `Instant` | one exact moment on the timeline (UTC), for timestamps |

`LocalDate.of(2026, 3, 1)` is a `SUNDAY`, day 60. Invalid dates are rejected: `Invalid date 'FEBRUARY 30'`.

**Section 3: immutable.** `date.plusDays(7)` returns a **new** date; the original is untouched (and a call that ignores the result is a classic bug). `plusMonths(1)` from Jan 31 clamps to `2026-02-28`. `TemporalAdjusters` give "first Monday" (`2026-03-02`) and "last day of month" (`2026-03-31`).

**Section 4: `Period` vs `Duration`.** `Period` is date units: `P35Y9M9D`. `Duration` is exact time: `PT8H30M`. `ChronoUnit.DAYS.between(...)` gives `59`.

**Section 5: formatting and parsing.** `DateTimeFormatter` is immutable and thread-safe (unlike the old `SimpleDateFormat`): `Sunday, 1 March 2026 at 14:30`. ISO text parses with no formatter; other formats need one. A wrong format gives `DateTimeParseException`. Mixing up `MM` (month) and `mm` (minutes) is a very common bug.

**Section 6: time zones.** The same instant, different wall-clock times:

```
New York: 2026-07-01T09:00-04:00[America/New_York]
Tokyo:    2026-07-01T22:00+09:00[Asia/Tokyo]   (same instant)
UTC:      2026-07-01T13:00Z[UTC]
```

Daylight saving: 2:30 on 8 March 2026 does not exist in New York, so it becomes `03:30`; 1:00 plus 2 **real** hours that day is `04:00`.

**Section 7: `Instant`** for timestamps: `Instant.ofEpochSecond(0)` is `1970-01-01T00:00:00Z`, plus a day is 86,400 seconds.

## Key Rules

1. Choose the type that says what you mean.
2. Use the return value (immutable).
3. `Period` for calendar amounts, `Duration` for exact time.
4. Store UTC/`Instant`; convert to a zone only to display.
5. Pass a `Clock` for testable code instead of calling `now()` everywhere.

## Gotchas Recap

- `MM` vs `mm`.
- Month-end arithmetic clamps.
- Local date/times in a zone with DST can be skipped or repeated.

## Why This Structure Exists

Types first, then arithmetic, then the zone tricks that cause real bugs.
