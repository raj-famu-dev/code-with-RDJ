# `_7_CleaningMissingData.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Real data is messy: missing values, duplicated rows, inconsistent capitalisation and spacing, numbers stored as text, impossible values, and unparseable dates. Cleaning means finding each problem, deciding what to do (drop, fix, fill or flag), and recording that decision. This file does it on a deliberately messy 8-row dataset embedded as text in the script, so there are no files to download.

## Full Line-by-Line Breakdown

### The raw data
The CSV text is parsed with `pd.read_csv(io.StringIO(...))`. Problems planted on purpose: names with stray spaces and mixed case, a missing name, missing ages, a negative age, a city missing, inconsistent city spelling (`NEW YORK`, `new york`, `boston `), a salary with `$` and commas, a salary of `N/A`, a row that is an exact duplicate (id 2), and a date that is not a date.

```text
=== RAW messy data ===
   id      name   age      city   salary      joined
0   1    Alice   30.0  NEW YORK  $72,000  2021-03-01
1   2       bob   NaN  new york    65000  2020-07-15
2   3     CAROL  41.0    Boston      NaN  2019-11-30
3   4      Dave  29.0   boston     58000  not a date
4   2       bob   NaN  new york    65000  2020-07-15
5   5       NaN  35.0   Chicago    91000  2022-01-10
6   6     Frank  -5.0   Chicago    48000  2021-12-25
7   7     Grace  38.0       NaN  $80,500  2018-05-05
id          int64
name          str
age       float64
city          str
salary        str
joined        str
```

### SECTION 1: detecting missing values
`isna().sum()` counts missing values per column. `isna().any(axis=1)` flags rows with at least one missing value. pandas treated `N/A` as missing automatically when reading the CSV, but the text `not a date` is a normal string and is not flagged yet. The trap: `np.nan == np.nan` is `False` (NaN is not equal to anything, including itself), so always use `isna()`.

```text
=== SECTION 1: detecting missing values ===
isna().sum() per column:
id        0
name      1
age       2
city      1
salary    1
joined    0
rows with any missing value: 5
NOTE: 'N/A' was read as NaN automatically; the string 'not a date' was not.
TRAP: np.nan == np.nan is False | use isna(), never == np.nan
```

### SECTION 2: duplicates
`duplicated()` marks the second and later copies of identical rows; `drop_duplicates()` removes them. Checking `subset="id"` verifies that IDs are now unique.

```text
=== SECTION 2: duplicates ===
duplicated rows: [2]
after drop_duplicates, rows = 7
duplicates by key only (id): 0
```

### SECTION 3: string cleaning
The `.str` accessor applies string methods to a whole column: `strip()` removes surrounding spaces and `title()` normalises capitalisation, so the three spellings of New York and the two of Boston collapse into one each. Missing values stay missing.

```text
=== SECTION 3: string cleaning ===
   id   name      city
0   1  Alice  New York
1   2    Bob  New York
2   3  Carol    Boston
3   4   Dave    Boston
4   5    NaN   Chicago
5   6  Frank   Chicago
6   7  Grace       NaN
unique cities now: ['Boston', 'Chicago', 'New York']
```

### SECTION 4: type fixes
The salary column was read as text because of the `$` and commas. The code removes those characters with a regular expression and converts with `pd.to_numeric(..., errors="coerce")`, which turns anything unparseable into `NaN` instead of crashing. `pd.to_datetime(..., errors="coerce")` does the same for dates: the bad date becomes `NaT` ("not a time"). A negative age is impossible, so it is set to missing.

```text
=== SECTION 4: type fixes ===
salary dtype before: str (text, because of '$' and ',')
salary dtype after: float64 -> [72000.0, 65000.0, nan, 58000.0, 91000.0, 48000.0, 80500.0]
joined after to_datetime(errors='coerce'):
0   2021-03-01
1   2020-07-15
2   2019-11-30
3          NaT
4   2022-01-10
5   2021-12-25
6   2018-05-05
(the bad date became NaT, 'not a time')
impossible ages (<0): [6] -> treat as missing
```

### SECTION 5: fillna / dropna
`fillna` invents values (here the median age and salary, and `"Unknown"` for text), while `dropna` throws rows away. `dropna(subset=[...])` only looks at chosen columns; plain `dropna()` would keep a single row of the eight, which is far too aggressive. The median is computed from the non-missing values only. The printed rule is the real lesson: filling adds assumptions, dropping loses data, so decide per column and write the reason down. (The file works on a copy so the original is still available.)

```text
=== SECTION 5: fillna / dropna ===
missing counts now:
id        0
name      1
age       2
city      1
salary    1
joined    1
filled copy:
   id     name   age      city   salary
0   1    Alice  30.0  New York  72000.0
1   2      Bob  35.0  New York  65000.0
2   3    Carol  41.0    Boston  68500.0
3   4     Dave  29.0    Boston  58000.0
4   5  Unknown  35.0   Chicago  91000.0
5   6    Frank  35.0   Chicago  48000.0
6   7    Grace  38.0   Unknown  80500.0
median age used: 35.0 (computed from the non-missing ages only)
dropna(subset=['salary','name']) keeps ids: [1, 2, 4, 6, 7]
dropna() with no subset keeps ids: [1] (too aggressive: loses almost everything)
DECISION RULE: dropping loses rows; filling invents values. Pick per column and record why.
```

### SECTION 6: clean result
The final dtypes show `salary` as a float, `joined` as a datetime, and the text columns as `str`. The remaining `NaT` in `joined` was left missing deliberately, because inventing a date is not justified.

```text
=== SECTION 6: clean result ===
id                 int64
name                 str
age              float64
city                 str
salary           float64
joined    datetime64[us]
   id     name   age      city   salary     joined
0   1    Alice  30.0  New York  72000.0 2021-03-01
1   2      Bob  35.0  New York  65000.0 2020-07-15
2   3    Carol  41.0    Boston  68500.0 2019-11-30
3   4     Dave  29.0    Boston  58000.0        NaT
4   5  Unknown  35.0   Chicago  91000.0 2022-01-10
5   6    Frank  35.0   Chicago  48000.0 2021-12-25
6   7    Grace  38.0   Unknown  80500.0 2018-05-05
```

## Key Differences From Java
| Idea | Java | Python with pandas |
|---|---|---|
| Missing | `null` (NullPointerException if used) | `NaN` / `NaT` / `pd.NA`, which propagate through maths instead of crashing |
| Trim and case | `s.trim().toLowerCase()` in a loop | `df["name"].str.strip().str.title()` on the whole column |
| Parse numbers | `Double.parseDouble` (throws `NumberFormatException`) | `pd.to_numeric(..., errors="coerce")` |
| Parse dates | `LocalDate.parse(...)` | `pd.to_datetime(..., errors="coerce")` |
| De-duplicate | `new LinkedHashSet<>(list)` with `equals`/`hashCode` | `df.drop_duplicates()` |

How you would do this in Java: read each row, validate each field in a `try/catch`, trim strings, parse numbers and dates into typed fields, and use a `Set` for duplicates. It works but takes many more lines than the column-wise pandas calls.

## Key Rules / Gotchas Recap
- Never compare to `np.nan` with `==`; use `isna()`.
- `errors="coerce"` turns bad values into missing instead of raising, so count missing values again afterwards.
- Clean strings (`strip`, case) before counting categories or removing duplicates.
- Plain `dropna()` can remove almost every row; use `subset=`.
- Every fill or drop is an assumption; record why.

## Why This Structure Exists
Models and evaluations are only as good as the data fed to them. Cleaning is usually the largest share of a data project, and it also matters in security tooling, where log files are never tidy.
