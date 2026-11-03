# `tests.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
`tests.cpp` is a hand-rolled test runner: a `CHECK(cond)` macro counts checks and failures, each `test_*` function is run by a `RUN` macro, and `main` returns 0 only if nothing failed. The core technique is the **oracle test**: apply thousands of seeded random operations to our structure and to the matching standard container, and compare after every step. Any disagreement is a bug in ours, because the standard container is the specification.

## Full Line-by-Line Breakdown

### The runner
`CHECK` evaluates the condition, increments `g_checks`, and on failure prints `file:line: expression` and increments `g_failures`. `RUN` remembers the failure count before and after a test and prints PASS or FAIL. No framework, no dependencies.

### Helper types
- `Tracked` counts live instances in a static; the test asserts the count returns to 0, which catches leaks, double destruction and missing destructor calls without any tool.
- `Fragile` is copy-only and can be told to throw on the Nth copy, to test the strong exception guarantee of `DynamicArray` growth.
- `ConstantHash` is the worst legal hash.

### The oracle tests (all seeded `std::mt19937`)
| Test | Operations | Oracle |
|---|---|---|
| `test_dynamic_array_oracle` | 20,000 push, pop, insert, erase, assign, clear | `std::vector<int>` |
| `test_linked_list_oracle` | 10,000 push/pop at both ends, insert/erase at random positions, reverse, copy; checked forward AND backward | `std::list<int>` |
| `test_hash_map_oracle_ints` | 50,000 `insert_or_assign`, `insert`, `erase`, `operator[]`, `find`, `contains`; load factor never above 0.75 | `std::unordered_map<int,int>` |
| `test_hash_map_oracle_strings` | 20,000 word-count style updates and erases | `std::unordered_map<std::string,size_t>` |
| `test_min_heap_oracle` | 30,000 pushes and pops (duplicates, negatives), then a full drain | `std::priority_queue` with `std::greater` |

### The behaviour tests
Aliasing (`push_back(a[0])` during growth), rule of five with live-object accounting (copy, move, copy-assign, move-assign, self-assign), `at()`/`insert`/`erase` bounds errors, strong exception safety, iterator conversion, a constant hash that must still be correct (and whose longest chain must equal the size), references surviving a rehash, heapify plus heap sort of 5000 numbers against `std::sort`, a max-heap through `std::greater`, and a heap with a `std::function` comparator.

### Real output
```text
Running tests for the from-scratch data structures (seeded std::mt19937)
[PASS] test_dynamic_array_oracle
[PASS] test_dynamic_array_strings_and_aliasing
[PASS] test_dynamic_array_rule_of_five_and_lifetimes
[PASS] test_dynamic_array_bounds_and_exceptions
[PASS] test_linked_list_oracle
[PASS] test_linked_list_rule_of_five_and_lifetimes
[PASS] test_linked_list_iterators
[PASS] test_hash_map_oracle_ints
[PASS] test_hash_map_oracle_strings
[PASS] test_hash_map_worst_case_hash_still_correct
[PASS] test_hash_map_rule_of_five_iterators_and_lifetimes
[PASS] test_hash_map_references_survive_rehash
[PASS] test_min_heap_oracle
[PASS] test_min_heap_heapify_and_heapsort_and_comparators
81 checks, 0 failed
```

### Do the tests really test? (a sanity check I ran)
I deliberately broke the code twice and re-ran. Removing the right-child comparison in `sift_down` made the tests print 4 FAIL lines. Breaking `HashMap::erase` so it never unlinks the node made the test run hang (killed by a timeout; a hang is also a detected failure). Both mutations were then reverted and the suite is green again. This was a one-time check by hand, not a permanent test.

## Key Differences From Java
| Java (JUnit) | C++ here |
|---|---|
| `@Test`, `assertEquals`, a runner discovers tests | A macro and a function list; `main` is the runner |
| Oracle = `java.util.HashMap` in `main()` of the Java file | Oracle = standard containers, only inside `tests.cpp` |
| GC hides leaks | `Tracked::live` must return to 0; sanitizers back this up |

## Key Rules / Gotchas Recap
- Seed the generator and use `%` on `mt19937` output (distributions differ between standard libraries).
- Compare after every step, so a failure points at the operation that broke it.
- Count object lifetimes to catch leaks and double destruction.
- Run under `-fsanitize=address,undefined` as well (`make sanitize`).

## Why This Structure Exists
Randomised differential testing against a trusted implementation finds the edge cases nobody thinks to write by hand, and it is the same idea used to test compilers, parsers and security tools.
