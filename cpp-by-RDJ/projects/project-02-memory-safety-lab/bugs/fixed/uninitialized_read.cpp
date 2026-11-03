// Tags: #Cpp #Project #MemorySafety #Sanitizers #uninitializedread | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// FIX for bugs/uninitialized_read.cpp. Value-initialise: std::vector<int>(4) and 'new int[4]()' give
// zeros; for a local, write 'int x{};'. Rule of thumb: never declare a variable without giving it a value
// unless the very next statement assigns it.
#include <cstdio>
#include <vector>

int main() {
    std::vector<int> values(4);  // four ints, all value-initialised to 0
    if (values[2] > 0) {
        std::puts("positive");
    } else {
        std::puts("values[2] is zero (defined, always the same): zero or negative branch taken");
    }
    int local{};  // braces with nothing inside: zero-initialised
    std::printf("local = %d\n", local);
    return 0;
}
