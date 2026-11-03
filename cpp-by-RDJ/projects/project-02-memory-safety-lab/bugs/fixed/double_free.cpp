// Tags: #Cpp #Project #MemorySafety #Sanitizers #doublefree | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// FIX for bugs/double_free.cpp. std::unique_ptr has exactly ONE owner and deletes exactly once.
// Copying it is a compile error; handing ownership over needs an explicit std::move, after which the
// old pointer is null (and deleting nothing is always safe). std::shared_ptr is for genuinely shared ownership.
#include <cstdio>
#include <memory>
#include <utility>

int main() {
    auto original = std::make_unique<int>(42);
    // auto alias = original;                    // would NOT compile: unique ownership cannot be copied
    auto new_owner = std::move(original);        // ownership moves; 'original' is now null
    std::printf("new_owner holds %d, original is %s\n", *new_owner, original ? "set" : "null");

    auto shared = std::make_shared<int>(7);      // shared ownership: a reference count decides when to delete
    auto another = shared;
    std::printf("shared value %d, owners: %ld\n", *another, shared.use_count());
    return 0;
}
