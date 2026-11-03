// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// DELIBERATE BUG (toy program, own memory only): stack buffer overflow from an off-by-one loop.
// A local array of 4 ints is filled with "i <= count" instead of "i < count", so index 4 is written.
// This is a plain array overrun, NOT a runaway recursion. It is a toy that only touches its own frame.
// Educational purpose: UBSan flags the out-of-bounds index; AddressSanitizer reports "stack-buffer-overflow".
// Safe by default: the bug only runs when you pass --trigger.
#include <cstddef>
#include <cstdio>
#include <cstring>

int main(int argc, char** argv) {
    if (argc < 2 || std::strcmp(argv[1], "--trigger") != 0) {
        std::puts("stack_overflow_array: nothing dangerous done. Run with --trigger (ideally in a sanitizer build) to run the bug.");
        return 0;
    }
    std::puts("stack_overflow_array: writing one element past the end of a 4-int local array (deliberate bug)");
    int readings[4] = {0, 0, 0, 0};
    const std::size_t count = static_cast<std::size_t>(argc) + 2;  // 4 when run with --trigger
    for (std::size_t i = 0; i <= count; ++i) {                      // BUG: <= should be <
        readings[i] = static_cast<int>(i) * 10;
    }
    std::printf("readings[0] = %d\n", readings[0]);
    return 0;
}
