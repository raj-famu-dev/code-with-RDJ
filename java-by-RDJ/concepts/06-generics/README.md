# 06 · Generics

**Priority: NEXT.** Finish `03` to `05` first. Generics make the collections you learned in `03` make sense.

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_GenericClasses` | Write your own `Box<T>` and `Pair<A, B>`; why not just use `Object`? | ⬜ |
| 2 | `_2_GenericMethods` | Type inference, `static <T> ...` | ⬜ |
| 3 | `_3_BoundedTypes` | `<T extends Comparable<T>>` and writing a generic `max` | ⬜ |
| 4 | `_4_Wildcards` | `?`, `? extends T`, `? super T`; the PECS rule with one example of each | ⬜ |
| 5 | `_5_TypeErasure` | What disappears at runtime, why generic arrays are restricted | ⬜ |
| 6 | `_6_GenericsCapstone` | Your own generic `Stack<T>` and `Queue<T>` | ⬜ |

**Exit test:** explain PECS and why `List<Object>` is not a supertype of `List<String>`.
