<div align="center">

<img src="../../assets/modules/09-modern-java.svg" alt="Modern Java (17 to 21): Records, sealed types, pattern matching. Animated banner by Raj Patel (RDJ)." width="100%"/>

<br/>

![Status](https://img.shields.io/badge/Status-Reference%20Material-0EA5E9?style=for-the-badge)
![Topics](https://img.shields.io/badge/Topics-7-7C3AED?style=for-the-badge)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Author](https://img.shields.io/badge/By-Raj%20Patel%20(RDJ)-22D3EE?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

*Records, sealed types, pattern matching*

[Overview](#-overview) •
[Topics](#-topics) •
[Exit Test](#-exit-test) •
[Run It](#-run-it) •
[Status Note](#-status-note)

⬅ [Module 08](../08-lambdas-streams/) · [Java Mastery Lab](../../README.md) · [Module 10](../10-jdbc-sql/) ➡

</div>

---

## 🎯 Overview

**Priority: LATER.** Your repo badge says Java 21, so this folder is where that claim gets proof.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

**Module status:** 📘 Reference material: compiled and run, not yet counted as mine.


## 📚 Topics

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_VarAndTextBlocks` | Where `var` helps and where it hurts | 📘 |
| 2 | `_2_Records` | What a record gives you for free; compact constructors | 📘 |
| 3 | `_3_SealedClasses` | Restricting an inheritance hierarchy | 📘 |
| 4 | `_4_SwitchExpressionsAndPatterns` | Pattern matching for `switch` and `instanceof`, record patterns | 📘 |
| 5 | `_5_JavaTimeApi` | `LocalDate`, `Duration`, `Period`, formatting; why `Date` is legacy | 📘 |
| 6 | `_6_HttpClient` | Call a REST API and parse the response (uses a local server so it runs offline) | 📘 |
| 7 | `_7_ModernJavaCapstone` | Payment system modeled with sealed types and records | 📘 |

## 🧪 Exit Test

show one place where a modern feature replaced boilerplate and one where using it would have been showing off.

## 🚀 Run It

From the repository root (JDK 21):

```bash
cd java-by-RDJ/concepts/09-modern-java
javac -d out _*.java
java -cp out _1_VarAndTextBlocks
```

`out/` is git-ignored. Swap `_1_VarAndTextBlocks` for any other `_N_Name` class to run that topic.

## 🧾 Status Note

**Key:** ✅ complete and understood by me · 📘 reference added (compiled and run) · 🔄 in progress · ⬜ not started.

📘 = reference file and walkthrough committed (compiled and run). Do not mark a row ✅ until you have retyped the file, broken it on purpose, and rewritten its `.md` in your own words.

---

<div align="center">

### 👨‍💻 Built and owned by Raj Patel (RDJ)

Computer Science undergraduate at **Florida A&M University** · Tallahassee, Florida · GitHub [`raj-famu-dev`](https://github.com/raj-famu-dev)

This is my personal learning lab and portfolio. I build it, I maintain it, and I am accountable for what it claims.

<sub>The reference files here were drafted with Claude and say so in their first line. I count a topic as mine (✅) only after I retype it, break it on purpose and rewrite its walkthrough in my own words.</sub>

⬅ [Module 08](../08-lambdas-streams/) · [Java Mastery Lab](../../README.md) · [Module 10](../10-jdbc-sql/) ➡

**© 2026 Raj Patel (RDJ).** Released under the [MIT License](../../LICENSE).

</div>
