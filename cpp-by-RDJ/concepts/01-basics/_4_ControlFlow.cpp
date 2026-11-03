// Tags: #Cpp #Basics #ControlFlow | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _4_ControlFlow
 * Teaches: if with initialiser, switch fallthrough (and [[fallthrough]]),
 * range-based for (by value vs by reference), loops, break/continue.
 */
#include <iostream>
#include <map>
#include <string>
#include <vector>

enum class Level { Low, Medium, High };

// Deliberate fallthrough, documented with the attribute so -Wextra stays quiet.
std::string describe(Level l) {
    std::string out;
    switch (l) {
        case Level::High:
            out += "alert ";
            [[fallthrough]];
        case Level::Medium:
            out += "log ";
            break;
        case Level::Low:
            out += "ignore ";
            break;
    }
    return out;
}

// TRAP version: every case breaks, so nothing leaks into the next case.
std::string describe_no_fall(Level l) {
    switch (l) {
        case Level::High: return "alert";
        case Level::Medium: return "log";
        case Level::Low: return "ignore";
    }
    return "unknown";
}

int main() {
    std::cout << "===== SECTION 1: if WITH INITIALISER =====\n";
    std::map<std::string, int> stock{{"apple", 3}, {"pear", 0}};
    if (auto it = stock.find("apple"); it != stock.end()) {   // 'it' lives only inside this if/else
        std::cout << "apple count = " << it->second << '\n';
    } else {
        std::cout << "no apple\n";
    }
    if (auto it = stock.find("kiwi"); it == stock.end()) std::cout << "kiwi not stocked\n";

    std::cout << "\n===== SECTION 2: switch AND [[fallthrough]] =====\n";
    std::cout << "High   -> " << describe(Level::High) << '\n';
    std::cout << "Medium -> " << describe(Level::Medium) << '\n';
    std::cout << "Low    -> " << describe(Level::Low) << '\n';
    std::cout << "no-fallthrough High -> " << describe_no_fall(Level::High) << '\n';
    // Trap: a forgotten 'break' silently runs the next case. -Wextra
    // (-Wimplicit-fallthrough) warns unless you write [[fallthrough]].
    // switch only works on integral/enum types: no strings, unlike Java 7+.

    std::cout << "\n===== SECTION 3: RANGE-BASED for =====\n";
    std::vector<int> v{1, 2, 3, 4};
    for (int x : v) x *= 10;                  // trap: x is a COPY, v unchanged
    std::cout << "after by-value loop:     ";
    for (const int& x : v) std::cout << x << ' ';
    std::cout << '\n';
    for (int& x : v) x *= 10;                 // reference: modifies the elements
    std::cout << "after by-reference loop: ";
    for (const int& x : v) std::cout << x << ' ';
    std::cout << '\n';
    std::vector<std::string> names{"Ada", "Linus", "Grace"};
    for (const auto& n : names) std::cout << n << '(' << n.size() << ") ";   // const& avoids copying strings
    std::cout << '\n';
    for (const auto& [k, val] : stock) std::cout << k << "=" << val << ' ';   // structured bindings
    std::cout << '\n';

    std::cout << "\n===== SECTION 4: LOOPS, break, continue =====\n";
    int sum = 0;
    for (int i = 1; i <= 10; ++i) {
        if (i % 2 == 0) continue;     // skip evens
        if (i > 7) break;             // stop early
        sum += i;
    }
    std::cout << "sum of odd numbers up to 7 = " << sum << '\n';
    int n = 27, steps = 0;
    while (n != 1) { n = (n % 2 == 0) ? n / 2 : 3 * n + 1; ++steps; }
    std::cout << "Collatz steps for 27 = " << steps << '\n';
    int countdown = 3;
    do { std::cout << countdown << ' '; } while (--countdown > 0);   // body runs at least once
    std::cout << "liftoff\n";
    // Trap: indexing with an int against v.size() (unsigned) mixes signedness.
    for (std::size_t i = 0; i < v.size(); ++i) std::cout << v[i] << (i + 1 < v.size() ? "," : "\n");
    return 0;
}
