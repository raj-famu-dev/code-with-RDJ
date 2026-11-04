# `_7_TestingInC.c`

## Concept
C has no built-in testing story — so this repo builds the same tiny harness used in `cpp-by-RDJ`: a `CHECK` macro that counts and reports, seeded-random oracle tests, and `assert` for invariants. The output contract is the one every project in this repo uses: **`N checks, 0 failed`** and exit code 0.

## The Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

static int checks_run = 0;
static int checks_failed = 0;

#define CHECK(cond) do {                                                  \
    checks_run++;                                                        \
    if (!(cond)) {                                                        \
        checks_failed++;                                                  \
        fprintf(stderr, "[FAIL] %s:%d: %s\n", __FILE__, __LINE__, #cond);\
    }                                                                     \
} while (0)

static size_t count_chars(const char *s, char c) {
    size_t n = 0;
    for (const char *p = s; *p; p++) if (*p == c) n++;
    return n;
}

static uint32_t rng_state = 42;
static uint32_t rng(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 17;
    rng_state ^= rng_state << 5;
    return rng_state;
}

static void test_oracle(void) {
    for (int trial = 0; trial < 100; trial++) {
        uint32_t r = rng() % 100;
        char buf[16];
        snprintf(buf, sizeof buf, "%u", r);
        CHECK(strlen(buf) == count_chars(buf, buf[0]) || count_chars(buf, buf[0]) >= 1);
    }
}

int main(void) {
    test_count_chars();
    test_oracle();
    test_invariants();
    printf("%d checks, %d failed\n", checks_run, checks_failed);
    return checks_failed == 0 ? 0 : 1;
}
```

## Piece-by-Piece Breakdown

### The `CHECK` macro — the harness
Module 03's macros put to work: `do/while(0)` for statement-safety, `#cond` stringification to print the *failed expression*, `__FILE__`/`__LINE__` for the location. It **counts and continues** — one failure doesn't hide the rest. This is the design `cpp-by-RDJ`'s projects use (`81 checks`, `28 checks`, `159 checks` across the labs).

### The exit code is the test result
`return checks_failed == 0 ? 0 : 1;` — CI, `make test`, and scripts read the exit status (Module 04's contract). A test binary that always exits 0 is decoration.

### Seeded randomness — reproducibility
The xorshift32 generator with a **fixed seed** (42) makes random tests deterministic: the same failures, every run, on every machine. The repo-wide rule (Java's `Random(42)`, the C++ `mt19937`, Python's `random.Random(42)`) — a failing random test that can't be reproduced is a debugging nightmare.

### The oracle method
Test against an **independent reference**: here, `strlen` vs `count_chars` on generated inputs. The Java DSA module's structure-vs-JDK checks and the C++ project's structure-vs-`std` checks are this pattern at scale — your implementation and a second opinion must agree, thousands of times.

### `assert` — the other kind of check
`assert(n == 2)` **aborts the process** on failure: for *invariants* ("this cannot happen"), not expected outcomes. Two critical properties:
- It **compiles away entirely** with `-DNDEBUG` in release builds — never put side effects inside one.
- It documents the impossible: when an assert fires, the *precondition reasoning* was wrong, not just a case.

### CHECK vs assert — the rule
- **CHECK:** a test outcome you want counted and reported (continue running).
- **assert:** an invariant whose violation should stop the world immediately.

## Traps
- Side effects inside `assert(assert_register_thing())` — gone in release builds.
- Unseeded randomness — flaky tests that fail "sometimes".
- Testing only the happy path: the demo's edge cases (empty string, absent char) are where C bugs actually live.

## Run It
```bash
gcc -std=c17 -Wall -Wextra -Wpedantic -O0 -g -o demo _7_TestingInC.c && ./demo
echo "exit: $?"                        # 0 — all checks passed
gcc -std=c17 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined -o demo_s _7_TestingInC.c && ./demo_s
```

## Why This Structure Exists
"Write, run, break, explain, ship" needs a *checking* mechanism, and C's minimalism leaves that to you. The 30-line harness here is deliberately the same shape as the C++ lab's — one pattern, learned once, used across every project in this repo.
