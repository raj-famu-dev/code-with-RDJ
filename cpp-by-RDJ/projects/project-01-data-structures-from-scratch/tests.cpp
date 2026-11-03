// Tags: #Cpp #Project #DataStructures #Tests | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// Hand-rolled test runner (no framework) for the four from-scratch data structures.
// Each structure is checked against the matching STANDARD container ("oracle") on thousands of
// operations drawn from a seeded std::mt19937, the same idea as the Java 14-dsa-in-java oracle tests.
// The standard containers are used ONLY here, as the reference; the headers do not include them.
// Exit code: 0 if every CHECK passed, 1 otherwise.

#include <cstdio>
#include <functional>
#include <list>
#include <queue>
#include <random>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
#include <algorithm>

#include "dynamic_array.hpp"
#include "hash_map.hpp"
#include "linked_list.hpp"
#include "min_heap.hpp"

static int g_checks = 0;
static int g_failures = 0;

#define CHECK(cond)                                                                \
    do {                                                                           \
        ++g_checks;                                                                \
        if (!(cond)) {                                                             \
            ++g_failures;                                                          \
            std::printf("  FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond);          \
        }                                                                          \
    } while (0)

#define RUN(test_fn)                                                               \
    do {                                                                           \
        const int before = g_failures;                                             \
        test_fn();                                                                 \
        std::printf("[%s] %s\n", g_failures == before ? "PASS" : "FAIL", #test_fn); \
    } while (0)

// ---------- a type that counts how many instances are alive (finds leaks and double destruction) ----------
struct Tracked {
    static inline int live = 0;
    int id;
    explicit Tracked(int i = 0) : id(i) { ++live; }
    Tracked(const Tracked& o) : id(o.id) { ++live; }
    Tracked(Tracked&& o) noexcept : id(o.id) { ++live; }
    Tracked& operator=(const Tracked&) = default;
    Tracked& operator=(Tracked&&) noexcept = default;
    ~Tracked() { --live; }
    bool operator==(const Tracked& o) const { return id == o.id; }
};

// Copy-only type whose copy constructor can be told to throw: tests the strong exception guarantee.
struct Fragile {
    static inline int live = 0;
    static inline int copies_until_throw = -1;  // -1 = never throw
    int id;
    explicit Fragile(int i = 0) : id(i) { ++live; }
    Fragile(const Fragile& o) : id(o.id) {
        if (copies_until_throw == 0) throw std::runtime_error("copy failed");
        if (copies_until_throw > 0) --copies_until_throw;
        ++live;
    }
    Fragile& operator=(const Fragile&) = default;
    ~Fragile() { --live; }
};

template <class Array, class Vec>
static bool same_contents(const Array& a, const Vec& v) {
    if (a.size() != v.size()) return false;
    for (std::size_t i = 0; i < v.size(); ++i) {
        if (!(a[i] == v[i])) return false;
    }
    return true;
}

// =============================== DynamicArray ===============================

static void test_dynamic_array_oracle() {
    std::mt19937 rng(12345);
    DynamicArray<int> ours;
    std::vector<int> oracle;
    bool all_match = true;
    for (int step = 0; step < 20000; ++step) {
        const int op = static_cast<int>(rng() % 100);
        const int value = static_cast<int>(rng() % 1000);
        if (op < 50 || oracle.empty()) {
            ours.push_back(value);
            oracle.push_back(value);
        } else if (op < 65) {
            ours.pop_back();
            oracle.pop_back();
        } else if (op < 80) {
            const std::size_t idx = rng() % (oracle.size() + 1);
            ours.insert(idx, value);
            oracle.insert(oracle.begin() + static_cast<std::ptrdiff_t>(idx), value);
        } else if (op < 92) {
            const std::size_t idx = rng() % oracle.size();
            ours.erase(idx);
            oracle.erase(oracle.begin() + static_cast<std::ptrdiff_t>(idx));
        } else if (op < 99) {
            const std::size_t idx = rng() % oracle.size();
            ours[idx] = value;
            oracle[idx] = value;
        } else {
            ours.clear();
            oracle.clear();
        }
        if (ours.size() != oracle.size()) all_match = false;
        if (step % 50 == 0 && !same_contents(ours, oracle)) all_match = false;
    }
    CHECK(all_match);
    CHECK(same_contents(ours, oracle));
    CHECK(ours.capacity() >= ours.size());
}

static void test_dynamic_array_strings_and_aliasing() {
    DynamicArray<std::string> words;
    for (int i = 0; i < 100; ++i) words.push_back("a fairly long string to defeat small-string optimisation #" + std::to_string(i));
    CHECK(words.size() == 100);
    CHECK(words[99].back() == '9');
    // push_back of a reference to an element of the SAME array, while it has to reallocate
    DynamicArray<std::string> a{"x", "y", "z", "w"};  // size == capacity == 4: next push reallocates
    CHECK(a.size() == a.capacity());
    a.push_back(a[0]);
    CHECK(a.size() == 5 && a[4] == "x" && a[0] == "x");
}

static void test_dynamic_array_rule_of_five_and_lifetimes() {
    {
        DynamicArray<Tracked> a;
        for (int i = 0; i < 50; ++i) a.emplace_back(i);
        CHECK(Tracked::live == 50);
        DynamicArray<Tracked> copy(a);  // copy ctor: deep
        CHECK(Tracked::live == 100);
        copy[0].id = 999;
        CHECK(a[0].id == 0);  // independent storage
        DynamicArray<Tracked> moved(std::move(a));
        CHECK(a.size() == 0 && moved.size() == 50);  // NOLINT: moved-from state is specified for OUR type
        CHECK(Tracked::live == 100);                 // a move creates nothing
        DynamicArray<Tracked> assigned;
        assigned = copy;                              // copy assign
        CHECK(assigned.size() == 50 && assigned[0].id == 999);
        assigned = std::move(moved);                  // move assign releases the old buffer
        CHECK(assigned.size() == 50);
        assigned = assigned;                          // self assignment must be harmless
        CHECK(assigned.size() == 50);
    }
    CHECK(Tracked::live == 0);  // everything destroyed exactly once
}

static void test_dynamic_array_bounds_and_exceptions() {
    DynamicArray<int> a{1, 2, 3};
    bool threw = false;
    try {
        (void)a.at(3);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    CHECK(threw);
    threw = false;
    try {
        a.insert(4, 0);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    CHECK(threw);
    threw = false;
    try {
        a.erase(3);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    CHECK(threw);
    CHECK(a.size() == 3);

    // Strong guarantee: a copy that throws during reallocation leaves the array unchanged and leaks nothing.
    {
        DynamicArray<Fragile> f;
        for (int i = 0; i < 4; ++i) f.emplace_back(i);  // size 4 == capacity 4
        const int live_before = Fragile::live;
        Fragile::copies_until_throw = 2;  // the 3rd copy made while relocating will throw
        threw = false;
        try {
            f.emplace_back(4);
        } catch (const std::runtime_error&) {
            threw = true;
        }
        Fragile::copies_until_throw = -1;
        CHECK(threw);
        CHECK(f.size() == 4 && f.capacity() == 4);
        CHECK(f[0].id == 0 && f[3].id == 3);
        CHECK(Fragile::live == live_before);  // the half-built copies were destroyed
    }
    CHECK(Fragile::live == 0);
}

// =============================== LinkedList ===============================

static void test_linked_list_oracle() {
    std::mt19937 rng(777);
    LinkedList<int> ours;
    std::list<int> oracle;
    bool all_match = true;
    auto equal_forward_and_backward = [&]() {
        if (ours.size() != oracle.size()) return false;
        auto o = oracle.begin();
        for (auto it = ours.begin(); it != ours.end(); ++it, ++o) {
            if (*it != *o) return false;
        }
        auto ro = oracle.rbegin();
        auto it = ours.end();
        while (it != ours.begin()) {
            --it;
            if (*it != *ro) return false;
            ++ro;
        }
        return true;
    };
    for (int step = 0; step < 10000; ++step) {
        const int op = static_cast<int>(rng() % 100);
        const int value = static_cast<int>(rng() % 1000);
        if (op < 25) {
            ours.push_back(value);
            oracle.push_back(value);
        } else if (op < 45) {
            ours.push_front(value);
            oracle.push_front(value);
        } else if (op < 55 && !oracle.empty()) {
            ours.pop_back();
            oracle.pop_back();
        } else if (op < 65 && !oracle.empty()) {
            ours.pop_front();
            oracle.pop_front();
        } else if (op < 82) {
            const std::size_t idx = rng() % (oracle.size() + 1);
            auto a = ours.begin();
            auto b = oracle.begin();
            for (std::size_t k = 0; k < idx; ++k) {
                ++a;
                ++b;
            }
            ours.insert(a, value);
            oracle.insert(b, value);
        } else if (op < 95 && !oracle.empty()) {
            const std::size_t idx = rng() % oracle.size();
            auto a = ours.begin();
            auto b = oracle.begin();
            for (std::size_t k = 0; k < idx; ++k) {
                ++a;
                ++b;
            }
            auto next_ours = ours.erase(a);
            auto next_oracle = oracle.erase(b);
            if ((next_ours == ours.end()) != (next_oracle == oracle.end())) all_match = false;
        } else if (op < 98) {
            ours.reverse();
            oracle.reverse();
        } else {
            LinkedList<int> copy(ours);  // copy ctor: must equal the original, and be independent
            if (!(copy == ours)) all_match = false;
            copy.push_back(-1);
            if (copy == ours) all_match = false;
        }
        if (!oracle.empty()) {
            if (ours.front() != oracle.front() || ours.back() != oracle.back()) all_match = false;
        }
        if (step % 25 == 0 && !equal_forward_and_backward()) all_match = false;
    }
    CHECK(all_match);
    CHECK(equal_forward_and_backward());
}

static void test_linked_list_rule_of_five_and_lifetimes() {
    {
        LinkedList<Tracked> a;
        for (int i = 0; i < 30; ++i) a.emplace_back(i);
        CHECK(Tracked::live == 30);
        LinkedList<Tracked> copy(a);
        CHECK(Tracked::live == 60);
        LinkedList<Tracked> moved(std::move(a));
        CHECK(a.empty() && moved.size() == 30);  // NOLINT
        CHECK(Tracked::live == 60);
        LinkedList<Tracked> x;
        x = copy;
        x = std::move(moved);
        x = x;  // self assignment
        CHECK(x.size() == 30 && x.front().id == 0 && x.back().id == 29);
        x.pop_front();
        x.pop_back();
        CHECK(Tracked::live == 30 + 28);
    }
    CHECK(Tracked::live == 0);
}

static void test_linked_list_iterators() {
    LinkedList<int> l{1, 2, 3, 4};
    LinkedList<int>::const_iterator c = l.begin();  // iterator -> const_iterator conversion
    CHECK(*c == 1);
    auto it = l.begin();
    ++it;
    it = l.insert(it, 99);  // insert before 2
    CHECK(*it == 99);
    ++it;
    CHECK(*it == 2);
    it = l.erase(l.begin());
    CHECK(*it == 99 && l.front() == 99 && l.size() == 4);
    LinkedList<int> empty;
    CHECK(empty.begin() == empty.end());
    empty.push_front(5);
    CHECK(empty.front() == 5 && empty.back() == 5);
    empty.pop_back();
    CHECK(empty.empty() && empty.begin() == empty.end());
}

// =============================== HashMap ===============================

struct ConstantHash {  // the worst legal hash: everything collides
    std::size_t operator()(int) const noexcept { return 42; }
};

template <class Map, class Oracle>
static bool maps_equal(const Map& ours, const Oracle& oracle) {
    if (ours.size() != oracle.size()) return false;
    std::size_t visited = 0;
    for (const auto& kv : ours) {  // iteration must visit every entry exactly once
        auto found = oracle.find(kv.first);
        if (found == oracle.end() || found->second != kv.second) return false;
        ++visited;
    }
    if (visited != oracle.size()) return false;
    for (const auto& kv : oracle) {
        if (!ours.contains(kv.first)) return false;
        if (ours.at(kv.first) != kv.second) return false;
    }
    return true;
}

static void test_hash_map_oracle_ints() {
    std::mt19937 rng(99);
    HashMap<int, int> ours;
    std::unordered_map<int, int> oracle;
    bool all_match = true;
    bool load_ok = true;
    for (int step = 0; step < 50000; ++step) {
        const int key = static_cast<int>(rng() % 2000);
        const int value = static_cast<int>(rng());
        switch (rng() % 6) {
            case 0: {
                const bool inserted = ours.insert_or_assign(key, value);
                const bool inserted_oracle = oracle.insert_or_assign(key, value).second;
                if (inserted != inserted_oracle) all_match = false;
                break;
            }
            case 1: {
                const bool inserted = ours.insert(key, value).second;  // does NOT overwrite
                const bool inserted_oracle = oracle.insert({key, value}).second;
                if (inserted != inserted_oracle) all_match = false;
                break;
            }
            case 2:
                if (ours.erase(key) != (oracle.erase(key) == 1)) all_match = false;
                break;
            case 3:
                if (ours[key] != oracle[key]) all_match = false;  // inserts 0 when absent, on both
                break;
            case 4: {
                auto it = ours.find(key);
                auto ref = oracle.find(key);
                if ((it == ours.end()) != (ref == oracle.end())) all_match = false;
                else if (it != ours.end() && it->second != ref->second) all_match = false;
                break;
            }
            default:
                if (ours.contains(key) != (oracle.count(key) == 1)) all_match = false;
                break;
        }
        if (ours.size() != oracle.size()) all_match = false;
        if (ours.size() > 0 && ours.load_factor() > HashMap<int, int>::max_load_factor()) load_ok = false;
        if (step % 5000 == 0 && !maps_equal(ours, oracle)) all_match = false;
    }
    CHECK(all_match);
    CHECK(load_ok);
    CHECK(maps_equal(ours, oracle));
    CHECK(ours.rehash_count() > 0);
}

static void test_hash_map_oracle_strings() {
    std::mt19937 rng(2024);
    HashMap<std::string, std::size_t> ours;
    std::unordered_map<std::string, std::size_t> oracle;
    bool all_match = true;
    for (int step = 0; step < 20000; ++step) {
        const std::string key = "word-" + std::to_string(rng() % 1500);
        if (rng() % 3 == 0) {
            if (ours.erase(key) != (oracle.erase(key) == 1)) all_match = false;
        } else {
            ours[key] += 1;  // the classic word-count idiom
            oracle[key] += 1;
        }
    }
    CHECK(all_match);
    CHECK(maps_equal(ours, oracle));
}

static void test_hash_map_worst_case_hash_still_correct() {
    HashMap<int, int, ConstantHash> ours;
    std::unordered_map<int, int> oracle;
    std::mt19937 rng(5);
    for (int i = 0; i < 1500; ++i) {
        const int key = static_cast<int>(rng() % 600);
        ours.insert_or_assign(key, i);
        oracle.insert_or_assign(key, i);
        if (i % 7 == 0) {
            const int dead = static_cast<int>(rng() % 600);
            ours.erase(dead);
            oracle.erase(dead);
        }
    }
    CHECK(maps_equal(ours, oracle));
    CHECK(ours.longest_chain() == ours.size());  // all in ONE chain: a linked list in disguise
}

static void test_hash_map_rule_of_five_iterators_and_lifetimes() {
    {
        HashMap<int, Tracked> m;
        for (int i = 0; i < 200; ++i) m.insert(i, Tracked(i));
        CHECK(Tracked::live == 200);
        HashMap<int, Tracked> copy(m);
        CHECK(Tracked::live == 400);
        CHECK(copy.size() == 200 && copy.at(150).id == 150);
        copy.at(150).id = -1;
        CHECK(m.at(150).id == 150);  // deep copy
        HashMap<int, Tracked> moved(std::move(m));
        CHECK(m.size() == 0 && m.begin() == m.end() && moved.size() == 200);  // NOLINT
        CHECK(Tracked::live == 400);
        HashMap<int, Tracked> x;
        x = copy;
        x = std::move(moved);
        x = x;  // self assignment
        CHECK(x.size() == 200);
        for (int i = 0; i < 200; i += 2) x.erase(i);
        CHECK(x.size() == 100);
        CHECK(Tracked::live == 200 + 100);  // copy (200) + x (100)
        x.clear();
        CHECK(x.empty() && Tracked::live == 200);
        x.insert(1, Tracked(1));  // still usable after clear()
        CHECK(x.contains(1));
    }
    CHECK(Tracked::live == 0);

    HashMap<int, int> m;
    CHECK(m.begin() == m.end() && !m.contains(1) && m.erase(1) == false);  // empty map, no buckets yet
    m.insert(1, 10);
    HashMap<int, int>::const_iterator ci = m.begin();  // iterator -> const_iterator
    CHECK(ci->first == 1 && ci->second == 10);
    for (auto& kv : m) kv.second += 1;  // mutable iteration
    CHECK(m.at(1) == 11);
    bool threw = false;
    try {
        (void)m.at(2);
    } catch (const std::out_of_range&) {
        threw = true;
    }
    CHECK(threw);
    CHECK(!m.insert(1, 500).second && m.at(1) == 11);  // insert never overwrites
    CHECK(!m.insert_or_assign(1, 500) && m.at(1) == 500);
}

static void test_hash_map_references_survive_rehash() {
    HashMap<int, int> m;
    m.insert(0, 123);
    int& ref = m.at(0);
    const std::size_t buckets_before = m.bucket_count();
    for (int i = 1; i < 1000; ++i) m.insert(i, i);
    CHECK(m.bucket_count() > buckets_before);  // it DID rehash...
    CHECK(ref == 123 && &ref == &m.at(0));     // ...and nodes did not move
}

// =============================== MinHeap ===============================

static void test_min_heap_oracle() {
    std::mt19937 rng(31337);
    MinHeap<int> ours;
    std::priority_queue<int, std::vector<int>, std::greater<int>> oracle;
    bool all_match = true;
    for (int step = 0; step < 30000; ++step) {
        if (oracle.empty() || rng() % 100 < 60) {
            const int v = static_cast<int>(rng() % 5000) - 2500;  // duplicates and negatives on purpose
            ours.push(v);
            oracle.push(v);
        } else {
            if (ours.top() != oracle.top()) all_match = false;
            const int a = ours.pop();
            const int b = oracle.top();
            oracle.pop();
            if (a != b) all_match = false;
        }
        if (ours.size() != oracle.size()) all_match = false;
    }
    while (!oracle.empty()) {  // drain: must come out in exactly the same sorted order
        if (ours.pop() != oracle.top()) all_match = false;
        oracle.pop();
    }
    CHECK(all_match);
    CHECK(ours.empty());
}

static void test_min_heap_heapify_and_heapsort_and_comparators() {
    std::mt19937 rng(8);
    DynamicArray<int> items;
    std::vector<int> expected;
    for (int i = 0; i < 5000; ++i) {
        const int v = static_cast<int>(rng() % 100000);
        items.push_back(v);
        expected.push_back(v);
    }
    std::sort(expected.begin(), expected.end());
    MinHeap<int> heap(std::move(items));  // O(n) heapify
    CHECK(heap.size() == 5000);
    bool sorted = true;
    for (int v : expected) sorted = sorted && heap.pop() == v;  // heap sort
    CHECK(sorted && heap.empty());

    MinHeap<int, std::greater<int>> max_heap{3, 9, 1, 7};  // std::greater turns it into a MAX-heap
    CHECK(max_heap.top() == 9);
    MinHeap<std::string> words{"pear", "apple", "fig"};
    CHECK(words.top() == "apple");

    bool threw = false;
    try {
        MinHeap<int> empty;
        (void)empty.pop();
    } catch (const std::out_of_range&) {
        threw = true;
    }
    CHECK(threw);

    {
        MinHeap<Tracked, std::function<bool(const Tracked&, const Tracked&)>> tracked(
            [](const Tracked& a, const Tracked& b) { return a.id < b.id; });
        for (int i = 0; i < 100; ++i) tracked.push(Tracked(100 - i));
        CHECK(Tracked::live == 100);
        CHECK(tracked.top().id == 1);
        MinHeap<Tracked, std::function<bool(const Tracked&, const Tracked&)>> copy = tracked;
        CHECK(Tracked::live == 200);
        (void)tracked.pop();
        CHECK(Tracked::live == 199);
    }
    CHECK(Tracked::live == 0);
}

int main() {
    std::printf("Running tests for the from-scratch data structures (seeded std::mt19937)\n");
    RUN(test_dynamic_array_oracle);
    RUN(test_dynamic_array_strings_and_aliasing);
    RUN(test_dynamic_array_rule_of_five_and_lifetimes);
    RUN(test_dynamic_array_bounds_and_exceptions);
    RUN(test_linked_list_oracle);
    RUN(test_linked_list_rule_of_five_and_lifetimes);
    RUN(test_linked_list_iterators);
    RUN(test_hash_map_oracle_ints);
    RUN(test_hash_map_oracle_strings);
    RUN(test_hash_map_worst_case_hash_still_correct);
    RUN(test_hash_map_rule_of_five_iterators_and_lifetimes);
    RUN(test_hash_map_references_survive_rehash);
    RUN(test_min_heap_oracle);
    RUN(test_min_heap_heapify_and_heapsort_and_comparators);
    std::printf("%d checks, %d failed\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
