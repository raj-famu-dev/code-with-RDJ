// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _1_HelloWorldAndCompilation
 * Teaches: what a translation unit is, what main() is, how <iostream> gets
 * into your file, and the three build steps g++ performs (preprocess,
 * compile, link). The build steps are explained in the .md; this file shows
 * what the preprocessor produces by inspecting predefined macros.
 */
#include <iostream>   // textual copy-paste of declarations for std::cout etc.
#include <string>

#define SQUARE_BAD(x) x * x           // trap: macros are text substitution
#define SQUARE_OK(x) ((x) * (x))

int add(int a, int b) { return a + b; }  // definition lives in this translation unit

int main() {
    std::cout << "===== SECTION 1: HELLO WORLD =====\n";
    std::cout << "Hello, World!\n";
    std::cout << "Hello from C++" << ' ' << __cplusplus << " (YYYYMM of the language standard)\n";

    std::cout << "\n===== SECTION 2: WHAT THE PREPROCESSOR KNOWS =====\n";
    // __FILE__ would print a path that depends on how you compiled, so only
    // the line number and a fixed macro are shown.
    std::cout << "__LINE__ on this line is " << __LINE__ << '\n';
#ifdef __GNUC__
    std::cout << "Compiled by a GNU-compatible compiler, major version >= 13: "
              << std::boolalpha << (__GNUC__ >= 13) << '\n';
#endif
#ifdef NDEBUG
    std::cout << "NDEBUG is defined (release-style build)\n";
#else
    std::cout << "NDEBUG is not defined (asserts would be active)\n";
#endif

    std::cout << "\n===== SECTION 3: MACROS ARE JUST TEXT (TRAP) =====\n";
    int n = 3;
    // SQUARE_BAD(n + 1) becomes  n + 1 * n + 1  = 3 + 3 + 1 = 7
    std::cout << "SQUARE_BAD(n + 1) = " << SQUARE_BAD(n + 1) << "  (expected 16, got text substitution)\n";
    std::cout << "SQUARE_OK(n + 1)  = " << SQUARE_OK(n + 1) << '\n';
    std::cout << "A real function avoids this: add(n, 1) squared = " << add(n, 1) * add(n, 1) << '\n';

    std::cout << "\n===== SECTION 4: main AND THE EXIT CODE =====\n";
    std::cout << "main returns int; 0 means success to the shell.\n";
    std::cout << "If you omit 'return' in main only, the compiler inserts 'return 0;'.\n";
    return 0;
}
