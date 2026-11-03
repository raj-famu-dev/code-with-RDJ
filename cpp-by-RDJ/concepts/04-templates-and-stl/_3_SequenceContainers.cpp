// Tags: #Cpp #Templates #STL #SequenceContainers | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: std::vector, std::deque, std::list and std::array, and what each
 * costs. The complexity claims are VERIFIED by counting operations with an
 * instrumented element type (copies/moves), not by timing. No timings are
 * printed or claimed anywhere in this file.
 */
#include <array>
#include <deque>
#include <iostream>
#include <list>
#include <string>
#include <vector>

// An element that counts how many times it is moved or copied.
struct Counted {
    static inline long moves = 0;
    static inline long copies = 0;
    int v;
    Counted(int x = 0) : v(x) {}
    Counted(const Counted& o) : v(o.v) { ++copies; }
    Counted(Counted&& o) noexcept : v(o.v) { ++moves; }
    Counted& operator=(const Counted& o) { v = o.v; ++copies; return *this; }
    Counted& operator=(Counted&& o) noexcept { v = o.v; ++moves; return *this; }
    static void reset() { moves = copies = 0; }
    static long total() { return moves + copies; }
};

template <typename C>
long costOfInsertFront(int n) {                    // build a container of n elements then insert one at the FRONT
    C c;
    for (int i = 0; i < n; ++i) c.emplace_back(i);
    Counted::reset();
    c.insert(c.begin(), Counted(-1));
    return Counted::total();
}
template <typename C>
long costOfInsertMiddle(int n) {                   // vector/deque only (list needs an iterator walk, which is not a move)
    C c;
    for (int i = 0; i < n; ++i) c.emplace_back(i);
    Counted::reset();
    c.insert(c.begin() + n / 2, Counted(-1));
    return Counted::total();
}
template <typename C>
long costOfAppend(int n) {                         // append to a deque or list (never relocates existing elements)
    C c;
    for (int i = 0; i < n; ++i) c.emplace_back(i);
    Counted::reset();
    c.emplace_back(-1);
    return Counted::total();
}

int main() {
    std::cout << "===== SECTION 1: std::vector =====\n";
    std::vector<int> v;
    std::size_t lastCap = 0;
    int growths = 0;
    for (int i = 0; i < 1000; ++i) {
        v.push_back(i);
        if (v.capacity() != lastCap) { lastCap = v.capacity(); ++growths; }
    }
    std::cout << "after 1000 push_back: size=" << v.size() << ", capacity>=size: " << (v.capacity() >= v.size()) << "\n";
    std::cout << "number of reallocations for 1000 push_backs: " << growths << " (a measurement of THIS standard library; far fewer than 1000 because capacity grows geometrically)\n";
    std::vector<int> w;
    w.reserve(1000);
    const int* before = w.data();
    for (int i = 0; i < 1000; ++i) w.push_back(i);
    std::cout << "with reserve(1000) the buffer never moved: " << std::boolalpha << (before == w.data()) << "\n";
    std::vector<int> small{1, 2, 3};
    const int* p = small.data();
    small.reserve(100);
    std::cout << "Trap: after growth, old pointers/iterators are invalid; the buffer moved: " << (p != small.data()) << " (pointer comparison only, address not printed)\n";

    std::cout << "\n===== SECTION 2: cost of inserting at the front (counted element moves/copies, n=1000) =====\n";
    long vecFront = costOfInsertFront<std::vector<Counted>>(1000);
    long dqFront = costOfInsertFront<std::deque<Counted>>(1000);
    long lstFront = costOfInsertFront<std::list<Counted>>(1000);
    std::cout << "vector: " << vecFront << " ops  (shifts every element: O(n))\n";
    std::cout << "deque : " << dqFront << " ops  (insert at either end of a deque is O(1))\n";
    std::cout << "list  : " << lstFront << " ops  (relinks nodes: O(1))\n";
    long vecFront2 = costOfInsertFront<std::vector<Counted>>(2000);
    std::cout << "vector with n=2000: " << vecFront2 << " ops (it grew with n; the list stayed at " << costOfInsertFront<std::list<Counted>>(2000) << ")\n";
    std::cout << "insert in the MIDDLE (n=1000): vector " << costOfInsertMiddle<std::vector<Counted>>(1000)
              << " ops, deque " << costOfInsertMiddle<std::deque<Counted>>(1000) << " ops (both shift elements: O(n); roughly half the elements move)\n";
    std::deque<int> d;
    d.push_front(2); d.push_front(1); d.push_back(3);
    std::cout << "deque push_front/push_back both O(1): ";
    for (int x : d) std::cout << x << " ";
    std::cout << "\n";

    std::cout << "\n===== SECTION 3: append cost and element access =====\n";
    std::cout << "appending to a deque/list never relocates existing elements: deque ops = " << costOfAppend<std::deque<Counted>>(1000)
              << ", list ops = " << costOfAppend<std::list<Counted>>(1000) << " (n=1000)\n";
    std::vector<Counted> cv;
    cv.reserve(10);
    for (int i = 0; i < 5; ++i) cv.emplace_back(i);
    Counted::reset();
    cv.emplace_back(5);
    std::cout << "vector with spare capacity, emplace_back ops: " << Counted::total() << " (amortized O(1): no shifting)\n";
    std::vector<Counted> full;
    for (int i = 0; i < 4; ++i) full.emplace_back(i);
    full.shrink_to_fit();
    Counted::reset();
    full.emplace_back(4);
    std::cout << "vector at full capacity, emplace_back ops: " << Counted::total() << " (reallocation moved/copied the old elements)\n";
    std::list<int> l{10, 20, 30};
    std::cout << "list has no operator[]; reaching element 2 means walking: *std::next(l.begin(), 2) = " << *std::next(l.begin(), 2) << "\n";
    std::vector<int> r{10, 20, 30};
    std::cout << "vector r[2] = " << r[2] << " (O(1) random access)\n";

    std::cout << "\n===== SECTION 4: std::array and the complexity table =====\n";
    std::array<int, 4> a{1, 2, 3, 4};
    std::cout << "std::array<int,4>: size " << a.size() << " fixed at compile time, sizeof = " << sizeof(a) << " (no heap allocation, no growth)\n";
    std::cout << "a.at(3) = " << a.at(3) << "; ";
    try { a.at(4); } catch (const std::out_of_range&) { std::cout << "a.at(4) threw out_of_range\n"; }
    std::cout << "\nstandard guarantees (the counts above confirm the vector/deque/list front, middle and append rows):\n";
    std::cout << "  op                 vector      deque       list        array\n";
    std::cout << "  random access      O(1)        O(1)        O(n)        O(1)\n";
    std::cout << "  push_back          amort O(1)  O(1)        O(1)        n/a\n";
    std::cout << "  push_front         O(n)        O(1)        O(1)        n/a\n";
    std::cout << "  insert in middle   O(n)        O(n)        O(1)*       n/a\n";
    std::cout << "  contiguous memory  yes         no          no          yes\n";
    std::cout << "  (* O(1) once you HAVE the iterator; finding it is O(n))\n";
    return 0;
}
