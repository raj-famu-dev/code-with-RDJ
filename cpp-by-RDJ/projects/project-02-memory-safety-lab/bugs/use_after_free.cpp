// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// DELIBERATE BUG (toy program, own memory only): use after free.
// A heap block is released with delete[] and then read through the stale pointer.
// Educational purpose: see how AddressSanitizer reports a "heap-use-after-free".
// Safe by default: the bug only runs when you pass --trigger.
#include <cstdio>
#include <cstring>

static void release(int* block) { delete[] block; }  // frees the block; the caller's pointer is NOT cleared

int main(int argc, char** argv) {
    if (argc < 2 || std::strcmp(argv[1], "--trigger") != 0) {
        std::puts("use_after_free: nothing dangerous done. Run with --trigger (ideally in a sanitizer build) to run the bug.");
        return 0;
    }
    std::puts("use_after_free: about to read memory after it was freed (deliberate bug)");
    int* scores = new int[3]{90, 85, 77};
    release(scores);
    // BUG: 'scores' still holds the old address, but the block belongs to the allocator again.
    std::printf("score after free: %d\n", scores[0]);
    return 0;
}
