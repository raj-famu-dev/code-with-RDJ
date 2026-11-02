# `_5_JsonHandling.py`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
JSON is the standard text format for configuration and for data exchanged with web APIs and LLM tools. Python's `json` module converts between JSON text and Python objects: `dumps`/`loads` work with strings, `dump`/`load` work with files. It handles dictionaries, lists, strings, numbers, booleans and `None`; anything else (dates, sets, your own classes) needs a custom encoder, and invalid input raises `JSONDecodeError`.

## Full Line-by-Line Breakdown

### SECTION 1: dumps and loads (strings)
The `s` in `dumps`/`loads` stands for "string". `json.dumps(obj)` returns JSON text; `json.loads(text)` returns Python objects. The mapping is: dict to object, list/tuple to array, `str` to string, `int`/`float` to number, `True`/`False` to `true`/`false`, `None` to `null`. The round trip yields an equal dictionary.

```text
=== SECTION 1: dumps and loads (strings) ===
dumps: {"name": "Ada", "age": 36, "langs": ["Python", "Java"], "active": true, "boss": null}
type: str
loads: {'name': 'Ada', 'age': 36, 'langs': ['Python', 'Java'], 'active': True, 'boss': None}
round trip equal: True
Python -> JSON: True->true, None->null: [true, null, 1.5]

```

### SECTION 2: indent and sort_keys
`indent=2` pretty-prints; `sort_keys=True` gives a stable key order (handy for diffs and tests); `separators=(",", ":")` removes spaces for the smallest output. By default non-ASCII characters are escaped (`ã`), which is safe but hard to read; `ensure_ascii=False` keeps them as real characters (write the file with `encoding="utf-8"`).

```text
=== SECTION 2: indent and sort_keys ===
{
  "name": "Ada",
  "age": 36,
  "langs": [
    "Python",
    "Java"
  ],
  "active": true,
  "boss": null
}
sort_keys: {"a": 2, "b": 1}
compact  : {"a":1,"b":[1,2]}
unicode default: {"city": "S\u00e3o Paulo"}
ensure_ascii=False: {"city": "São Paulo"}

```

### SECTION 3: dump and load (files)
`json.dump(obj, f)` writes straight to an open text file and `json.load(f)` reads from one. Both expect a file object, not a path.

```text
=== SECTION 3: dump and load (files) ===
file round trip equal: True
first line on disk: {

```

### SECTION 4: JSON type-mapping surprises
Tuples come back as lists. Dictionary keys must be strings in JSON, so the integer key `1` returns as `'1'`. Sets and `datetime` objects are not serialisable and raise `TypeError`.

```text
=== SECTION 4: JSON type-mapping surprises ===
tuple becomes list: [1, 2]
int keys become str: {'1': 'a'}
set is NOT serialisable -> TypeError: Object of type set is not JSON serializable
datetime is NOT serialisable -> TypeError: Object of type datetime is not JSON serializable

```

### SECTION 5: custom encoder for dataclass and datetime
Subclass `json.JSONEncoder` and override `default(o)`, which Python calls only for objects it cannot serialise. Here it turns dates into ISO-8601 strings, sets into sorted lists (sorted for deterministic output), and dataclasses into dicts using `dataclasses.asdict`. For anything else it calls `super().default(o)`, which raises `TypeError`. For a quick job you can pass `default=str` instead. Decoding is the one-way trap: after `loads`, the date is a plain `str`, so you must rebuild objects yourself (`datetime.fromisoformat`).

```text
=== SECTION 5: custom encoder for dataclass and datetime ===
{
  "title": "Demo",
  "when": "2025-06-01T09:30:00",
  "tags": [
    "a",
    "b"
  ]
}
Same result with a function: {"d": "2025-01-01"}
decoded 'when' is just a str: str
manually rebuilt: True

```

### SECTION 6: JSONDecodeError
Invalid JSON raises `json.JSONDecodeError`, a subclass of `ValueError`, carrying `msg`, `lineno`, `colno` and `pos`. Common mistakes shown: single quotes (JSON requires double quotes), trailing commas, an empty string and truncated text. The exact message wording belongs to Python 3.13 and can differ in other versions.

```text
=== SECTION 6: JSONDecodeError ===
single quotes   -> line 1 col 2: Expecting property name enclosed in double quotes
trailing comma  -> line 1 col 8: Illegal trailing comma before end of object
empty string    -> line 1 col 1: Expecting value
truncated       -> line 1 col 12: Expecting ',' delimiter
JSONDecodeError is a subclass of ValueError: True

```

### SECTION 7: safe loading from a file
`load_json` returns a default for a **missing** file (`FileNotFoundError`) and for a **corrupt or empty** file (`JSONDecodeError`) and lets other errors propagate. An empty file is a surprisingly common failure, for example after a crashed write.

```text
=== SECTION 7: safe loading from a file ===
missing : {}
  corrupt file corrupt.json: Expecting ',' delimiter at char 7
corrupt : {}
  corrupt file empty.json: Expecting value at char 0
empty   : {}
good    : Ada

```

### SECTION 8: NaN and big numbers
Python writes `float('nan')` as `NaN`, which is **not** valid JSON; strict parsers in other languages reject it. `allow_nan=False` makes Python refuse instead. Python integers are arbitrary size and round-trip exactly, but JavaScript numbers are doubles, so very large integers can lose precision in other consumers.

```text
=== SECTION 8: NaN and big numbers ===
dumps(float('nan')): NaN <- NOT valid JSON by spec!
allow_nan=False -> ValueError
big int survives in Python: 123456789012345678901234567890

temp dir removed: True
```

## Key Differences From Java

| Idea | Java | Python |
|---|---|---|
| Library | **Not in the JDK.** Use Jackson, Gson or similar | Built-in `json` module |
| Serialise | `objectMapper.writeValueAsString(obj)` | `json.dumps(obj)` |
| Parse | `objectMapper.readValue(text, Person.class)` into a typed class | `json.loads(text)` gives dicts/lists; no automatic typing (use dataclasses, Pydantic) |
| Custom types | Annotations, `JsonSerializer`, modules (`JavaTimeModule`) | Subclass `JSONEncoder` or pass `default=` |
| Errors | `JsonProcessingException` (checked in Jackson 2) | `JSONDecodeError` (unchecked `ValueError`) |
| Pretty print | `writerWithDefaultPrettyPrinter()` | `indent=2` |
| Stable output | `ORDER_MAP_ENTRIES_BY_KEYS` | `sort_keys=True` |
| Null | `null` maps to `null` reference | `null` maps to `None` |

## Key Rules / Gotchas Recap

- `dumps`/`loads` for strings, `dump`/`load` for files.
- JSON needs double quotes; Python `repr` output is not JSON.
- Dict keys become strings; tuples become lists; sets and datetimes need an encoder.
- `loads` never recreates dates or custom classes; convert after loading.
- Catch `JSONDecodeError` (and `FileNotFoundError`) when reading files you did not just write.
- Pass `encoding="utf-8"` when opening JSON files.

## Why This Structure Exists
LLM APIs, config files, tool-calling and web services all speak JSON, so parsing failures are a daily reality. Validating and handling bad JSON gracefully is the foundation of robust AI pipelines and security tools that must not crash on hostile or malformed input.
