# `_4_CsvFiles.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
CSV (comma-separated values) looks trivial but has quoting rules: fields containing commas, quotes or newlines are wrapped in double quotes, and a quote inside a field is doubled. The `csv` module implements those rules so you do not have to, with `reader`/`writer` working on lists and `DictReader`/`DictWriter` working on dictionaries keyed by the header row. Two classic traps are splitting lines yourself with `split(",")` and forgetting `newline=""` when opening the file.

## Full Line-by-Line Breakdown

### SECTION 1: csv.writer
`csv.writer(f)` wraps a file; `writerow` writes one row, `writerows` writes many. Numbers are converted to text automatically. The file must be opened with `newline=""` so the module controls line endings itself. By default each row ends with `\r\n` (the CSV standard, RFC 4180), which you can see in the raw bytes.

```text
=== SECTION 1: csv.writer ===
raw bytes on disk: b'name,age,city\r\nAda,36,London\r\nLinus,54,Portland\r\n'
csv.writer ends rows with \r\n by default (RFC 4180).

```

### SECTION 2: csv.reader (everything is a string)
`csv.reader(f)` yields each row as a list of strings. CSV has no types: `36` comes back as the string `'36'`, so you must convert (`int(...)`) yourself. `header, *data = list(...)` splits the first row from the rest.

```text
=== SECTION 2: csv.reader (everything is a string) ===
['name', 'age', 'city']
['Ada', '36', 'London']
['Linus', '54', 'Portland']
age column types: {'str'} <- convert yourself
sum of ages: 90

```

### SECTION 3: DictReader and DictWriter
`DictReader` uses the first row as keys, so you refer to columns by name (`row["score"]`) instead of position, which survives column reordering. `DictWriter` needs `fieldnames`, `writeheader()` writes the header, and writing a dict with an unknown key raises `ValueError` (a useful typo catcher).

```text
=== SECTION 3: DictReader and DictWriter ===
{'name': 'Ada', 'age': '36', 'city': 'London'}
{'name': 'Linus', 'age': '54', 'city': 'Portland'}
best: Mia 91
extra key -> ValueError: dict contains fields not in fieldnames: 'grade'

```

### SECTION 4: TRAP - naive split(',') vs real CSV quoting
`'1,"Hello, world"'.split(",")` yields three pieces and leaves stray quote characters, because it does not know the comma was inside quotes. `csv.reader` returns the correct two fields, and decodes `""` back into a single `"`.

```text
=== SECTION 4: TRAP - naive split(',') vs real CSV quoting ===
naive split : ['1', '"Hello', ' world"'] <- WRONG: 3 fields, comma inside quotes broke it
csv.reader  : ['1', 'Hello, world']
escaped quote: ['2', 'She said "hi"']

```

### SECTION 5: writer quoting rules
The default `QUOTE_MINIMAL` quotes only fields that need it (commas, quotes, newlines) and doubles inner quotes. `QUOTE_ALL` quotes everything, `QUOTE_NONNUMERIC` quotes strings but not numbers, and `delimiter=";"` changes the separator (common in European exports). The script writes into `io.StringIO` so you can see the exact text.

```text
=== SECTION 5: writer quoting rules ===
QUOTE_MINIMAL (default): 'plain,"has,comma","has ""quote""","multi\nline"\r\n'
QUOTE_ALL              : '"a","1","2.5"\r\n'
QUOTE_NONNUMERIC       : '"a",1,2.5\r\n'
delimiter=';'          : 'x;"y;z"\r\n'

```

### SECTION 6: TRAP - newline=''
The csv module writes `\r\n` itself. If the file is opened in normal text mode, Python's own newline translation runs on top of it; on Windows that turns `\r\n` into `\r\r\n`, which many programs show as a blank line between rows. Also, newlines *inside* quoted fields only round-trip correctly with `newline=""`. The script cannot reproduce Windows behaviour on Linux, so it **simulates** the translation with a string replace and says so; the round-trip of an embedded newline is real.

```text
=== SECTION 6: TRAP - newline='' ===
with newline=''   : b'a,b\r\n'
Windows w/o newline='' would write: 'a,b\r\r\n' <- doubled \r
Also: embedded newlines inside quoted fields only round-trip with newline=''.
round trip: [['multi\nline', 'x']]

```

### SECTION 7: dialects and missing columns
`delimiter="\t"` reads TSV. If a row is **short**, `DictReader` fills missing columns with `None`; if it is **long**, the extra values are collected in a list under the key `None`. Real-world CSVs are often ragged, so check for this.

```text
=== SECTION 7: dialects and missing columns ===
TSV via delimiter: [['a', 'b'], ['1', '2']]
short row DictReader: {'a': '1', 'b': '2', 'c': None} <- missing = None
long row DictReader : {'a': '1', 'b': '2', None: ['3']} <- extras under None key

temp dir removed: True
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Standard library support | **None.** You add OpenCSV, Apache Commons CSV or univocity | Built-in `csv` module |
| Quick-and-dirty approach | `line.split(",")` (same quoting bug) | `line.split(",")` (same bug); use `csv` instead |
| Rows as objects | Map to a class by hand or with annotations (OpenCSV beans) | `DictReader` gives dicts per row |
| Typed values | Parse manually (`Integer.parseInt`) or via bean mapping | Everything is `str`; convert manually (or use `pandas.read_csv` which infers types) |
| Line endings | `BufferedWriter.newLine()` uses the platform separator | `csv.writer` emits `\r\n`; open with `newline=""` |
| Resource handling | try-with-resources around reader/writer | `with open(..., newline="")` |

## Key Rules / Gotchas Recap

- Always `open(path, newline="", encoding="utf-8")` for CSV, in both read and write.
- Never parse CSV with `split(",")`; quoted fields will break it.
- Everything read is a string; convert numbers and dates yourself.
- `DictWriter` raises `ValueError` for keys not in `fieldnames`.
- `DictReader` shows ragged rows as `None` values or a `None` key.
- Choose `delimiter=` for TSV or semicolon files.

## Why This Structure Exists
CSV is the lingua franca of datasets, exports and spreadsheets, and AI/data work starts with loading it correctly. Understanding the raw module explains what `pandas.read_csv` is doing for you and why a malformed row can silently corrupt a dataset.
