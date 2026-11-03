// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _9_HeadersAndNamespaces
 * Teaches: declaration vs definition, include guards, the One Definition
 * Rule (ODR), and namespaces. A real project splits code across .h and
 * .cpp files; this single file SIMULATES a header with clearly marked
 * regions so it stays one translation unit. The multi-file build and
 * Makefile are explained in the .md only.
 */
#include <iostream>
#include <string>

// ----------------------------------------------------------------------
// ---- pretend this region is "shapes.h" -------------------------------
// ----------------------------------------------------------------------
#ifndef SHAPES_H            // include guard: the second inclusion becomes empty
#define SHAPES_H

namespace shapes {

constexpr double kPi = 3.14159;            // fine in a header: constexpr implies internal linkage for namespace-scope const

double area_of_circle(double r);            // DECLARATION only: tells the compiler the signature
inline int twice(int x) { return 2 * x; }   // inline DEFINITION is allowed in headers (ODR exception)

class Counter {                             // class definitions may appear in many translation units
public:
    void bump();                            // declared here, defined in the .cpp region
    int value() const { return value_; }    // defined inside the class => implicitly inline
private:
    int value_ = 0;
};

}  // namespace shapes

#endif  // SHAPES_H

// Simulate a SECOND #include "shapes.h" (for example via two other headers).
// The guard is already defined, so everything up to #endif is skipped.
// Without the guard, 'class Counter' would be defined twice: a compile error.
#ifndef SHAPES_H
#define SHAPES_H
namespace shapes { class Counter { int would_be_a_redefinition; }; }
#endif
// ----------------------------------------------------------------------
// ---- end of simulated "shapes.h" -------------------------------------
// ----------------------------------------------------------------------

// ----------------------------------------------------------------------
// ---- pretend this region is "shapes.cpp" ------------------------------
// ----------------------------------------------------------------------
namespace shapes {
double area_of_circle(double r) { return kPi * r * r; }   // the ONE definition of this function
void Counter::bump() { ++value_; }
}  // namespace shapes

// ----------------------------------------------------------------------
// ---- pretend this region is "other_lib.h" ----------------------------
// ----------------------------------------------------------------------
namespace mylib {
std::string name() { return "mylib::name"; }
namespace detail {                          // convention: "internal, do not use"
std::string secret() { return "mylib::detail::secret"; }
}  // namespace detail
}  // namespace mylib

namespace otherlib {
std::string name() { return "otherlib::name"; }   // same name, different namespace: no clash
}  // namespace otherlib

// An anonymous namespace gives internal linkage: invisible to other .cpp files.
namespace {
int helper_only_here() { return 42; }
}  // namespace

// ----------------------------------------------------------------------
// ---- main.cpp ---------------------------------------------------------
// ----------------------------------------------------------------------
int main() {
    std::cout << "===== SECTION 1: DECLARATION VS DEFINITION =====\n";
    std::cout << "area_of_circle(2) = " << shapes::area_of_circle(2.0) << " (declared in 'header', defined once in 'cpp')\n";
    std::cout << "twice(21) = " << shapes::twice(21) << " (inline: definition may repeat in every file)\n";
    std::cout << "A declaration says 'this exists'; a definition creates it. Many declarations are OK, exactly one definition.\n";

    std::cout << "\n===== SECTION 2: INCLUDE GUARDS AND ODR =====\n";
    shapes::Counter c;
    c.bump();
    c.bump();
    std::cout << "Counter value = " << c.value() << '\n';
    std::cout << "Guard macro SHAPES_H defined: "
#ifdef SHAPES_H
              << "yes"
#else
              << "no"
#endif
              << '\n';
    // TRAP (described, cannot be shown in one file): defining a non-inline
    // function or a non-const global variable in a header and including it
    // from two .cpp files gives "multiple definition" errors at LINK time,
    // even though every .cpp compiles fine. Fix: declare in .h, define in
    // one .cpp, or mark it inline/constexpr.

    std::cout << "\n===== SECTION 3: NAMESPACES =====\n";
    std::cout << mylib::name() << " vs " << otherlib::name() << '\n';
    std::cout << mylib::detail::secret() << '\n';
    {
        using mylib::name;                  // brings ONE name in, scoped to this block
        std::cout << "using-declaration: " << name() << '\n';
    }
    namespace ml = mylib;                   // alias
    std::cout << "alias: " << ml::name() << '\n';
    std::cout << "anonymous namespace helper = " << helper_only_here() << '\n';
    // Trap: 'using namespace std;' in a HEADER pollutes every file that includes it
    // and can silently change which overload is called. Avoid it in headers; prefer std:: everywhere.
    return 0;
}
