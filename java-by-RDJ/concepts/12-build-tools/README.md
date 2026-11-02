# 12 · Build Tools (Maven and Gradle)

**Priority: NEXT.** Every project from here on should be a Maven or Gradle project, not loose `.java` files.

Convention: one `_N_Name.md` per topic (this folder is mostly configuration, so some topics have no `.java`).

| # | Topic | Question it must answer | Status |
|---|---|---|:---:|
| 1 | `_1_ProjectLayout` | Why `src/main/java` and `src/test/java`? | ⬜ |
| 2 | `_2_Maven` | `pom.xml`, lifecycle (`compile`, `test`, `package`), dependency scopes | ⬜ |
| 3 | `_3_Gradle` | `build.gradle.kts`, tasks, dependency configurations | ⬜ |
| 4 | `_4_Dependencies` | Transitive dependencies and version conflicts | ⬜ |
| 5 | `_5_RunnableJar` | Build and run an executable JAR with `java -jar` | ⬜ |

**Exit test:** `mvn clean package` succeeds on a fresh clone of one of your projects.
