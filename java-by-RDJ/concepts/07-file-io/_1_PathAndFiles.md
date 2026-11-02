> 📘 Reference material drafted with Claude. Not yet learned: retype `_1_PathAndFiles.java`, break it on purpose, then rewrite this walkthrough in your own words.

# Path and Files

## Concept

In `java.nio.file`, a **`Path`** is only a *description* of a location (it need not exist). The **`Files`** class does the real work on disk (create, copy, move, delete, list). Use these instead of the old `java.io.File` in new code.

## Full Line-by-Line Breakdown

**Section 1: a Path touches nothing.**

```
path:        data/reports/2026/summary.txt
file name:   summary.txt
parent:      data/reports/2026
name count:  4
is absolute: false
exists?      false  (it is only a description)
```

**Section 2: combining.** `resolve` appends, `normalize` removes `.` and `..`, `relativize` gives the route from one path to another:

```
resolve:     project/src/Main.java
normalize:   project/src/../docs/./readme.md  ->  project/docs/readme.md
relativize:  ../docs/readme.md
```

Never glue paths with `"/"` yourself: Windows uses `\`. (The output above is from Linux.)

**Section 3: a temp workspace.** `Files.createTempDirectory` gives a fresh folder deleted at the end in `finally`, so the program never touches your own files. `Files.createDirectories` creates every missing level. `Files.size` returned `12 bytes` for `"hello files\n"`.

**Section 4: copy, move, delete.** By default `copy` and `move` refuse to overwrite: a second copy throws `FileAlreadyExistsException`. `StandardCopyOption.REPLACE_EXISTING` is explicit permission to overwrite. After the move, the source is gone and the target exists.

**Section 5: listing.** `Files.list` shows one folder; `Files.walk` all levels. Both return a `Stream` holding an open handle, so **use try-with-resources**. Order is not guaranteed, so the demo sorts:

```
Files.list(workspace): [a, notes.txt]
Files.walk(workspace): [, a, a/b, a/b/c, a/b/c/moved.txt, notes.txt]
```

The first item of the walk is an empty string: that is the workspace itself, relativized to itself.

**Section 6: exceptions.** `NoSuchFileException` (missing file), `DirectoryNotEmptyException` (deleting a non-empty folder), and `deleteIfExists` returning `false` instead of throwing.

**`deleteTree`.** Walks the folder, sorts in reverse order so children come before parents, and deletes each.

## Key Rules

1. `Path` = description; `Files` = action.
2. Build paths with `resolve`, not string concatenation.
3. Almost every `Files` method throws `IOException`.
4. Close streams from `list`/`walk`/`lines`.
5. Experiments belong in a temp directory you clean up.

## Gotchas Recap

- `Files.exists(path)` being `true` a moment ago does not mean it still is (another process may delete it).
- `Files.delete` refuses non-empty folders.
- Forgetting to close `Files.list` leaks a file handle.

## Why This Structure Exists

It goes from pure path maths (no disk), to creating files, to the destructive operations and their safety defaults, which is the order of risk.
