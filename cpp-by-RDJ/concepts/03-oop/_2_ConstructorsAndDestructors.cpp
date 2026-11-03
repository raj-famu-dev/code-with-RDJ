// Tags: #Cpp #OOP #ConstructorsDestructors | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: default / parameterized / delegating constructors, `explicit`
 * (blocking silent conversions), and destruction order (reverse of
 * construction, members before base, locals in reverse scope order).
 * A Logger prints every construction and destruction so the order is visible.
 */
#include <iostream>
#include <string>
#include <vector>

struct Logger {
    std::string name;
    explicit Logger(std::string n) : name(std::move(n)) { std::cout << "  + " << name << "\n"; }
    Logger(const Logger& o) : name(o.name + "'") { std::cout << "  + " << name << " (copy)\n"; }
    ~Logger() { std::cout << "  - " << name << "\n"; }
};

// ===== SECTION 1: default, parameterized, delegating =====
class Rect {
public:
    Rect() : Rect(1, 1) { std::cout << "  Rect() body ran after delegation\n"; }       // delegating
    explicit Rect(int side) : Rect(side, side) {}                                         // delegating
    Rect(int w, int h) : w_(w), h_(h) { std::cout << "  Rect(" << w_ << "," << h_ << ") target ctor\n"; }
    int area() const { return w_ * h_; }
private:
    int w_, h_;
};

// ===== SECTION 2: explicit =====
class Meters {
public:
    explicit Meters(double v) : v_(v) {}
    double value() const { return v_; }
private:
    double v_;
};
class Feet {                       // NOT explicit: converts silently
public:
    Feet(double v) : v_(v) {}      // NOLINT: deliberately implicit for the demo
    double value() const { return v_; }
private:
    double v_;
};
double describeMeters(Meters m) { return m.value(); }
double describeFeet(Feet f) { return f.value(); }

// ===== SECTION 3: destruction order =====
struct Base {
    Logger b{"Base subobject"};
    Base() { std::cout << "  Base() body\n"; }
    ~Base() { std::cout << "  ~Base() body\n"; }
};
struct Derived : Base {
    Logger m1{"member m1"};
    Logger m2{"member m2"};
    Derived() { std::cout << "  Derived() body\n"; }
    ~Derived() { std::cout << "  ~Derived() body\n"; }
};

int main() {
    std::cout << "===== SECTION 1: default, parameterized, delegating =====\n";
    std::cout << "Rect r0;\n";
    Rect r0;
    std::cout << "Rect r1(4);\n";
    Rect r1(4);
    std::cout << "Rect r2(2, 3);\n";
    Rect r2(2, 3);
    std::cout << "areas: " << r0.area() << " " << r1.area() << " " << r2.area() << "\n";
    std::cout << "Most vexing parse: `Rect r3();` declares a FUNCTION, not an object. Use `Rect r3;` or `Rect r3{};`.\n";

    std::cout << "\n===== SECTION 2: explicit =====\n";
    std::cout << "describeFeet(3.5) compiles (implicit double -> Feet): " << describeFeet(3.5) << "\n";
    std::cout << "describeMeters(Meters{3.5}) must be spelled out: " << describeMeters(Meters{3.5}) << "\n";
    std::cout << "describeMeters(3.5) would be a compile error because the constructor is explicit.\n";

    std::cout << "\n===== SECTION 3: destruction order =====\n";
    {
        std::cout << " scope opens\n";
        Logger a("local a");
        Logger b("local b");
        Derived d;
        std::cout << " scope closes (destruction runs in REVERSE order of construction)\n";
    }
    std::cout << "\nWith g++ 13 (libstdc++) a vector destroys its elements front to back (the standard does not promise an order):\n";
    {
        std::vector<Logger> v;
        v.reserve(3);
        v.emplace_back("v0");
        v.emplace_back("v1");
        v.emplace_back("v2");
        std::cout << " vector scope closes\n";
    }
    std::cout << "\n(r0, r1, r2 are destroyed when main returns.)\n";
    return 0;
}
