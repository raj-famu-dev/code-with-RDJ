// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _2_ReferencesVsPointers
 * Teaches: a reference is a permanent alias that cannot be null and cannot
 * be reseated; a pointer can be null and can be re-pointed. Shows when to
 * use each, with std::optional and reference_wrapper as extras.
 */
#include <functional>
#include <iostream>
#include <optional>
#include <string>
#include <vector>

void bump_ref(int& x) { ++x; }
void bump_ptr(int* x) { if (x) ++*x; }       // pointer API must handle null

// Returns a pointer because "not found" is a valid answer.
const std::string* find_name(const std::vector<std::string>& names, const std::string& wanted) {
    for (const auto& n : names) if (n == wanted) return &n;
    return nullptr;
}

int main() {
    std::cout << "===== SECTION 1: RULES OF A REFERENCE =====\n";
    int a = 1;
    int& r = a;                  // MUST be initialised; it is another name for a
    r = 5;
    std::cout << "a = " << a << " after r = 5 (r is a, not a copy)\n";
    std::cout << "&r == &a: " << std::boolalpha << (&r == &a) << " (taking the address of a reference gives the target's address)\n";
    // int& bad;                 // ERROR: references must be initialised
    // int& null = nullptr;      // ERROR: no such thing as a null reference
    const int& tmp = 3 + 4;      // a const reference may bind to a temporary and extends its life
    std::cout << "const int& bound to a temporary: " << tmp << '\n';

    std::cout << "\n===== SECTION 2: RESEATING (THE BIG DIFFERENCE) =====\n";
    int b = 100;
    int* p = &a;
    p = &b;                      // pointer re-pointed to a different object
    std::cout << "pointer reseated: *p = " << *p << '\n';
    r = b;                       // TRAP: this does NOT make r refer to b; it copies b's value into a
    std::cout << "r = b copied the value: a = " << a << ", still aliasing a: " << (&r == &a) << '\n';
    b = 7;
    std::cout << "changing b to 7 leaves a = " << a << " (r never moved)\n";

    std::cout << "\n===== SECTION 3: WHEN TO USE WHICH =====\n";
    int n = 0;
    bump_ref(n);
    bump_ptr(&n);
    bump_ptr(nullptr);           // safe only because the function checks
    std::cout << "n = " << n << " (reference param: caller cannot pass 'nothing')\n";
    std::vector<std::string> names{"ada", "linus"};
    if (const std::string* hit = find_name(names, "linus")) std::cout << "found: " << *hit << '\n';
    if (!find_name(names, "grace")) std::cout << "grace: nullptr means not found\n";
    // Modern alternative: optional says "maybe a value" without pointers. Here it holds a COPY.
    auto find_index = [&](const std::string& w) -> std::optional<std::size_t> {
        for (std::size_t i = 0; i < names.size(); ++i) if (names[i] == w) return i;
        return std::nullopt;
    };
    std::cout << "find_index(\"linus\") = " << find_index("linus").value_or(999)
              << ", find_index(\"x\") = " << find_index("x").value_or(999) << '\n';
    std::cout << "Rule of thumb: reference = required, non-null, same object for life; pointer = optional or reseatable.\n";

    std::cout << "\n===== SECTION 4: REFERENCES IN CONTAINERS =====\n";
    // std::vector<int&> does not compile: references are not assignable objects.
    int u = 1, v = 2;
    std::vector<std::reference_wrapper<int>> refs{u, v};   // a reseatable, copyable reference
    for (int& x : refs) x *= 10;
    std::cout << "u = " << u << ", v = " << v << " (modified through reference_wrapper)\n";
    int w = 3;
    refs[0] = w;                                           // reseats the wrapper (unlike a raw reference)
    refs[0].get() += 1;
    std::cout << "after reseat: u = " << u << ", w = " << w << '\n';

    std::cout << "\n===== SECTION 5: DANGLING REFERENCE TRAP =====\n";
    // Returning a reference to a local is a classic bug; described, not executed:
    //   int& bad() { int local = 1; return local; }   // g++ warns; using it is undefined behaviour
    // Fix: return by value.
    auto good = [] { int local = 1; return local; };
    std::cout << "returning by value is safe: " << good() << '\n';
    return 0;
}
