// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: "prefer composition over inheritance" by refactoring a small
 * design twice. Version A: a Stack that INHERITS from std::vector (leaks
 * the whole vector interface, breaks the stack rule). Version B: a Stack
 * that HAS a vector (composition), exposing only push/pop/top. Then a
 * second example: behavior swapped at run time via composition of a strategy.
 */
#include <functional>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

// ===== SECTION 1: Version A, inheritance (the tempting design) =====
class StackByInheritance : public std::vector<int> {       // is-a vector?  Not really.
public:
    void push(int v) { push_back(v); }
    int pop() { int v = back(); pop_back(); return v; }
};

// ===== SECTION 2: Version B, composition =====
class Stack {
public:
    void push(int v) { items_.push_back(v); }
    int pop() {
        if (items_.empty()) throw std::underflow_error("pop on empty Stack");
        int v = items_.back();
        items_.pop_back();
        return v;
    }
    int top() const { return items_.at(items_.size() - 1); }
    bool empty() const { return items_.empty(); }
    std::size_t size() const { return items_.size(); }
private:
    std::vector<int> items_;                                // HAS-A vector; interface is entirely under our control
};

// ===== SECTION 3: composition lets behavior change at run time =====
class Discount {                                            // small interface: the "strategy"
public:
    virtual ~Discount() = default;
    virtual int apply(int cents) const = 0;
};
class NoDiscount : public Discount { public: int apply(int c) const override { return c; } };
class PercentOff : public Discount {
public:
    explicit PercentOff(int p) : p_(p) {}
    int apply(int c) const override { return c - c * p_ / 100; }
private:
    int p_;
};
class Checkout {                                            // has-a Discount, not is-a
public:
    explicit Checkout(std::unique_ptr<Discount> d) : discount_(std::move(d)) {}
    void setDiscount(std::unique_ptr<Discount> d) { discount_ = std::move(d); }   // change behaviour while running
    int total(int cents) const { return discount_->apply(cents); }
private:
    std::unique_ptr<Discount> discount_;
};
// The inheritance version would need Checkout, CheckoutWithTenPercent, CheckoutWithTwentyPercent... one class per combination.

int main() {
    std::cout << "===== SECTION 1: Version A, inheritance =====\n";
    StackByInheritance bad;
    bad.push(1); bad.push(2); bad.push(3);
    std::cout << "pop() = " << bad.pop() << " (looks like a stack)\n";
    bad.insert(bad.begin(), 99);                           // legal: the whole vector interface leaked out
    bad.erase(bad.begin() + 1);                            // removes from the middle
    std::cout << "but a 'stack' also allows insert/erase anywhere; contents now:";
    for (int x : bad) std::cout << " " << x;
    std::cout << "\n";
    std::cout << "Also: std::vector has no virtual destructor; deleting a StackByInheritance through a vector* would be undefined behaviour.\n";

    std::cout << "\n===== SECTION 2: Version B, composition =====\n";
    Stack s;
    s.push(10); s.push(20); s.push(30);
    std::cout << "top = " << s.top() << ", size = " << s.size() << "\n";
    std::cout << "pop x3: " << s.pop() << " " << s.pop() << " " << s.pop() << "\n";
    try { s.pop(); } catch (const std::underflow_error& e) { std::cout << "pop on empty: " << e.what() << " (invariant enforced)\n"; }
    std::cout << "s.insert(...) does not exist: only push/pop/top/empty/size can be called.\n";
    std::cout << "Later we could swap std::vector for std::deque or std::list inside Stack and no caller would change.\n";

    std::cout << "\n===== SECTION 3: composition lets behavior change at run time =====\n";
    Checkout co(std::make_unique<NoDiscount>());
    std::cout << "no discount on 2000c: " << co.total(2000) << "\n";
    co.setDiscount(std::make_unique<PercentOff>(25));
    std::cout << "25% off on 2000c   : " << co.total(2000) << " (same Checkout object, new behaviour)\n";

    std::cout << "\nRule of thumb:\n";
    std::cout << "  - inherit for a true is-a relationship AND when you need polymorphism through the base\n";
    std::cout << "  - otherwise hold the other class as a member (has-a) and forward the few operations you want\n";
    return 0;
}
