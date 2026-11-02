# 07 · File I/O

**Priority: NEXT.** Needed for the file-backed projects.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_PathAndFiles` | `Path`, `Files.exists`, create, copy, delete (NIO.2) | ⬜ |
| 2 | `_2_ReadingTextFiles` | `Files.readAllLines` vs `BufferedReader`; when does each break on large files? | ⬜ |
| 3 | `_3_WritingTextFiles` | Overwrite vs append, `BufferedWriter`, encoding (UTF-8) | ⬜ |
| 4 | `_4_BinaryIO` | Streams vs readers/writers | ⬜ |
| 5 | `_5_CsvAndJson` | Parse a CSV by hand, then read JSON with a library | ⬜ |
| 6 | `_6_SerializationAndItsDangers` | Java serialization basics and why to prefer JSON | ⬜ |
| 7 | `_7_FileIOCapstone` | Persistent contact book with graceful handling of missing or corrupt files | ⬜ |

**Exit test:** what happens to your program if the file is missing, empty, or half-written?
