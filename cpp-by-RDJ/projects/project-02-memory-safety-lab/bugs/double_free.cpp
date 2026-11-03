// Tags: #Cpp #Project #MemorySafety #Sanitizers #doublefree | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// DELIBERATE BUG (toy program, own memory only): double free.
// Two pointers refer to the same heap block and both are deleted.
// Educational purpose: see how AddressSanitizer reports "attempting double-free".
// Safe by default: the bug only runs when you pass --trigger.
#include <cstdio>
#include <cstring>

static void discard(int* p) { delete p; }

int main(int argc, char** argv) {
    if (argc < 2 || std::strcmp(argv[1], "--trigger") != 0) {
        std::puts("double_free: nothing dangerous done. Run with --trigger (ideally in a sanitizer build) to run the bug.");
        return 0;
    }
    std::puts("double_free: deleting the same block twice (deliberate bug)");
    int* original = new int(42);
    int* alias = original;  // a second pointer to the SAME block: two "owners"
    discard(original);
    discard(alias);         // BUG: the block was already returned to the allocator
    std::puts("unreachable if the sanitizer stops the program");
    return 0;
}
