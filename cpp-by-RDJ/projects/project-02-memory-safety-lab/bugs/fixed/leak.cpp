// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// FIX for bugs/leak.cpp. The settings live in a std::vector (or std::unique_ptr): whoever owns the
// object frees it automatically when it goes out of scope, on every path including exceptions.
#include <cstdio>
#include <vector>

static int load_config(int value) {
    std::vector<int> settings(10);  // owns its memory; freed when the function returns
    settings[0] = value;
    return settings[0];
}

int main() {
    int total = 0;
    for (int i = 0; i < 3; ++i) total += load_config(i);
    std::printf("total: %d (no leak: every block was released by its owner)\n", total);
    return 0;
}
