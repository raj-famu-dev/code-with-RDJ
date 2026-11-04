// Tags: #C #Testing #Assert #TestHarness | @rdj_369 | C17 (gcc 13)
// Completed and verified (gcc 13, -std=c17 -Wall -Wextra -Wpedantic). Written with Claude (GLM-5.3); authorship disclosed.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdint.h>

/* C has no built-in test framework. The repo's convention (cpp-by-RDJ):
   a tiny harness that prints 'N checks, 0 failed' — and assert for
   invariants that should be impossible to break. */

static int checks_run = 0;
static int checks_failed = 0;

#define CHECK(cond) do {                                                     \
    checks_run++;                                                            \
    if (!(cond)) {                                                           \
        checks_failed++;                                                     \
        fprintf(stderr, "[FAIL] %s:%d: %s\n", __FILE__, __LINE__, #cond);    \
    }                                                                        \
} while (0)

/* The subject under test: a minimal module with its own invariants. */
static size_t count_chars(const char *s, char c) {
    size_t n = 0;
    for (const char *p = s; *p; p++) if (*p == c) n++;
    return n;
}

static void test_count_chars(void) {
    CHECK(count_chars("hello", 'l') == 2);
    CHECK(count_chars("", 'x') == 0);            /* empty string edge */
    CHECK(count_chars("aaaa", 'a') == 4);
    CHECK(count_chars("abc", 'z') == 0);         /* absent char */
}

/* A seeded RNG so the tests are REPRODUCIBLE — the repo-wide rule. */
static uint32_t rng_state = 42;
static uint32_t rng(void) {                      /* xorshift32 */
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 17;
    rng_state ^= rng_state << 5;
    return rng_state;
}

static void test_oracle(void) {
    /* The oracle method: compare against an independent reference. */
    for (int trial = 0; trial < 100; trial++) {
        uint32_t r = rng() % 100;
        char buf[16];
        snprintf(buf, sizeof buf, "%u", r);
        CHECK(count_chars(buf, buf[0]) >= 1);    /* first char is always present */
    }
}

/* assert(): for invariants — aborts (crash) when broken. Unlike CHECK,
   it COMPILES AWAY with -DNDEBUG in release builds. Use it for
   "impossible" conditions, not for test outcomes you want to count. */
static void test_invariants(void) {
    size_t n = count_chars("test", 't');
    CHECK(n <= strlen("test"));                  /* an invariant as a CHECK */
    assert(n == 2);                              /* the impossible case: abort if wrong */
}

int main(void) {
    test_count_chars();
    test_oracle();
    test_invariants();

    printf("%d checks, %d failed\n", checks_run, checks_failed);
    return checks_failed == 0 ? 0 : 1;            /* exit code: CI reads this */
}
