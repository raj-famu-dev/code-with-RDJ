> 📘 Reference material drafted with Claude. Not yet learned: retype `_2_ReadingTextFiles.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Reading Text Files

## Concept

Five ways to read text, from "everything at once" to "one line at a time". Choose by file size and by what you need.

## Full Line-by-Line Breakdown

The file `poem.txt` has 5 lines, one of them blank (the file ends with a newline).

**Section 1: `Files.readString`.** The whole file as one `String` (63 characters). Fine for small files; the entire content sits in memory.

**Section 2: `Files.readAllLines`.** A `List<String>` with the line terminators removed: 5 lines, and line 3 is empty.

**Section 3: `BufferedReader` (big files).** Reads a chunk at a time. `readLine()` returns `null` at the end. try-with-resources closes the reader even on an exception.

```
BufferedReader: 5 lines, 4 non-blank
```

**Section 4: `Files.lines`.** A lazy `Stream<String>`. It holds the file open, so it must be closed (try-with-resources): `lines containing "are": 2`.

**Section 5: `Scanner`.** For tokens (words, numbers): `Scanner counted 13 words`.

**Section 6: encoding.** Text on disk is bytes; a charset says how they become characters. The word "cafe" with an accented e is 4 characters but 5 bytes in UTF-8. Reading those bytes with the **wrong** charset gives 5 characters and different text:

```
the word has 4 chars but takes 5 bytes in UTF-8
read as ISO-8859-1 (WRONG charset): 5 chars, same text as before: false
```

(The source uses a `é` escape and the program prints no accented characters, because the terminal may not display them. Since Java 18 the default charset is UTF-8, but being explicit is safer.)

**Section 7: a missing file** throws `NoSuchFileException`. The older `Scanner(String)`/`FileReader` APIs throw `FileNotFoundException`. Both are `IOException`s.

**Section 8: which one?** Small file: `readString`/`readAllLines`. Big file: `Files.lines` or `BufferedReader`. Tokens: `Scanner`.

## Key Rules

1. Close every reader and stream (try-with-resources).
2. Big files: stream them, do not load them whole.
3. State the charset when the file comes from elsewhere.
4. `readLine()` returns `null` at the end, not an empty string.

## Gotchas Recap

- Wrong charset gives garbled text with no exception.
- `Files.lines` inside a stream pipeline that is not closed leaks a handle.
- A trailing newline does not create an extra empty last line in `readAllLines`.

## Why This Structure Exists

The methods are ordered by memory use, so the "which one?" table at the end is something you have already seen working.
