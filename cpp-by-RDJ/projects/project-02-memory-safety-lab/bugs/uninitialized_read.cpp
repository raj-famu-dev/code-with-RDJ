// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// DELIBERATE BUG (toy program, own memory only): reading memory that was never initialised.
// 'new int[4]' (default-initialisation) gives indeterminate values; the program reads one.
// Educational purpose: this is the bug class that AddressSanitizer and UBSan do NOT report.
// It needs a different tool (MemorySanitizer in clang, or Valgrind memcheck); see the README.
// Safe by default: the bug only runs when you pass --trigger.
#include <cstdio>
#include <cstring>

static int* make_buffer() { return new int[4]; }  // BUG source: 4 ints with indeterminate contents

int main(int argc, char** argv) {
    if (argc < 2 || std::strcmp(argv[1], "--trigger") != 0) {
        std::puts("uninitialized_read: nothing dangerous done. Run with --trigger (ideally in a sanitizer build) to run the bug.");
        return 0;
    }
    std::puts("uninitialized_read: branching on a value that was never set (deliberate bug)");
    int* values = make_buffer();
    if (values[2] > 0) {  // BUG: reads an indeterminate value, and the branch depends on it
        std::puts("the unset value happened to be positive");
    } else {
        std::puts("the unset value happened to be zero or negative");
    }
    delete[] values;
    return 0;
}
