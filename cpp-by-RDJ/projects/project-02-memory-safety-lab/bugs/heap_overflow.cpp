// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// DELIBERATE BUG (toy program, own memory only): heap buffer overflow.
// A loop writes 12 bytes into an 8-byte heap block (the classic "forgot the buffer's size" mistake).
// Educational purpose: see how AddressSanitizer reports a "heap-buffer-overflow".
// Safe by default: the bug only runs when you pass --trigger.
#include <cstddef>
#include <cstdio>
#include <cstring>

int main(int argc, char** argv) {
    if (argc < 2 || std::strcmp(argv[1], "--trigger") != 0) {
        std::puts("heap_overflow: nothing dangerous done. Run with --trigger (ideally in a sanitizer build) to run the bug.");
        return 0;
    }
    std::puts("heap_overflow: about to write past the end of an 8-byte heap block (deliberate bug)");
    const std::size_t capacity = 8;
    const std::size_t wanted = capacity + static_cast<std::size_t>(argc) + 2;  // 12 when run with --trigger
    char* name = new char[capacity];
    for (std::size_t i = 0; i < wanted; ++i) {
        name[i] = 'A';  // BUG: nothing stops i from reaching capacity and beyond
    }
    std::printf("first byte: %c\n", name[0]);
    delete[] name;
    return 0;
}
