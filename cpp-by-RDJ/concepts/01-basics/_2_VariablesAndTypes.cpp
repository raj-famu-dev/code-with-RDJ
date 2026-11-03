// Tags: #Cpp #Basics #VariablesTypes | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _2_VariablesAndTypes
 * Teaches: fixed-width integers, sizeof, signed overflow (undefined) vs
 * unsigned wraparound (defined), auto, const/constexpr, the initialization
 * forms and why braces reject narrowing.
 */
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>

constexpr int square(int x) { return x * x; }

int main() {
    std::cout << "===== SECTION 1: FIXED-WIDTH INTEGERS AND sizeof =====\n";
    std::int8_t   a = 100;
    std::uint8_t  b = 200;
    std::int32_t  c = -2'000'000'000;   // digit separators are legal since C++14
    std::uint64_t d = 18'446'744'073'709'551'615ULL;
    // int8_t is a char type, so cast before printing or you get a character.
    std::cout << "int8_t  " << static_cast<int>(a) << " (sizeof " << sizeof(a) << ")\n";
    std::cout << "uint8_t " << static_cast<int>(b) << " (sizeof " << sizeof(b) << ")\n";
    std::cout << "int32_t " << c << " (sizeof " << sizeof(c) << ")\n";
    std::cout << "uint64_t " << d << " (sizeof " << sizeof(d) << ")\n";
    // These sizes are NOT fixed by the standard; they are what this platform does.
    std::cout << "plain int sizeof = " << sizeof(int) << ", long = " << sizeof(long)
              << ", long long = " << sizeof(long long) << ", pointer = " << sizeof(void*) << " (platform-specific)\n";
    std::cout << "int max = " << std::numeric_limits<int>::max() << '\n';

    std::cout << "\n===== SECTION 2: OVERFLOW: SIGNED vs UNSIGNED =====\n";
    std::uint8_t u = 250;
    for (int i = 0; i < 10; ++i) ++u;   // unsigned wraparound is DEFINED: modulo 256
    std::cout << "uint8_t 250 + 10 wraps to " << static_cast<int>(u) << " (defined behaviour)\n";
    std::uint32_t zero = 0;
    std::cout << "uint32_t 0 - 1 = " << zero - 1u << " (wraps to max)\n";
    // Signed overflow is UNDEFINED behaviour. Never do int_max + 1 in real code.
    // Safe way: check first, or widen to a bigger type.
    int big = std::numeric_limits<int>::max();
    bool would_overflow = big > std::numeric_limits<int>::max() - 1;
    std::cout << "int max + 1 would overflow: " << std::boolalpha << would_overflow
              << " (so we do not compute it)\n";
    std::int64_t widened = static_cast<std::int64_t>(big) + 1;
    std::cout << "widen to int64_t first: " << widened << '\n';
    // Classic trap: mixing signed and unsigned.
    int neg = -1;
    unsigned int one = 1;
    std::cout << "Trap: (-1 < 1u) is " << (neg < static_cast<int>(one) ? "true" : "false")
              << " when both are int, but (-1 < 1u) as written is "
              << ((static_cast<unsigned int>(neg) < one) ? "true" : "false")
              << " because -1 converts to " << static_cast<unsigned int>(neg) << '\n';

    std::cout << "\n===== SECTION 3: auto, const, constexpr =====\n";
    auto i = 42;          // int
    auto f = 3.5;         // double
    auto s = std::string("hi");
    auto lit = "text";    // const char*, NOT std::string (trap)
    std::cout << "auto i=" << i << " f=" << f << " s=" << s << " lit=" << lit << '\n';
    std::cout << "sizeof(s)=" << (sizeof(s) > sizeof(lit) ? "bigger than" : "not bigger than")
              << " sizeof(lit) (a string object is not a pointer)\n";
    const int runtime_const = i * 2;          // value fixed after init, maybe computed at run time
    constexpr int compile_time = square(7);   // must be computable at compile time
    static_assert(compile_time == 49, "checked by the compiler, costs nothing at run time");
    int table[compile_time % 5 + 1] = {};     // constexpr values can size arrays
    std::cout << "const " << runtime_const << ", constexpr " << compile_time
              << ", array length from constexpr " << sizeof(table) / sizeof(table[0]) << '\n';

    std::cout << "\n===== SECTION 4: INITIALIZATION FORMS AND NARROWING =====\n";
    int x1 = 5;        // copy init
    int x2(5);         // direct init
    int x3{5};         // brace init
    int x4 = {5};
    int x5{};          // value-initialised: 0
    std::cout << x1 << ' ' << x2 << ' ' << x3 << ' ' << x4 << ' ' << x5 << '\n';
    double pi = 3.99;
    int truncated = pi;          // compiles silently: fractional part dropped
    std::cout << "int truncated = 3.99 gives " << truncated << " (silent narrowing)\n";
    // int rejected{pi};         // ERROR: narrowing conversion; braces refuse it
    int fixed{static_cast<int>(pi)};
    std::cout << "int fixed{static_cast<int>(pi)} gives " << fixed << " (explicit and visible)\n";
    int uninit_safe{};           // always initialise locals; reading an uninitialised int is UB
    std::cout << "value-initialised local: " << uninit_safe << '\n';
    return 0;
}
