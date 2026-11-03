// Tags: #Cpp #Project #MemorySafety #Sanitizers #LabCheck | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// Hand-rolled test runner for the memory safety lab (no framework). It launches the lab's OWN toy programs
// (built into ./bin by the Makefile) through the shell, captures stdout+stderr, and CHECKs the sanitizer verdict:
//   - every buggy program must be caught with the expected report when run with --trigger,
//   - run without --trigger it must do nothing dangerous and exit 0,
//   - every fixed program must exit 0 with no sanitizer text,
//   - uninitialized_read must produce NO ASan/UBSan report (a documented limitation of those two tools).
// Exit code: 0 if every CHECK passed, 1 otherwise.
#include <cstdio>
#include <string>

static int g_checks = 0;
static int g_failures = 0;

#define CHECK(cond)                                                       \
    do {                                                                  \
        ++g_checks;                                                       \
        if (!(cond)) {                                                    \
            ++g_failures;                                                 \
            std::printf("  FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); \
        }                                                                 \
    } while (0)

struct Result {
    std::string output;  // stdout + stderr, merged
    int exit_code = -1;
};

// Runs a shell command (one of our own binaries) and returns its merged output and exit status.
static Result run(const std::string& command) {
    Result r;
    const std::string full = "sh -c '" + command + " 2>&1; echo EXIT:$?'";
    FILE* pipe = popen(full.c_str(), "r");
    if (pipe == nullptr) return r;
    char buffer[512];
    while (std::fgets(buffer, sizeof buffer, pipe) != nullptr) r.output += buffer;
    pclose(pipe);
    const std::size_t pos = r.output.rfind("EXIT:");
    if (pos != std::string::npos) {
        r.exit_code = std::stoi(r.output.substr(pos + 5));
        r.output.erase(pos);
    }
    return r;
}

static bool has(const Result& r, const char* text) { return r.output.find(text) != std::string::npos; }

struct Expect {
    const char* name;
    const char* asan_text;  // text the sanitizer must print for the buggy program ("" = must print nothing)
};

int main() {
    const Expect cases[] = {
        {"use_after_free", "AddressSanitizer: heap-use-after-free"},
        {"heap_overflow", "AddressSanitizer: heap-buffer-overflow"},
        {"leak", "LeakSanitizer: detected memory leaks"},
        {"double_free", "AddressSanitizer: attempting double-free"},
        {"stack_overflow_array", "AddressSanitizer: stack-buffer-overflow"},
        {"uninitialized_read", ""},
    };

    for (const Expect& c : cases) {
        const std::string name = c.name;
        const int before = g_failures;

        const Result safe = run("./bin/bugs/" + name);
        CHECK(safe.exit_code == 0);
        CHECK(has(safe, "nothing dangerous done"));
        CHECK(!has(safe, "Sanitizer"));

        const Result bug = run("./bin/bugs/" + name + " --trigger");
        if (std::string(c.asan_text).empty()) {
            CHECK(bug.exit_code == 0);  // runs to the end: ASan/UBSan do not see this bug
            CHECK(!has(bug, "Sanitizer"));
            CHECK(!has(bug, "runtime error"));
        } else {
            CHECK(bug.exit_code != 0);
            CHECK(has(bug, c.asan_text));
        }
        if (name == "stack_overflow_array") CHECK(has(bug, "runtime error: index 4 out of bounds for type 'int [4]'"));

        const Result fixed = run("./bin/fixed/" + name);
        CHECK(fixed.exit_code == 0);
        CHECK(!has(fixed, "Sanitizer"));
        CHECK(!has(fixed, "runtime error"));

        std::printf("[%s] %s (buggy exit code %d, fixed exit code %d)\n", g_failures == before ? "PASS" : "FAIL", c.name, bug.exit_code,
                    fixed.exit_code);
    }
    std::printf("%d checks, %d failed\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
