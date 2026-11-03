// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: overloading +, ==, <=> (C++20 three-way comparison), <<, [],
 * and explicit conversion operators, plus the rules for when NOT to overload.
 * Types: Money (value type), Vec3 (indexing), Version (defaulted <=>), Flag (explicit bool).
 */
#include <compare>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <algorithm>

// ===== SECTION 1: arithmetic and streaming =====
class Money {
public:
    explicit Money(long long cents = 0) : cents_(cents) {}
    Money operator+(const Money& o) const { return Money(cents_ + o.cents_); }
    Money& operator+=(const Money& o) { cents_ += o.cents_; return *this; }
    Money operator-() const { return Money(-cents_); }                              // unary minus
    bool operator==(const Money& o) const = default;                                // C++20: memberwise ==
    friend std::ostream& operator<<(std::ostream& os, const Money& m) {
        long long abs = m.cents_ < 0 ? -m.cents_ : m.cents_;
        return os << (m.cents_ < 0 ? "-" : "") << "$" << abs / 100 << "." << (abs % 100 < 10 ? "0" : "") << abs % 100;
    }
private:
    long long cents_;
};

// ===== SECTION 2: comparison with <=> =====
struct Version {
    int major, minor, patch;
    auto operator<=>(const Version&) const = default;   // generates <, <=, >, >=, and == too
};
// Hand-written <=> for a custom rule: compare only the integer part of weight in kilograms.
class Parcel {
public:
    explicit Parcel(int grams) : grams_(grams) {}
    std::strong_ordering operator<=>(const Parcel& o) const { return grams_ / 1000 <=> o.grams_ / 1000; }
    bool operator==(const Parcel& o) const { return grams_ / 1000 == o.grams_ / 1000; }  // == is NOT synthesized from a hand-written <=>
    int grams() const { return grams_; }
private:
    int grams_;
};

// ===== SECTION 3: operator[] =====
class Vec3 {
public:
    Vec3(double x, double y, double z) : d_{x, y, z} {}
    double& operator[](std::size_t i) { return d_.at(i); }                 // mutable access
    const double& operator[](std::size_t i) const { return d_.at(i); }     // const access
private:
    std::vector<double> d_;
};

// ===== SECTION 4: explicit conversion =====
class Flag {
public:
    explicit Flag(bool v) : v_(v) {}
    explicit operator bool() const { return v_; }     // usable in if(...), NOT in arithmetic
private:
    bool v_;
};
class Celsius {
public:
    explicit Celsius(double d) : d_(d) {}
    operator double() const { return d_; }            // IMPLICIT conversion: the "don't do this" example
private:
    double d_;
};

int main() {
    std::cout << "===== SECTION 1: arithmetic and streaming =====\n";
    Money a(1999), b(501);
    Money c = a + b;
    c += Money(5);
    std::cout << "a=" << a << " b=" << b << " total=" << c << " -a=" << -a << "\n";
    std::cout << "Money(100) == Money(100): " << std::boolalpha << (Money(100) == Money(100)) << ", != works via == in C++20: " << (Money(1) != Money(2)) << "\n";

    std::cout << "\n===== SECTION 2: comparison with <=> =====\n";
    Version v1{1, 2, 3}, v2{1, 10, 0};
    std::cout << "1.2.3 < 1.10.0: " << (v1 < v2) << ", 1.2.3 == 1.2.3: " << (v1 == Version{1, 2, 3}) << "\n";
    auto cmp = v1 <=> v2;
    std::cout << "(v1 <=> v2) < 0: " << (cmp < 0) << " (std::strong_ordering::less)\n";
    std::vector<Version> vs{{2, 0, 0}, {1, 9, 9}, {1, 10, 0}};
    std::sort(vs.begin(), vs.end());
    std::cout << "sorted: ";
    for (const auto& v : vs) std::cout << v.major << "." << v.minor << "." << v.patch << " ";
    std::cout << "\n";
    Parcel p1(1200), p2(1900), p3(2100);
    std::cout << "Parcel(1200g) == Parcel(1900g): " << (p1 == p2) << " (same whole kg, by OUR rule)\n";
    std::cout << "Parcel(1900g) < Parcel(2100g): " << (p2 < p3) << "\n";
    std::cout << "Trap: equality by a custom rule must be written yourself; == is not generated from a hand-written <=>.\n";

    std::cout << "\n===== SECTION 3: operator[] =====\n";
    Vec3 v(1.0, 2.0, 3.0);
    v[1] = 20.0;
    const Vec3& cv = v;
    std::cout << "v[0]=" << v[0] << " v[1]=" << v[1] << " cv[2]=" << cv[2] << "\n";
    try { std::cout << v[3]; } catch (const std::out_of_range&) { std::cout << "v[3] threw std::out_of_range (we used at(), so no silent overflow)\n"; }

    std::cout << "\n===== SECTION 4: explicit conversion =====\n";
    Flag on(true), off(false);
    if (on) std::cout << "if (on) works: explicit operator bool is allowed in conditions\n";
    std::cout << "off as bool: " << static_cast<bool>(off) << "\n";
    std::cout << "int n = on + 1; would not compile (explicit stops silent arithmetic)\n";
    Celsius t(36.6);
    double d = t;                                        // implicit conversion happens quietly
    std::cout << "Celsius silently converted to double: " << d << " (convenient, but it also lets t + 5 and t < 'x' compile)\n";

    std::cout << "\nRules for when NOT to overload:\n";
    std::cout << "  - only when the meaning is obvious (Money + Money, not Employee + Employee)\n";
    std::cout << "  - never overload &&, ||, or , (comma): you lose short-circuit/ordering guarantees\n";
    std::cout << "  - keep == and < consistent with each other; keep symmetric ones as non-members/friends\n";
    std::cout << "  - prefer `explicit` conversions; prefer a named function when an operator would surprise a reader\n";
    return 0;
}
