// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * constexpr functions (run at compile time OR run time), consteval (compile
 * time only), static_assert (compile-time checks), and a lookup table that is
 * built entirely by the compiler.
 */
#include <array>
#include <cstddef>
#include <cstdint>
#include <iostream>

// ---- constexpr: may run at compile time when arguments are constants ----
constexpr std::uint64_t factorial(unsigned n) {
    std::uint64_t result = 1;
    for (unsigned i = 2; i <= n; ++i) result *= i;
    return result;
}

constexpr bool is_prime(unsigned n) {
    if (n < 2) return false;
    for (unsigned d = 2; d * d <= n; ++d)
        if (n % d == 0) return false;
    return true;
}

// ---- consteval: MUST be evaluated at compile time ----
consteval unsigned square_ct(unsigned x) { return x * x; }

// ---- a compile-time table: squares 0..9 ----
constexpr std::array<unsigned, 10> make_squares() {
    std::array<unsigned, 10> t{};
    for (std::size_t i = 0; i < t.size(); ++i) t[i] = static_cast<unsigned>(i * i);
    return t;
}
constexpr auto kSquares = make_squares();

// ---- compile-time table of primes below 50 (count first, then fill) ----
constexpr std::size_t count_primes(unsigned limit) {
    std::size_t c = 0;
    for (unsigned i = 0; i < limit; ++i)
        if (is_prime(i)) ++c;
    return c;
}
template <unsigned Limit>
constexpr auto make_primes() {
    std::array<unsigned, count_primes(Limit)> out{};
    std::size_t k = 0;
    for (unsigned i = 0; i < Limit; ++i)
        if (is_prime(i)) out[k++] = i;
    return out;
}
constexpr auto kPrimes = make_primes<50>();

// ---- compile-time CRC-8-like checksum table (256 entries) ----
constexpr std::array<std::uint8_t, 256> make_crc_table() {
    std::array<std::uint8_t, 256> t{};
    for (unsigned i = 0; i < 256; ++i) {
        std::uint8_t crc = static_cast<std::uint8_t>(i);
        for (int bit = 0; bit < 8; ++bit)
            crc = static_cast<std::uint8_t>((crc & 0x80) ? ((crc << 1) ^ 0x07) : (crc << 1));
        t[i] = crc;
    }
    return t;
}
constexpr auto kCrcTable = make_crc_table();

constexpr std::uint8_t crc8(const char* s) {
    std::uint8_t crc = 0;
    for (; *s != '\0'; ++s) crc = kCrcTable[crc ^ static_cast<std::uint8_t>(*s)];
    return crc;
}

// ---- static_assert: the compiler checks these; a failure stops the build ----
static_assert(factorial(5) == 120, "5! must be 120");
static_assert(is_prime(97) && !is_prime(91), "primality check");
static_assert(kSquares[9] == 81, "table entry");
static_assert(sizeof(std::uint32_t) == 4, "uint32_t must be 4 bytes");
static_assert(kPrimes.size() == 15, "there are 15 primes below 50");
static_assert(crc8("123456789") == 0xF4, "CRC-8 (poly 0x07) check value");

int main() {
    // ===== SECTION 1: constexpr AT COMPILE TIME AND RUN TIME =====
    std::cout << "===== SECTION 1: constexpr AT COMPILE TIME AND RUN TIME =====\n";
    constexpr auto f10 = factorial(10);  // forced compile-time
    std::cout << "factorial(10) computed at compile time = " << f10 << "\n";
    unsigned runtime_n = 12;             // not a constant expression
    std::cout << "factorial(" << runtime_n << ") computed at run time = " << factorial(runtime_n) << "\n";
    std::cout << std::boolalpha << "is_prime(97)=" << is_prime(97) << " is_prime(91)=" << is_prime(91) << " (91 = 7 * 13)\n";

    // ===== SECTION 2: consteval =====
    std::cout << "===== SECTION 2: consteval =====\n";
    constexpr unsigned sq = square_ct(12);
    std::cout << "square_ct(12) = " << sq << "\n";
    std::cout << "square_ct(runtime_n) would be a COMPILE ERROR: consteval functions only accept constants.\n";

    // ===== SECTION 3: static_assert =====
    std::cout << "===== SECTION 3: static_assert =====\n";
    std::cout << "Six static_asserts at the top of the file already passed before main() could run.\n";
    std::cout << "TRAP: change a table entry or the CRC polynomial and the BUILD fails, not the program.\n";
    std::cout << "sizeof(int)=" << sizeof(int) << " sizeof(long)=" << sizeof(long) << " sizeof(void*)=" << sizeof(void*)
              << " (platform facts; static_assert is how you pin assumptions)\n";

    // ===== SECTION 4: COMPILE-TIME TABLES =====
    std::cout << "===== SECTION 4: COMPILE-TIME TABLES =====\n";
    std::cout << "squares:";
    for (auto v : kSquares) std::cout << " " << v;
    std::cout << "\nprimes < 50 (" << kPrimes.size() << "):";
    for (auto v : kPrimes) std::cout << " " << v;
    std::cout << "\nCRC table entries 0..7:";
    for (int i = 0; i < 8; ++i) std::cout << " " << static_cast<unsigned>(kCrcTable[static_cast<std::size_t>(i)]);
    std::cout << "\ncrc8(\"123456789\") = 0x" << std::hex << static_cast<unsigned>(crc8("123456789")) << std::dec
              << "  (standard CRC-8 check value is 0xF4)\n";
    std::cout << "crc8(\"RDJ\") = " << static_cast<unsigned>(crc8("RDJ")) << "\n";
    std::cout << "The tables live in the executable's read-only data; no loop ran at start-up to build them.\n";
    return 0;
}
