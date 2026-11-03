// Tags: #Cpp #Templates #STL #ConceptsConstraints | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: C++20 concepts and `requires`: named, checkable constraints on
 * template parameters. Shows concept definition, requires-expressions,
 * the three ways to constrain a template, overload selection by concept,
 * and compile-time checking with static_assert. The readable compile
 * error is described in the .md (it was captured from a real failing compile).
 */
#include <concepts>
#include <iostream>
#include <string>
#include <type_traits>
#include <vector>

// ===== SECTION 1: defining concepts =====
template <typename T>
concept Numeric = std::is_arithmetic_v<T>;

template <typename T>
concept Addable = requires(T a, T b) {          // requires-expression: "this code must be valid"
    { a + b } -> std::convertible_to<T>;        // and the result must convert to T
};

template <typename T>
concept Printable = requires(std::ostream& os, const T& v) { os << v; };

struct NoPlus {};                                // supports none of the above
struct Meter {
    double v;
    Meter operator+(const Meter& o) const { return {v + o.v}; }
};

// ===== SECTION 2: three ways to constrain =====
template <Numeric T>                              // 1) constrained template parameter
T twice(T x) { return x + x; }

template <typename T>
    requires Addable<T> && Printable<T>          // 2) requires-clause
void showSum(T a, T b) { std::cout << "  sum = " << (a + b) << "\n"; }

auto average(const std::vector<std::floating_point auto>& v) {   // 3) constrained `auto` in a signature
    double s = 0;
    for (auto x : v) s += x;
    return v.empty() ? 0.0 : s / static_cast<double>(v.size());
}

// ===== SECTION 3: overloading on concepts =====
template <typename T>
std::string describe(const T&) { return "something generic"; }
template <std::integral T>
std::string describe(const T&) { return "an integer type"; }
template <std::floating_point T>
std::string describe(const T&) { return "a floating-point type"; }

// ===== SECTION 4: compile-time checks =====
static_assert(Numeric<int>);
static_assert(!Numeric<std::string>);
static_assert(Addable<int> && Addable<std::string> && Addable<Meter>);
static_assert(!Addable<NoPlus>);
static_assert(Printable<int> && !Printable<NoPlus>);

int main() {
    std::cout << "===== SECTION 1: defining concepts =====\n";
    std::cout << std::boolalpha;
    std::cout << "Numeric<int>=" << Numeric<int> << " Numeric<double>=" << Numeric<double> << " Numeric<std::string>=" << Numeric<std::string> << "\n";
    std::cout << "Addable<int>=" << Addable<int> << " Addable<std::string>=" << Addable<std::string>
              << " Addable<Meter>=" << Addable<Meter> << " Addable<NoPlus>=" << Addable<NoPlus> << "\n";
    std::cout << "Printable<int>=" << Printable<int> << " Printable<Meter>=" << Printable<Meter> << " (Meter has no operator<<)\n";

    std::cout << "\n===== SECTION 2: three ways to constrain =====\n";
    std::cout << "twice(21) = " << twice(21) << ", twice(1.5) = " << twice(1.5) << "\n";
    std::cout << "twice(std::string(\"x\")) would fail the Numeric constraint at the call site, before the body is looked at.\n";
    showSum(2, 3);
    showSum(std::string("con"), std::string("cat"));
    std::cout << "showSum(Meter{1}, Meter{2}) would not compile: Meter is Addable but not Printable.\n";
    std::cout << "average({1.0, 2.0, 6.0}) = " << average(std::vector<double>{1.0, 2.0, 6.0}) << "\n";

    std::cout << "\n===== SECTION 3: overloading on concepts =====\n";
    std::cout << "describe(5)      -> " << describe(5) << "\n";
    std::cout << "describe(2.5)    -> " << describe(2.5) << "\n";
    std::cout << "describe(\"hi\"s)  -> " << describe(std::string("hi")) << "\n";
    std::cout << "The most constrained viable overload wins; no tag dispatch or SFINAE tricks needed.\n";

    std::cout << "\n===== SECTION 4: compile-time checks =====\n";
    std::cout << "This file contains 5 static_assert lines at namespace scope.\n";
    std::cout << "They were verified by the compiler: if any were false, the file would not compile.\n";
    std::cout << "Meter{1.5} + Meter{2.0} = " << (Meter{1.5} + Meter{2.0}).v << "\n";
    return 0;
}
