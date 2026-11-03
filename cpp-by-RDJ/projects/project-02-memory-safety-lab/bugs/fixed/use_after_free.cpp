// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// FIX for bugs/use_after_free.cpp. The block is owned by a std::vector (RAII): it cannot be freed
// while we can still reach it, and it is released automatically when the vector goes out of scope.
// If you truly need a pointer-like owner, std::unique_ptr<int[]> does the same job.
#include <cstdio>
#include <memory>
#include <vector>

int main() {
    std::vector<int> scores{90, 85, 77};
    std::printf("score: %d (owner: std::vector, freed automatically at end of scope)\n", scores[0]);

    auto owned = std::make_unique<int[]>(3);  // alternative owner: unique_ptr to an array
    owned[0] = 90;
    std::printf("score via unique_ptr: %d\n", owned[0]);
    return 0;
}
