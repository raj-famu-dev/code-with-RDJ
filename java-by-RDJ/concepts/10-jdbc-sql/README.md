# 10 · JDBC and SQL

**Priority: LATER.** Databases are needed before Spring Data JPA makes sense.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic. Commit a `schema.sql` alongside.

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_SqlRefresher` | Joins, `GROUP BY`, indexes, normalization (notes in `.md`, queries in `schema.sql`) | ⬜ |
| 2 | `_2_JdbcConnection` | `Connection`, `Statement`, `ResultSet`, closing resources correctly | ⬜ |
| 3 | `_3_PreparedStatements` | Demonstrate SQL injection on **your own local database**, then fix it | ⬜ |
| 4 | `_4_Transactions` | Commit, rollback, a transfer that must be atomic | ⬜ |
| 5 | `_5_ConnectionPooling` | Why opening a connection per request is slow | ⬜ |
| 6 | `_6_DaoPattern` | Separating data access from business logic | ⬜ |

**Exit test:** show a test that fails if you remove the transaction from your transfer method.
