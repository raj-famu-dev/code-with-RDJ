// Tags: #Cpp #OOP #VirtualFunctionsPolymorphism | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: virtual functions, override, final, dynamic dispatch through
 * base references/pointers, and the virtual destructor trap. The trap
 * (deleting a Derived through a Base* whose destructor is NOT virtual) is
 * undefined behaviour, so it is hidden behind a flag:
 *     ./prog --trap     (run it WITHOUT sanitizers; ASan would abort on it)
 * It proves the bug by printing from the destructors: ~Derived never runs.
 */
#include <iostream>
#include <memory>
#include <string>
#include <vector>

// ===== SECTION 1: virtual + override + final =====
class Shape {
public:
    virtual ~Shape() = default;                       // virtual destructor: ALWAYS for polymorphic bases
    virtual double area() const = 0;
    virtual std::string name() const { return "Shape"; }
    std::string label() const { return name() + " area=" + std::to_string(static_cast<int>(area())); }
};
class Square : public Shape {
public:
    explicit Square(double s) : s_(s) {}
    double area() const override { return s_ * s_; }
    std::string name() const override { return "Square"; }
private:
    double s_;
};
class Circle final : public Shape {                   // final: nothing may derive from Circle
public:
    explicit Circle(double r) : r_(r) {}
    double area() const override { return 3.0 * r_ * r_; }    // pi approximated as 3 to keep output integral
    std::string name() const override { return "Circle"; }
private:
    double r_;
};
class Cube final : public Square {
public:
    explicit Cube(double s) : Square(s) {}
    std::string name() const final { return "CubeFace"; }
};

// ===== SECTION 3: the vtable trap, version with the missing virtual =====
struct BadBase {
    BadBase() = default;
    ~BadBase() { std::cout << "  ~BadBase\n"; }       // NOT virtual
};
struct BadDerived : BadBase {
    ~BadDerived() { std::cout << "  ~BadDerived\n"; }
};
struct GoodBase {
    virtual ~GoodBase() { std::cout << "  ~GoodBase\n"; }
};
struct GoodDerived : GoodBase {
    ~GoodDerived() override { std::cout << "  ~GoodDerived\n"; }
};

// ===== SECTION 4: how override protects you =====
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Woverloaded-virtual"   // the compiler warns here; silenced ON PURPOSE for the demo
struct Base2 { virtual void greet(int) const {} virtual ~Base2() = default; };
struct Oops : Base2 {
    void greet(long) const {}                          // meant to override, but the signature differs: a NEW function, silently
};
#pragma GCC diagnostic pop
struct Fixed : Base2 {
    void greet(int) const override { std::cout << "  Fixed::greet(int) overrides\n"; }
    // void greet(long) const override {}   // <- with `override` this line would be a COMPILE error
};

int main(int argc, char** argv) {
    bool trap = argc > 1 && std::string(argv[1]) == "--trap";

    std::cout << "===== SECTION 1: virtual + override + final =====\n";
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Square>(4));
    shapes.push_back(std::make_unique<Circle>(2));
    shapes.push_back(std::make_unique<Cube>(3));
    for (const auto& s : shapes) std::cout << "  " << s->label() << "\n";
    std::cout << "label() is written once in Shape and calls name()/area() which dispatch on the REAL object type.\n";

    std::cout << "\n===== SECTION 2: the vtable, observed =====\n";
    std::cout << "sizeof(Square) = " << sizeof(Square) << " (one double = 8, plus one hidden vptr = 8)\n";
    struct NoVirtual { double d; };
    struct WithVirtual { double d; virtual void f() {} virtual ~WithVirtual() = default; };
    std::cout << "sizeof(NoVirtual) = " << sizeof(NoVirtual) << ", sizeof(WithVirtual) = " << sizeof(WithVirtual) << "\n";
    std::cout << "Cost model: one pointer per object, one indirect call per virtual call, can prevent the compiler from inlining the call.\n";

    std::cout << "\n===== SECTION 3: virtual destructor trap =====\n";
    std::cout << "Correct (virtual destructor), deleting through GoodBase*:\n";
    {
        GoodBase* p = new GoodDerived;
        delete p;
    }
    if (trap) {
        std::cout << "TRAP (--trap): deleting BadDerived through BadBase* (undefined behaviour):\n";
        BadBase* p = new BadDerived;
        delete p;                                      // only ~BadBase runs; ~BadDerived never does
        std::cout << "Notice: '~BadDerived' was never printed, so Derived's resources would leak.\n";
    } else {
        std::cout << "TRAP not run by default (it is undefined behaviour). Run with --trap to see ~BadDerived never print.\n";
    }

    std::cout << "\n===== SECTION 4: how override protects you =====\n";
    Oops o;
    Base2& b = o;
    b.greet(1);
    std::cout << "  Oops::greet(long) was NOT called through Base2& (it is not an override); nothing printed above.\n";
    Fixed f;
    Base2& b2 = f;
    b2.greet(1);
    return 0;
}
