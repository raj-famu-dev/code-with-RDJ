// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// FIX for bugs/heap_overflow.cpp. std::string knows its own size and grows as needed, so there is no
// fixed-size block to overrun. When a fixed size is a hard limit, check it explicitly (or use .at(),
// which throws std::out_of_range instead of corrupting memory).
#include <cstddef>
#include <cstdio>
#include <stdexcept>
#include <string>

int main() {
    const std::size_t wanted = 12;
    std::string name;
    for (std::size_t i = 0; i < wanted; ++i) name.push_back('A');  // grows automatically
    std::printf("string of %zu characters, first byte: %c\n", name.size(), name[0]);

    try {
        (void)name.at(wanted);  // one past the end: a checked access throws instead of overflowing
    } catch (const std::out_of_range&) {
        std::puts("name.at(12) threw std::out_of_range (a catchable error, not silent memory damage)");
    }
    return 0;
}
