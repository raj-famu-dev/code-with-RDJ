// Tags: #Cpp #Project #MemorySafety #Sanitizers #leak | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// DELIBERATE BUG (toy program, own memory only): memory leak.
// load_config() allocates a block with new[] and returns without delete[]; the pointer is lost.
// Educational purpose: see how LeakSanitizer (part of AddressSanitizer on Linux) reports leaks at exit.
// Safe by default: the bug only runs when you pass --trigger.
#include <cstdio>
#include <cstring>

static int load_config(int value) {
    int* settings = new int[10];  // BUG: never deleted
    settings[0] = value;
    return settings[0];           // the pointer goes out of scope here: the block is unreachable forever
}

int main(int argc, char** argv) {
    if (argc < 2 || std::strcmp(argv[1], "--trigger") != 0) {
        std::puts("leak: nothing dangerous done. Run with --trigger (ideally in a sanitizer build) to run the bug.");
        return 0;
    }
    std::puts("leak: calling load_config() three times without ever freeing (deliberate bug)");
    int total = 0;
    for (int i = 0; i < 3; ++i) total += load_config(i);
    std::printf("total: %d\n", total);
    return 0;
}
