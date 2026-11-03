// Tags: #Cpp #Pointers #MemoryManagement #ConstLifetimes | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _8_ConstAndLifetimes
 * Teaches: const correctness (const methods, const references, mutable),
 * the dangling-reference traps (returning a reference to a local, a view
 * into a dead temporary), and iterator/pointer/reference invalidation when a
 * vector reallocates. Every dangerous line is DESCRIBED in a comment; the
 * code that runs is the safe version, proven with indices or fresh lookups.
 */
#include <cstdint>
#include <iostream>
#include <list>
#include <map>
#include <string>
#include <vector>

class Account {
public:
    explicit Account(int cents) : cents_(cents) {}
    int balance() const { ++reads_; return cents_; }      // const method; 'mutable' counter may still change
    void deposit(int c) { cents_ += c; }                  // non-const: changes the object
    int reads() const { return reads_; }
    const std::string& label() const { return label_; }   // returns a const reference to a MEMBER: safe while the object lives
private:
    int cents_;
    mutable int reads_ = 0;                               // bookkeeping that does not change logical state
    std::string label_ = "checking";
};

void report(const Account& a) {                           // const& promises not to modify: only const methods callable
    std::cout << "  balance " << a.balance() << " cents\n";
    // a.deposit(1);                                      // ERROR: deposit is not const
}

// TRAP (described): int& bad() { int x = 1; return x; }  -> dangling; g++ warns, use is UB.
// SAFE:
int good_value() { int x = 1; return x; }

// Returns by value, so callers can hold it safely.
std::string make_greeting(const std::string& name) { return "hello " + name; }

int main() {
    std::cout << "===== SECTION 1: CONST CORRECTNESS =====\n";
    Account acct(500);
    report(acct);
    const Account frozen(900);
    std::cout << "  const object can call const methods: " << frozen.balance() << '\n';
    // frozen.deposit(5);                                 // ERROR: cannot call a non-const method on a const object
    std::cout << "  mutable counter changed through const methods: reads = " << frozen.reads() << '\n';
    const std::string& lbl = acct.label();
    std::cout << "  label via const&: " << lbl << '\n';
    // std::string& rw = acct.label();                    // ERROR: cannot bind non-const ref to const result
    std::cout << "  const is a compile-time contract: it moves bugs from run time to compile time.\n";
    std::cout << "  const_cast can remove const, but modifying a truly const object that way is undefined behaviour.\n";

    std::cout << "\n===== SECTION 2: DANGLING REFERENCE TRAPS =====\n";
    std::cout << "  good_value() = " << good_value() << " (return by value is safe)\n";
    // Trap 1 (described): returning a reference/pointer to a local variable.
    // Trap 2 (described): const std::string& r = make_greeting("a").substr(0,2); is fine (lifetime extension),
    //   but   std::string_view v = make_greeting("a");   dangles at the semicolon: the temporary dies.
    // Trap 3 (described): a lambda capturing a local by reference [&], then returned or stored; the local is gone.
    const std::string& extended = make_greeting("RDJ");   // legal: a const& to a temporary extends its life
    std::cout << "  lifetime extension keeps the temporary alive: " << extended << '\n';
    auto make_counter = [] { int start = 10; return [start]() mutable { return ++start; }; };   // capture BY VALUE: safe
    auto counter = make_counter();
    std::cout << "  lambda capture by value survives: " << counter() << ", " << counter() << '\n';
    // The unsafe form would be [&start], which dangles once make_counter's frame is gone.

    std::cout << "\n===== SECTION 3: VECTOR REALLOCATION INVALIDATES =====\n";
    std::vector<int> v{1, 2, 3};
    v.shrink_to_fit();
    const std::size_t cap_before = v.capacity();
    // Keep the old buffer location only as an INTEGER (comparing a dead pointer is itself shaky).
    const auto buffer_before = reinterpret_cast<std::uintptr_t>(v.data());
    v.push_back(4);                                        // capacity was full => reallocation
    const bool reallocated = v.capacity() != cap_before;
    const bool buffer_moved = reinterpret_cast<std::uintptr_t>(v.data()) != buffer_before;
    std::cout << "  capacity changed after push_back: " << std::boolalpha << reallocated << '\n';
    std::cout << "  measurement: the element buffer moved to a new location: " << buffer_moved << '\n';
    // Any pointer, reference or iterator taken BEFORE that push_back is now INVALID:
    // using it would read freed memory. The demo never does.
    // Safe alternatives: (1) re-take &v[0] after the push_back, (2) remember an INDEX, (3) reserve() up front.
    int* fresh = &v[0];
    std::cout << "  re-taken pointer reads " << *fresh << '\n';
    std::size_t idx = 2;
    v.push_back(5); v.push_back(6); v.push_back(7);
    std::cout << "  index " << idx << " is still valid after more growth: v[2] = " << v[idx] << '\n';
    std::vector<int> reserved;
    reserved.reserve(10);
    reserved.push_back(1);
    int* stable = &reserved[0];
    for (int i = 2; i <= 10; ++i) reserved.push_back(i);   // never exceeds reserve(10), so no reallocation
    std::cout << "  with reserve(10) the pointer stayed valid: *stable = " << *stable << '\n';

    std::cout << "\n===== SECTION 4: ITERATOR INVALIDATION WHILE LOOPING =====\n";
    // Trap (described): for (auto x : v) if (x % 2 == 0) v.push_back(x); -> UB, the loop iterator is invalidated.
    // Trap (described): calling v.erase(it) and then ++it uses an invalid iterator.
    std::vector<int> nums{1, 2, 3, 4, 5, 6};
    for (auto it = nums.begin(); it != nums.end();) {
        if (*it % 2 == 0) it = nums.erase(it);             // erase returns the next valid iterator
        else ++it;
    }
    std::cout << "  erase-in-loop (using the returned iterator): ";
    for (int x : nums) std::cout << x << ' ';
    std::cout << '\n';
    std::vector<int> more{1, 2, 3, 4, 5, 6};
    std::erase_if(more, [](int x) { return x % 2 == 0; }); // C++20: the idiomatic one-liner
    std::cout << "  std::erase_if:                              ";
    for (int x : more) std::cout << x << ' ';
    std::cout << '\n';

    std::cout << "\n===== SECTION 5: WHICH CONTAINERS KEEP REFERENCES VALID =====\n";
    std::list<int> lst{1, 2, 3};
    int& in_list = lst.front();
    lst.push_back(4);                                      // std::list never moves existing nodes
    std::cout << "  list: reference to element survives push_back: " << in_list << '\n';
    std::map<std::string, int> m{{"a", 1}};
    int& in_map = m["a"];
    m["b"] = 2; m["c"] = 3;                                // std::map nodes are stable too
    std::cout << "  map: reference to element survives inserts: " << in_map << '\n';
    std::cout << "  vector/string use contiguous storage: growth may invalidate EVERYTHING; always check the container's rules.\n";
    return 0;
}
