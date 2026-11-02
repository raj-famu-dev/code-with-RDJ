> 📘 Reference material drafted with Claude. Not yet learned: retype `_5_CsvAndJson.java`, break it on purpose, then rewrite this walkthrough in your own words.

# CSV and JSON

## Concept

Two plain-text formats for exchanging data. Both look simple, and both fail on **escaping**. The file writes and reads them by hand so you understand the rules; real projects use a library.

## Full Line-by-Line Breakdown

**CSV rules (RFC 4180).** A field containing a comma, a quote or a newline is wrapped in double quotes, and a quote inside is doubled: `"Smith, John"`, `"Grace ""Amazing"" Hopper"`.

**`escapeCsv` / `toCsvLine`** apply those rules when writing. Output:

```
name,age,city
Ada Lovelace,36,London
"Smith, John",41,"New York, NY"
"Grace ""Amazing"" Hopper",85,Arlington
```

**The classic mistake: `line.split(",")`.**

```
naive split(",") gives 5 fields (should be 3)
parseCsvLine gives  3 fields: Smith, John | 41 | New York, NY
```

**`parseCsvLine`** walks the line character by character with an `inQuotes` flag: `""` inside quotes becomes one quote, a comma outside quotes ends a field. (Limitation: no newlines inside quoted fields.)

**Round trip.** Write, read back into `Person` records, compare with `equals`: `CSV round trip equal: true`. Round-trip tests are the best check for any file format code.

**JSON writing.** `jsonString` escapes `"`, `\`, newline, tab and control characters. `toJson` builds an array of objects.

**JSON reading: `MiniJsonParser`.** A recursive-descent parser for an array of flat objects with string or integer values. It tracks a `pos` and reports errors with a position:

```
malformed JSON rejected: expected a number at position 10
```

**Library note.** The code cannot read nested objects, arrays inside objects, decimals, booleans, null or unicode escapes in input. For real work use Jackson or Gson (JSON) and Apache Commons CSV or OpenCSV (CSV). The rules you learned still apply.

(One compile-level lesson: a `\u` followed by anything other than four hex digits inside even a **comment** is a compile error in Java, because unicode escapes are processed before the code is parsed.)

## Key Rules

1. Never parse CSV with `split(",")`.
2. Escape on output; unescape on input.
3. Test every format with a round trip.
4. Bad input should fail loudly with a position, not return garbage.
5. Use a library for real JSON/CSV.

## Gotchas Recap

- Header row: skip it when reading.
- Numbers inside CSV are text until you parse them (`Integer.parseInt` can throw).
- Hand-written JSON that forgets to escape a quote produces invalid JSON.

## Why This Structure Exists

Writing the parser yourself once explains why libraries exist and what they protect you from.
