// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _6_ArraysAndVectors
 * Teaches: C arrays and decay to pointers, std::array, std::vector growth
 * (size vs capacity), and bounds: operator[] (unchecked) vs at() (throws).
 * No out-of-bounds access happens here: operator[] misuse is described only.
 */
#include <array>
#include <iostream>
#include <stdexcept>
#include <vector>

// Trap: an array parameter is really a pointer. The classic
// sizeof(arr)/sizeof(arr[0]) trick therefore breaks inside a function
// (g++ even warns about it), so here we only report what sizeof sees.
std::size_t sizeof_seen_by_function(const int* arr) { return sizeof(arr); }
// Fix: take std::array by const& or a span; the length travels with the type.
template <std::size_t N>
std::size_t size_of_std_array(const std::array<int, N>&) { return N; }

int main() {
    std::cout << "===== SECTION 1: C ARRAYS AND DECAY =====\n";
    int c_arr[5] = {10, 20, 30, 40, 50};
    std::cout << "sizeof(c_arr)/sizeof(c_arr[0]) in the same scope = " << sizeof(c_arr) / sizeof(c_arr[0]) << '\n';
    const int* decayed = c_arr;   // array-to-pointer decay
    std::cout << "sizeof(decayed pointer) = " << sizeof(decayed) << " (just a pointer; length is lost)\n";
    std::cout << "inside a function the same array is seen as sizeof = " << sizeof_seen_by_function(c_arr)
              << " (pointer size, so sizeof(arr)/sizeof(arr[0]) no longer gives 5)\n";
    std::cout << "c_arr[2] == *(c_arr + 2): " << std::boolalpha << (c_arr[2] == *(c_arr + 2)) << '\n';

    std::cout << "\n===== SECTION 2: std::array =====\n";
    std::array<int, 5> arr{10, 20, 30, 40, 50};
    std::cout << "size() = " << arr.size() << ", front = " << arr.front() << ", back = " << arr.back() << '\n';
    std::cout << "size_of_std_array(arr) = " << size_of_std_array(arr) << " (length is part of the type)\n";
    std::array<int, 5> copy = arr;   // std::array copies by value; a C array cannot be assigned
    copy[0] = 99;
    std::cout << "copy[0]=" << copy[0] << " arr[0]=" << arr[0] << " (independent)\n";
    std::cout << "arr == copy: " << (arr == copy) << '\n';

    std::cout << "\n===== SECTION 3: vector GROWTH =====\n";
    std::vector<int> v;
    std::size_t last_cap = v.capacity();
    std::cout << "start: size=" << v.size() << " capacity=" << last_cap << '\n';
    for (int i = 1; i <= 20; ++i) {
        v.push_back(i);
        if (v.capacity() != last_cap) {
            last_cap = v.capacity();
            std::cout << "  push #" << i << " reallocated: capacity now " << last_cap << '\n';
        }
    }
    // The growth factor (here printed from a real run) is up to the library
    // implementation; the standard only promises amortised O(1) push_back.
    std::vector<int> reserved;
    reserved.reserve(20);
    for (int i = 0; i < 20; ++i) reserved.push_back(i);
    std::cout << "with reserve(20): size=" << reserved.size() << " capacity=" << reserved.capacity()
              << " (no reallocation while filling)\n";
    v.shrink_to_fit();
    std::cout << "after shrink_to_fit (a non-binding request): capacity=" << v.capacity() << '\n';
    std::vector<int> sized(3, 7);   // trap: parens mean (count, value); braces mean elements
    std::vector<int> listed{3, 7};
    std::cout << "vector<int>(3, 7) has " << sized.size() << " elements; vector<int>{3, 7} has " << listed.size() << '\n';

    std::cout << "\n===== SECTION 4: BOUNDS: operator[] vs at() =====\n";
    std::vector<int> small{1, 2, 3};
    std::cout << "small[2] = " << small[2] << " (operator[] does no checking; small[3] would be undefined behaviour)\n";
    try {
        std::cout << small.at(3) << '\n';   // checked: throws instead of reading garbage
    } catch (const std::out_of_range& e) {
        std::cout << "small.at(3) threw std::out_of_range (message text is library-specific)\n";
    }
    std::cout << "Rule: use at() or a checked loop when the index comes from outside; use range-for when you can.\n";
    return 0;
}
