# 11 · Testing (JUnit 5 and Mockito)

**Priority: LATER, but start using it as soon as `12-build-tools` is done.**

Convention: one `_N_Name.java` plus one `_N_Name.md` per topic.

| # | File | Question the file must answer | Status |
|---|---|---|:---:|
| 1 | `_1_UnitTestBasics` | `@Test`, assertions, arrange-act-assert | ⬜ |
| 2 | `_2_ParameterizedTests` | Many inputs, one test; edge cases (null, empty, negative, boundary) | ⬜ |
| 3 | `_3_ExceptionTests` | `assertThrows` against your custom exceptions from `04` | ⬜ |
| 4 | `_4_MockingWithMockito` | Mock vs stub; `verify`; testing a service without its repository | ⬜ |
| 5 | `_5_TddMiniFeature` | One feature built red, green, refactor, with a commit per step | ⬜ |
| 6 | `_6_CoverageWithJaCoCo` | Read a coverage report and explain why 100% is not the goal | ⬜ |

**Exit test:** one of your tests failed first for the right reason, and your commit history shows it.
