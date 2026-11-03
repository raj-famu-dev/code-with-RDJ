// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: private data protecting an invariant, const member functions
 * (a promise not to modify the object), `mutable` for caches, `friend`
 * for deliberate access, and the trap of returning non-const references
 * to private data (a hole in encapsulation).
 */
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

// ===== SECTION 1: an invariant enforced by private data =====
// Invariant: the stored percent is always within [0, 100].
class Percent {
public:
    explicit Percent(int v) { set(v); }
    void set(int v) {
        if (v < 0 || v > 100) throw std::out_of_range("percent must be 0..100, got " + std::to_string(v));
        value_ = v;
    }
    int get() const { return value_; }
private:
    int value_ = 0;
};

// ===== SECTION 2: const member functions =====
class Stats {
public:
    void add(int x) { data_.push_back(x); cacheValid_ = false; }
    double mean() const {                       // const: observably does not change the object
        if (!cacheValid_) {                     // but it may fill a mutable cache
            long long s = 0;
            for (int x : data_) s += x;
            cachedMean_ = data_.empty() ? 0.0 : static_cast<double>(s) / static_cast<double>(data_.size());
            cacheValid_ = true;
            ++cacheFills_;
        }
        return cachedMean_;
    }
    int cacheFills() const { return cacheFills_; }
private:
    std::vector<int> data_;
    mutable double cachedMean_ = 0.0;           // mutable: allowed to change inside const functions
    mutable bool cacheValid_ = false;
    mutable int cacheFills_ = 0;
};
void readOnlyView(const Stats& s) {              // a const reference can ONLY call const members
    std::cout << "  mean via const& = " << s.mean() << "\n";
}

// ===== SECTION 3: friend =====
class Secret {
public:
    explicit Secret(int v) : v_(v) {}
    friend void audit(const Secret& s);          // a non-member granted access
    friend std::ostream& operator<<(std::ostream& os, const Secret& s) { return os << "Secret(" << s.v_ << ")"; }
private:
    int v_;
};
void audit(const Secret& s) { std::cout << "  audit reads private v_ = " << s.v_ << "\n"; }

// ===== SECTION 4: the leaky getter trap =====
class LeakyBag {
public:
    LeakyBag() : items_{1, 2, 3} {}
    std::vector<int>& items() { return items_; }               // TRAP: caller can break any invariant
    std::size_t size() const { return items_.size(); }
private:
    std::vector<int> items_;                                    // intended: "never empty"
};
class SafeBag {
public:
    SafeBag() : items_{1, 2, 3} {}
    const std::vector<int>& items() const { return items_; }   // read-only view
    void removeLast() {
        if (items_.size() <= 1) throw std::logic_error("invariant: bag may never become empty");
        items_.pop_back();
    }
    std::size_t size() const { return items_.size(); }
private:
    std::vector<int> items_;
};

int main() {
    std::cout << "===== SECTION 1: an invariant enforced by private data =====\n";
    Percent p(40);
    std::cout << "Percent(40).get() = " << p.get() << "\n";
    try { p.set(150); } catch (const std::out_of_range& e) { std::cout << "rejected: " << e.what() << "\n"; }
    std::cout << "value after rejected set = " << p.get() << " (unchanged, invariant intact)\n";

    std::cout << "\n===== SECTION 2: const member functions =====\n";
    Stats s;
    s.add(2); s.add(4); s.add(9);
    readOnlyView(s);
    readOnlyView(s);
    std::cout << "cache was filled " << s.cacheFills() << " time(s) for 2 const calls (mutable cache)\n";
    s.add(1);
    readOnlyView(s);
    std::cout << "after add(): cache filled " << s.cacheFills() << " time(s) total\n";

    std::cout << "\n===== SECTION 3: friend =====\n";
    Secret sec(7);
    audit(sec);
    std::cout << "  streamed: " << sec << "\n";
    std::cout << "  friendship is not inherited and not mutual; grant it sparingly.\n";

    std::cout << "\n===== SECTION 4: the leaky getter trap =====\n";
    LeakyBag lb;
    lb.items().clear();                           // legal, and destroys the "never empty" rule
    std::cout << "LeakyBag after caller clears items(): size = " << lb.size() << " (invariant broken)\n";
    SafeBag sb;
    try {
        while (true) sb.removeLast();
    } catch (const std::logic_error& e) {
        std::cout << "SafeBag stopped by its own rule: " << e.what() << "; size = " << sb.size() << "\n";
    }
    return 0;
}
