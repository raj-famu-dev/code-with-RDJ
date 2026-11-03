// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * std::string_view and std::span (non-owning views), the dangling-view trap,
 * and a std::ranges / std::views pipeline that is lazy, like a Java stream.
 */
#include <algorithm>
#include <iostream>
#include <numeric>
#include <ranges>
#include <span>
#include <string>
#include <string_view>
#include <vector>

// Takes ANY contiguous string without copying.
std::size_t count_vowels(std::string_view text) {
    return static_cast<std::size_t>(std::count_if(text.begin(), text.end(), [](char c) {
        return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u';
    }));
}

// Takes a vector, array, or C array without copying.
int sum_span(std::span<const int> values) {
    return std::accumulate(values.begin(), values.end(), 0);
}

void zero_first_half(std::span<int> values) {
    for (std::size_t i = 0; i < values.size() / 2; ++i) values[i] = 0;
}

std::string_view dangling_view() {
    std::string local = "temporary text long enough to live on the heap";
    return std::string_view(local);  // BUG pattern: view outlives its owner (not called in the default path)
}

int main(int argc, char** argv) {
    // ===== SECTION 1: string_view =====
    std::cout << "===== SECTION 1: string_view =====\n";
    std::string owned = "education is the key";
    const char* c_str = "queue and aeiou";
    std::cout << "vowels in std::string: " << count_vowels(owned) << "\n";
    std::cout << "vowels in C string:    " << count_vowels(c_str) << "\n";
    std::cout << "vowels in literal:     " << count_vowels("rhythm") << "\n";
    std::string_view sv = owned;
    std::string_view word = sv.substr(0, 9);  // O(1): only a pointer and a length
    std::cout << "substr view: \"" << word << "\" size=" << word.size() << "\n";
    sv.remove_prefix(10);
    std::cout << "after remove_prefix(10): \"" << sv << "\"\n";
    std::cout << "starts_with(\"is\")? " << std::boolalpha << std::string_view("is the key").starts_with("is") << "\n";
    std::cout << "TRAP: a string_view is NOT null-terminated, so never pass sv.data() to a C function expecting a C string.\n";
    std::cout << "TRAP: never return a view of a local (see dangling_view), and never keep one past its owner's life.\n";
    std::string_view v_dead = "safe literal";
    std::cout << "A view of a string literal is safe, literals live for the whole program: " << v_dead << "\n";

    // ===== SECTION 2: std::span =====
    std::cout << "===== SECTION 2: std::span =====\n";
    std::vector<int> vec = {1, 2, 3, 4, 5, 6};
    int plain[] = {10, 20, 30};
    std::cout << "sum_span(vector) = " << sum_span(vec) << "\n";
    std::cout << "sum_span(C array) = " << sum_span(plain) << "\n";
    std::cout << "sum of the middle two via subspan = " << sum_span(std::span<const int>(vec).subspan(2, 2)) << "\n";
    zero_first_half(vec);  // span writes through to the vector
    std::cout << "after zero_first_half(vec):";
    for (int x : vec) std::cout << " " << x;
    std::cout << "\n";
    std::cout << "TRAP: push_back on the vector can reallocate and leave an existing span pointing at freed memory.\n";

    // ===== SECTION 3: ranges VIEWS PIPELINE =====
    std::cout << "===== SECTION 3: ranges VIEWS PIPELINE =====\n";
    std::vector<int> nums = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    auto pipeline = nums
        | std::views::filter([](int n) { return n % 2 == 0; })
        | std::views::transform([](int n) { return n * n; });
    std::cout << "squares of evens:";
    for (int n : pipeline) std::cout << " " << n;
    std::cout << "\n";
    std::cout << "take(3) of reversed:";
    for (int n : nums | std::views::reverse | std::views::take(3)) std::cout << " " << n;
    std::cout << "\n";
    std::cout << "iota(1,6) = ";
    for (int n : std::views::iota(1, 6)) std::cout << n << " ";
    std::cout << "\n";
    std::vector<int> collected;
    for (int n : pipeline) collected.push_back(n);  // C++20 has no ranges::to; collect manually
    std::cout << "collected into a vector of size " << collected.size() << "\n";
    std::vector<int> unsorted = {5, 2, 9, 1};
    std::ranges::sort(unsorted);
    std::cout << "ranges::sort:";
    for (int n : unsorted) std::cout << " " << n;
    std::cout << "\n";

    // ===== SECTION 4: LAZINESS =====
    std::cout << "===== SECTION 4: LAZINESS =====\n";
    int calls = 0;
    auto lazy = nums | std::views::transform([&calls](int n) { ++calls; return n * 10; });
    std::cout << "built the view; transform calls so far: " << calls << "\n";
    auto it = lazy.begin();
    std::cout << "first element " << *it << "; calls so far: " << calls << "\n";
    int taken = 0;
    for (int n : lazy | std::views::take(3)) { taken += n; }
    std::cout << "iterated 3 elements (sum " << taken << "); total calls: " << calls << " (the other 7 never ran)\n";
    std::cout << "Infinite source is fine when lazy, first 5 even squares from iota(1):";
    for (int n : std::views::iota(1) | std::views::filter([](int k) { return k % 2 == 0; })
                     | std::views::transform([](int k) { return k * k; }) | std::views::take(5))
        std::cout << " " << n;
    std::cout << "\n";
    std::cout << "TRAP: the view holds a reference to nums and the lambdas; changing nums changes what the view yields.\n";
    nums[0] = 100;
    std::cout << "after nums[0]=100, *lazy.begin() = " << *lazy.begin() << "\n";

    // ===== SECTION 5: THE DANGLING VIEW BUG (opt-in) =====
    std::cout << "===== SECTION 5: THE DANGLING VIEW BUG (opt-in) =====\n";
    if (argc > 1 && std::string_view(argv[1]) == "--dangling") {
        std::string_view bad = dangling_view();
        std::cout << "reading a dangling view (undefined behaviour, sanitizers will flag it): " << bad << "\n";
    } else {
        std::cout << "skipped; run with --dangling to read a view whose string was destroyed (use -fsanitize=address).\n";
        std::string_view fixed = "returned views must refer to storage that outlives the call";
        std::cout << "fix: return std::string by value, or a view of a longer-lived owner: " << fixed.substr(0, 20) << "...\n";
    }
    return 0;
}
