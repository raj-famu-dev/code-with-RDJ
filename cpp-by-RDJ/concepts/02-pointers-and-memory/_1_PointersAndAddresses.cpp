// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _1_PointersAndAddresses
 * Teaches: address-of (&), dereference (*), pointer arithmetic over an
 * array, pointer comparison/difference, nullptr and null checks.
 * Raw address values are never printed (they change every run under ASLR);
 * only relationships between pointers are shown.
 */
#include <cstddef>
#include <iostream>

int main() {
    std::cout << "===== SECTION 1: ADDRESS-OF AND DEREFERENCE =====\n";
    int x = 10;
    int* p = &x;                 // p holds the address of x
    std::cout << "x = " << x << ", *p = " << *p << '\n';
    *p = 25;                     // writing through the pointer changes x
    std::cout << "after *p = 25, x = " << x << '\n';
    int* q = p;                  // copies the ADDRESS, not the int
    *q += 1;
    std::cout << "p and q point to the same object: " << std::boolalpha << (p == q) << ", x = " << x << '\n';
    int y = x;                   // copies the VALUE
    y = 0;
    std::cout << "copying the value leaves x alone: x = " << x << ", y = " << y << '\n';
    std::cout << "sizeof(int*) = " << sizeof(p) << " bytes (measurement: pointer width on this machine)\n";

    std::cout << "\n===== SECTION 2: POINTER ARITHMETIC OVER AN ARRAY =====\n";
    int arr[5] = {10, 20, 30, 40, 50};
    int* begin = arr;                          // array decays to pointer to element 0
    int* end = arr + 5;                        // one-past-the-end is a legal pointer (never dereference it)
    std::cout << "*(begin + 2) = " << *(begin + 2) << ", begin[2] = " << begin[2] << " (a[i] is *(a + i))\n";
    std::cout << "end - begin = " << (end - begin) << " elements (not bytes)\n";
    int sum = 0;
    for (const int* it = begin; it != end; ++it) sum += *it;   // the iterator idiom STL is built on
    std::cout << "sum via pointer walk = " << sum << '\n';
    int* mid = begin + 2;
    ++mid;
    std::cout << "after ++mid, *mid = " << *mid << " (ptr + 1 moves by sizeof(int) bytes automatically)\n";
    std::cout << "(mid - begin) = " << (mid - begin) << ", begin < mid is " << (begin < mid) << '\n';
    // TRAP (described only): arithmetic that leaves [begin, end] is undefined behaviour
    // even if you never dereference it, e.g. begin - 1 or begin + 6.
    const char* text = "ABC";
    std::cout << "walking a C string: ";
    for (const char* c = text; *c != '\0'; ++c) std::cout << *c << '-';
    std::cout << "end (stops at the null terminator)\n";

    std::cout << "\n===== SECTION 3: nullptr AND NULL CHECKS =====\n";
    int* none = nullptr;                       // "points at nothing"
    std::cout << "none == nullptr: " << (none == nullptr) << '\n';
    if (none) std::cout << "never printed\n";
    else std::cout << "a null pointer is false in a condition\n";
    // TRAP (described only): *none is undefined behaviour (usually a segfault).
    // Fix: check before dereferencing.
    auto safe_read = [](const int* ptr) { return ptr ? *ptr : -1; };
    std::cout << "safe_read(&x) = " << safe_read(&x) << ", safe_read(nullptr) = " << safe_read(nullptr) << '\n';
    // nullptr has its own type (std::nullptr_t); the old macro NULL is just 0 and
    // can pick the wrong overload. Always write nullptr.

    std::cout << "\n===== SECTION 4: const AND POINTERS =====\n";
    const int fixed = 7;
    const int* ptr_to_const = &fixed;          // cannot change *ptr_to_const
    int other = 8;
    ptr_to_const = &other;                     // but the pointer itself can be re-pointed
    int* const const_ptr = &other;             // cannot re-point, can change the target
    *const_ptr = 9;
    std::cout << "read through ptr_to_const: " << *ptr_to_const << ", after write via const_ptr other = " << other << '\n';
    std::cout << "Read right to left: 'const int*' = pointer to const int; 'int* const' = const pointer to int.\n";
    return 0;
}
