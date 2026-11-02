> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Writing Text Files

## Concept

Writing is riskier than reading: the **default write erases the file**. This file shows the open options, buffered writers, and a safe save pattern.

## Full Line-by-Line Breakdown

**Section 1: the default.** `Files.writeString` creates the file or **truncates** it. Two writes in a row leave only the second: `second run`.

**Section 2: `APPEND`.** `StandardOpenOption.APPEND` adds to the end: `[second run, third line]`.

**Section 3: `CREATE_NEW`.** Fails with `FileAlreadyExistsException` if the file exists: "fail rather than overwrite".

**Section 4: `Files.write(path, lines)`** writes a list of lines.

**Section 5: `BufferedWriter`.** Collects text and writes in big chunks. try-with-resources **flushes and closes** it; forget that and the last part may never reach the disk. `newLine()` uses the platform's separator.

**Section 6: `PrintWriter`.** Gives `printf`/`println` for files:

```
alpha      3.1
beta      42.0
```

`PrintWriter` never throws `IOException`; call `checkError()` if it matters.

**Section 7: `saveSafely(target, content)`.**
1. Create a temp file **next to** the target.
2. Write the content to it.
3. Move it over the target with `ATOMIC_MOVE` (fallback: a normal replace if the file system cannot do it).
4. `finally`: delete the temp file if it is still there.

If the program crashes halfway, the old file is intact instead of half-written.

```
settings after two safe saves: theme=light
leftover .tmp files: 0
```

## Key Rules

1. A plain write **erases**: pick `APPEND` or `CREATE_NEW` on purpose.
2. Always close writers: closing flushes.
3. Important files: write a temp file, then move it.
4. Pass the charset if the file is shared with other systems.

## Gotchas Recap

- Unclosed `BufferedWriter` loses buffered data.
- `ATOMIC_MOVE` is not supported everywhere, hence the fallback.
- The temp file must be in the **same folder** (same file system) for an atomic move to work.

## Why This Structure Exists

Each option is added right after the risk it removes (overwrite, then append, then refuse-to-overwrite), ending with the pattern real programs use.
