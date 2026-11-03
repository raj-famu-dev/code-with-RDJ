// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: iterator categories, the <algorithm>/<numeric> workhorses (sort,
 * find_if, transform, accumulate), the erase-remove idiom (and the trap of
 * calling remove without erase), and std::ranges / views basics (lazy pipelines,
 * and the `dangling` guard for temporaries).
 */
#include <algorithm>
#include <forward_list>
#include <iostream>
#include <iterator>
#include <list>
#include <numeric>
#include <ranges>
#include <string>
#include <type_traits>
#include <vector>

template <typename C>
void show(const char* label, const C& c) {
    std::cout << label << ":";
    for (const auto& x : c) std::cout << " " << x;
    std::cout << "\n";
}

int main() {
    std::cout << "===== SECTION 1: iterator categories =====\n";
    using VecIt = std::vector<int>::iterator;
    using LstIt = std::list<int>::iterator;
    using FwdIt = std::forward_list<int>::iterator;
    std::cout << std::boolalpha;
    std::cout << "vector  : random_access=" << std::random_access_iterator<VecIt> << " bidirectional=" << std::bidirectional_iterator<VecIt> << "\n";
    std::cout << "list    : random_access=" << std::random_access_iterator<LstIt> << " bidirectional=" << std::bidirectional_iterator<LstIt> << "\n";
    std::cout << "fwd_list: bidirectional=" << std::bidirectional_iterator<FwdIt> << " forward=" << std::forward_iterator<FwdIt> << "\n";
    std::cout << "std::sort needs random access, so std::sort on a std::list does not compile; use list.sort().\n";
    std::list<int> lst{3, 1, 2};
    lst.sort();
    show("list.sort()", lst);
    std::vector<int> nums{10, 20, 30, 40};
    std::cout << "std::distance (O(1) for random access) = " << std::distance(nums.begin(), nums.end()) << ", std::next(begin,2) = " << *std::next(nums.begin(), 2) << "\n";

    std::cout << "\n===== SECTION 2: core algorithms =====\n";
    std::vector<int> v{5, 2, 9, 1, 7, 3};
    std::sort(v.begin(), v.end());
    show("sorted", v);
    std::sort(v.begin(), v.end(), std::greater<>{});
    show("sorted descending", v);
    auto it = std::find_if(v.begin(), v.end(), [](int x) { return x % 3 == 0; });
    std::cout << "first multiple of 3: " << *it << " at index " << (it - v.begin()) << "\n";
    std::vector<int> squares(v.size());
    std::transform(v.begin(), v.end(), squares.begin(), [](int x) { return x * x; });
    show("squares", squares);
    std::cout << "accumulate sum = " << std::accumulate(v.begin(), v.end(), 0) << ", product of first 3 = "
              << std::accumulate(v.begin(), v.begin() + 3, 1, std::multiplies<>{}) << "\n";
    std::cout << "count_if even = " << std::count_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; })
              << ", any_of > 8: " << std::any_of(v.begin(), v.end(), [](int x) { return x > 8; }) << "\n";
    std::vector<double> dv{0.5, 0.5};
    std::cout << "accumulate trap: the start value's type decides the result type: accumulate({0.5,0.5}, 0) = "
              << std::accumulate(dv.begin(), dv.end(), 0) << " (int start truncates each partial sum)\n";
    std::cout << "accumulate(dv, 0.0) = " << std::accumulate(dv.begin(), dv.end(), 0.0) << "\n";

    std::cout << "\n===== SECTION 3: erase-remove idiom =====\n";
    std::vector<int> a{1, 2, 3, 2, 4, 2};
    auto newEnd = std::remove(a.begin(), a.end(), 2);
    std::cout << "after std::remove ALONE size is still " << a.size() << " (remove only shuffles kept elements to the front)\n";
    std::cout << "kept range [begin,newEnd): ";
    for (auto i = a.begin(); i != newEnd; ++i) std::cout << *i << " ";
    std::cout << "\n";
    a.erase(newEnd, a.end());
    show("after erase(newEnd, end)", a);
    std::vector<int> b{1, 2, 3, 2, 4, 2};
    b.erase(std::remove(b.begin(), b.end(), 2), b.end());   // the classic one-liner
    show("erase-remove one-liner", b);
    std::vector<int> c{1, 2, 3, 2, 4, 2};
    auto removed = std::erase(c, 2);                         // C++20: does it in one call
    std::cout << "C++20 std::erase removed " << removed << " elements:";
    for (int x : c) std::cout << " " << x;
    std::cout << "\n";
    std::vector<int> d{1, 2, 3, 4, 5, 6};
    std::erase_if(d, [](int x) { return x % 2 == 0; });
    show("erase_if odd kept", d);
    std::cout << "Trap: erasing inside a range-for over the same vector invalidates iterators (undefined behaviour); use erase-remove / erase_if.\n";

    std::cout << "\n===== SECTION 4: std::ranges basics =====\n";
    std::vector<int> data{1, 2, 3, 4, 5, 6, 7, 8};
    int predicateCalls = 0;
    auto pipeline = data | std::views::filter([&predicateCalls](int x) { ++predicateCalls; return x % 2 == 0; })
                         | std::views::transform([](int x) { return x * 10; });
    std::cout << "pipeline built; predicate calls so far = " << predicateCalls << " (views are LAZY: nothing ran yet)\n";
    std::cout << "iterating evens*10:";
    for (int x : pipeline) std::cout << " " << x;
    std::cout << "\n";
    std::cout << "predicate calls after one pass = " << predicateCalls << " (work happens while iterating; data was not copied)\n";
    std::cout << "Rule: do not modify the underlying container while a view over it is alive.\n";
    std::vector<std::string> words{"pear", "fig", "banana"};
    std::ranges::sort(words, [](const std::string& l, const std::string& r) { return l.size() < r.size(); });
    show("ranges::sort by length", words);
    auto pos = std::ranges::find(data, 4);
    std::cout << "ranges::find(data, 4) found at index " << (pos - data.begin()) << "\n";
    auto dangling = std::ranges::find(std::vector<int>{1, 2, 3}, 2);    // temporary container
    std::cout << "find on a TEMPORARY returns std::ranges::dangling (not an iterator): "
              << std::is_same_v<decltype(dangling), std::ranges::dangling> << "\n";
    for (int x : std::views::iota(1, 4)) std::cout << "iota " << x << (x < 3 ? ", " : "\n");
    return 0;
}
