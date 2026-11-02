> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Binary I/O

## Concept

Files are bytes. Text files give them a text meaning; binary files (images, zips, your own formats) give them another. Java's `byte` is **signed** (-128..127), so mask with `& 0xFF` to get 0..255.

## Full Line-by-Line Breakdown

**Section 1.** `(byte) 200` is `-56`; `& 0xFF` gives back `200`.

**Section 2.** `Files.write(path, byte[])` and `Files.readAllBytes` for small files: `[1, 2, 3, -1]` (255 shows as -1).

**Section 3: copying with a buffer.** Read a chunk into a `byte[1024]`, write **exactly the bytes read** (`out.write(buffer, 0, read)`, not `buffer.length`), repeat until `read()` returns `-1`. A 10,000-byte file copies identically.

**Section 4: `DataOutputStream`/`DataInputStream`.** Typed values in a fixed layout. The demo's made-up format is: magic number, record count, then `(name, score)` pairs. You must read in **exactly the order you wrote**.

```
scores.dat is 51 bytes
  record 1: ada = 91.5
  record 2: linus = 78.25
  record 3: grace = 99.0
EOFException: tried to read past the end
```

The 51 bytes: 4 (magic) + 4 (count) + 3 x (2-byte length + name) + 3 x 8 (double) = 4 + 4 + (5 + 7 + 7) + 24.

The magic number check (`RDJ1`) rejects files that are not in this format.

**Section 5: wrong order is not an error.** Reading the first 8 bytes as a `double` gives `2.018118813037619E88`: silent garbage, because the file has no labels.

**Section 6: byte order.** The int 1 is `[0, 0, 0, 1]` big-endian and `[1, 0, 0, 0]` little-endian. Java defaults to big-endian; many formats use little-endian; `ByteBuffer.order(...)` lets you choose.

**Section 7: text is bytes plus a charset.** A 4-character string with an accented letter takes 5 bytes in UTF-8 (`[72, 105, 32, -61, -87]`), and decodes back to the same text.

## Key Rules

1. Write `read` bytes, not `buffer.length`.
2. Read binary data in exactly the order it was written.
3. Start custom formats with a magic number (and ideally a version).
4. Mind byte order when exchanging files with other systems.

## Gotchas Recap

- `read()` may return fewer bytes than the buffer holds.
- Signed bytes: `255` prints as `-1`.
- `EOFException` means you expected more data than the file has.

## Why This Structure Exists

It builds from single bytes to a tiny custom format, and deliberately shows the silent-garbage case so you respect the "same order" rule.
