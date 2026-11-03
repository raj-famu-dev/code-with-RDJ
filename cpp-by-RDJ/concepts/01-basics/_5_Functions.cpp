// Tags: #Cpp #Basics #Functions | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _5_Functions
 * Teaches: pass by value / reference / const reference, overloading,
 * default arguments, inline, and returning values (copy elision).
 */
#include <iostream>
#include <string>
#include <utility>
#include <vector>

// A type that announces its copies so the cost of passing by value is visible.
struct Noisy {
    std::string name;
    static inline int copies = 0;
    explicit Noisy(std::string n) : name(std::move(n)) {}
    Noisy(const Noisy& o) : name(o.name) { ++copies; }
    Noisy& operator=(const Noisy&) = default;
};

void by_value(Noisy n) { (void)n; }
void by_ref(Noisy& n) { n.name += "!"; }
void by_const_ref(const Noisy& n) { (void)n; }

void increment_value(int x) { ++x; }          // changes the copy only
void increment_ref(int& x) { ++x; }           // changes the caller's variable

// Overloads: same name, different parameter lists.
std::string show(int x) { return "int:" + std::to_string(x); }
std::string show(double x) { return "double:" + std::to_string(x).substr(0, 4); }
std::string show(const std::string& x) { return "string:" + x; }

// Default arguments are filled in by the CALLER at compile time.
std::string greet(const std::string& name, const std::string& greeting = "Hello", int excl = 1) {
    return greeting + ", " + name + std::string(static_cast<std::size_t>(excl), '!');
}

inline int square(int x) { return x * x; }   // 'inline' mainly means "multiple definitions across files are OK"

Noisy make_noisy() { return Noisy("made"); }   // returns a prvalue; no copy since C++17

int main() {
    std::cout << "===== SECTION 1: VALUE vs REFERENCE =====\n";
    int a = 1;
    increment_value(a);
    std::cout << "after increment_value: " << a << " (unchanged)\n";
    increment_ref(a);
    std::cout << "after increment_ref:   " << a << " (changed)\n";

    std::cout << "\n===== SECTION 2: WHAT PASSING BY VALUE COSTS =====\n";
    Noisy n("data");
    by_value(n);
    std::cout << "copies after by_value:     " << Noisy::copies << '\n';
    by_const_ref(n);
    std::cout << "copies after by_const_ref: " << Noisy::copies << " (no new copy)\n";
    by_ref(n);
    std::cout << "by_ref modified the caller's object: " << n.name << '\n';
    Noisy made = make_noisy();
    std::cout << "copies after returning by value: " << Noisy::copies << " (guaranteed elision, none added)\n";
    std::cout << "Rule: small types (int, double, pointers) by value; big types by const&; out-params by &.\n";
    // by_ref(Noisy("temp"));   // ERROR: a temporary cannot bind to a non-const lvalue reference

    std::cout << "\n===== SECTION 3: OVERLOADING =====\n";
    std::cout << show(7) << ' ' << show(2.5) << ' ' << show(std::string("x")) << '\n';
    // A string literal is a const char[]. Only the std::string overload can
    // accept it (via an implicit conversion), so that one is chosen.
    // Trap to remember: ambiguous calls (e.g. show(5L) with int and double
    // overloads) are compile errors, not silent picks.
    std::cout << show("literal") << '\n';
    // The return type alone cannot distinguish overloads.

    std::cout << "\n===== SECTION 4: DEFAULT ARGUMENTS AND inline =====\n";
    std::cout << greet("Ada") << '\n';
    std::cout << greet("Ada", "Hi") << '\n';
    std::cout << greet("Ada", "Hey", 3) << '\n';
    // You cannot skip a middle argument: greet("Ada", , 3) is not C++.
    // Defaults belong in the declaration (header), not repeated in the definition.
    std::cout << "inline square(9) = " << square(9) << '\n';
    std::vector<int> v{3, 1, 2};
    auto total = [](const std::vector<int>& xs) { int s = 0; for (int x : xs) s += x; return s; };
    std::cout << "lambda over const& vector = " << total(v) << '\n';
    return 0;
}
