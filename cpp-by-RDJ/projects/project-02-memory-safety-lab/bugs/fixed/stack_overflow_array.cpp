// Tags: #Cpp #Project #MemorySafety #Sanitizers #stackoverflowarray | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// FIX for bugs/stack_overflow_array.cpp. Use std::array and a range-based for loop: the loop cannot
// run past the end because it asks the container for its own size. at() gives a checked access when an
// index comes from somewhere else.
#include <array>
#include <cstddef>
#include <cstdio>
#include <stdexcept>

int main() {
    std::array<int, 4> readings{};
    for (std::size_t i = 0; i < readings.size(); ++i) readings[i] = static_cast<int>(i) * 10;  // "<" and .size()
    std::printf("readings: %d %d %d %d\n", readings[0], readings[1], readings[2], readings[3]);

    try {
        readings.at(4) = 40;  // one past the end, checked
    } catch (const std::out_of_range&) {
        std::puts("readings.at(4) threw std::out_of_range (a catchable error, not silent stack corruption)");
    }
    return 0;
}
