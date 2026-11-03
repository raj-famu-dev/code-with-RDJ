// Tags: #Cpp #OOP #ClassesStructs | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: class vs struct (the only language difference is default access),
 * public/private/protected access specifiers, member initializer lists
 * (and the declaration-order trap), and the implicit `this` pointer.
 */
#include <iostream>
#include <string>
#include <type_traits>

// ===== SECTION 1: class vs struct =====
struct PointS { int x; int y; };          // members public by default
class PointC { int x; int y; public: PointC(int a, int b) : x(a), y(b) {} int sum() const { return x + y; } };

// ===== SECTION 2: access specifiers =====
class Account {
public:
    explicit Account(std::string owner) : owner_(std::move(owner)) {}
    const std::string& owner() const { return owner_; }
    void deposit(int c) { balance_ += c; }
    int balance() const { return balance_; }
protected:
    int protectedValue() const { return 42; }   // visible to derived classes only
private:
    std::string owner_;
    int balance_ = 0;                            // default member initializer
};

// ===== SECTION 3: member initializer lists =====
struct Noisy {
    explicit Noisy(const char* n) : name(n) { std::cout << "  Noisy(" << name << ") constructed\n"; }
    Noisy(const Noisy& o) : name(o.name + "-copy") { std::cout << "  Noisy copied -> " << name << "\n"; }
    Noisy& operator=(const Noisy& o) { name = o.name + "-assigned"; std::cout << "  Noisy assigned -> " << name << "\n"; return *this; }
    std::string name;
};
struct ViaList   { Noisy n; explicit ViaList(const Noisy& src) : n(src) {} };
struct ViaBody   { Noisy n{"default"}; explicit ViaBody(const Noisy& src) { n = src; } };

// Trap: members are initialized in DECLARATION order, not in the order written in the list.
// The tracer makes that visible without reading uninitialized memory.
struct Tracer { explicit Tracer(const char* n) { std::cout << "  init " << n << "\n"; } };
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreorder"   // silence the compiler's warning ON PURPOSE for the demo
struct OrderTrap {
    Tracer first;
    Tracer second;
    OrderTrap() : second("second (written first in list)"), first("first (written second in list)") {}
};
#pragma GCC diagnostic pop
// Real-world consequence: `first(second * 2)` would read `second` before it exists. Fix: keep list order == declaration order.
struct OrderFixed {
    int first;
    int second;
    explicit OrderFixed(int v) : first(v * 2), second(v) {}
};

// ===== SECTION 4: this =====
class Counter {
public:
    Counter& add(int n) { total_ += n; return *this; }     // returning *this enables chaining
    bool isSame(const Counter& o) const { return this == &o; }
    int total() const { return total_; }
private:
    int total_ = 0;
};

int main() {

    std::cout << "===== SECTION 1: class vs struct =====\n";
    PointS ps{3, 4};
    PointC pc(3, 4);
    std::cout << "struct member access ps.x = " << ps.x << " (public by default)\n";
    std::cout << "class method pc.sum() = " << pc.sum() << " (members private by default; ps.x style access would not compile)\n";
    std::cout << "sizeof(PointS) == sizeof(PointC): " << std::boolalpha << (sizeof(PointS) == sizeof(PointC)) << "\n";
    std::cout << "both standard-layout: " << std::is_standard_layout_v<PointS> << "/" << std::is_standard_layout_v<PointC> << "\n";

    std::cout << "\n===== SECTION 2: access specifiers =====\n";
    Account a("rdj");
    a.deposit(50);
    a.deposit(25);
    std::cout << a.owner() << " balance = " << a.balance() << "\n";
    std::cout << "a.balance_ would be a compile error (private); a.protectedValue() too (protected).\n";

    std::cout << "\n===== SECTION 3: member initializer lists =====\n";
    Noisy src("src");
    std::cout << "ViaList (initializes n directly by copy):\n";
    ViaList vl(src);
    std::cout << "ViaBody (default-constructs n, then assigns in the body):\n";
    ViaBody vb(src);
    std::cout << "result names: " << vl.n.name << " | " << vb.n.name << "\n";
    OrderFixed good(5);
    std::cout << "OrderFixed(5): first=" << good.first << " second=" << good.second << "\n";
    std::cout << "OrderTrap: list says second then first; actual construction order:\n";
    OrderTrap t;
    (void)t;

    std::cout << "\n===== SECTION 4: this =====\n";
    Counter c;
    c.add(1).add(2).add(3);
    std::cout << "chained add(1).add(2).add(3) total = " << c.total() << "\n";
    Counter d;
    std::cout << "c.isSame(c) = " << c.isSame(c) << ", c.isSame(d) = " << c.isSame(d) << "\n";
    return 0;
}
