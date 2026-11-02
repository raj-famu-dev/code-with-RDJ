<div align="center">

<img src="../../assets/modules/07-file-io.svg" alt="File I/O: Files, streams, buffers, NIO.2. Animated banner by Raj Patel (RDJ)." width="100%"/>

<br/>

![Status](https://img.shields.io/badge/Status-Reference%20Material-0EA5E9?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-7-7C3AED?style=for-the-badge)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

*Files, streams, buffers, NIO.2*

[Overview](#-overview) •
[Topics](#-topics) •
[Exit Test](#-exit-test) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 06](../06-generics/) · [Java Mastery Lab](../../README.md) · [Module 08](../08-lambdas-streams/) ➡

</div>

---

## 🎯 Overview

**Priority: NEXT.** Needed for the file-backed projects.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

**Module status:** 📘 Reference material: compiled and run, not yet counted as mine.


## 📚 Topics

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_PathAndFiles` | `Path`, `Files.exists`, create, copy, delete (NIO.2) | 📘 |
| 2 | `_2_ReadingTextFiles` | `Files.readAllLines` vs `BufferedReader`; when does each break on large files? | 📘 |
| 3 | `_3_WritingTextFiles` | Overwrite vs append, `BufferedWriter`, encoding (UTF-8) | 📘 |
| 4 | `_4_BinaryIO` | Streams vs readers/writers | 📘 |
| 5 | `_5_CsvAndJson` | Parse a CSV by hand, then read JSON with a library | 📘 |
| 6 | `_6_SerializationAndItsDangers` | Java serialization basics and why to prefer JSON | 📘 |
| 7 | `_7_FileIOCapstone` | Log analyzer: tolerates corrupt lines, writes a summary CSV safely (the contact book is `projects/project-05`) | 📘 |

## 🧪 Exit Test

what happens to your program if the file is missing, empty, or half-written?

## 🚀 Run It

From the repository root (JDK 21):

```bash
cd java-by-RDJ/concepts/07-file-io
javac -d out _*.java
java -cp out _1_PathAndFiles
```

`out/` is git-ignored. Swap `_1_PathAndFiles` for any other `_N_Name` class to run that topic.

## 🧾 Status Note

**Key:** ✅ complete and understood by me · 📘 reference added (compiled and run) · 🔄 in progress · ⬜ not started.

📘 = reference file and walkthrough committed (compiled and run). Do not mark a row ✅ until you have retyped the file, broken it on purpose, and rewritten its `.md` in your own words.

---

<div align="center">

### 👨‍💻 Built and owned by Raj Patel (RDJ)

Computer Science undergraduate at **Florida A&M University** · Tallahassee, Florida · GitHub [`raj-famu-dev`](https://github.com/raj-famu-dev)

This is my personal learning lab and portfolio. I build it, I maintain it, and I am accountable for what it claims.

<sub>The reference files here were drafted with Claude and say so in their first line. I count a topic as mine (✅) only after I retype it, break it on purpose and rewrite its walkthrough in my own words.</sub>

⬅ [Module 06](../06-generics/) · [Java Mastery Lab](../../README.md) · [Module 08](../08-lambdas-streams/) ➡

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](../../LICENSE).

</div>
