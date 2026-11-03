// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// Demo of the four from-scratch data structures. Everything printed below is a deterministic COUNT
// measured by instrumented types (copies, moves, rehashes, chain lengths, comparisons) from seeded input.
// No timings are printed: timings vary per machine and are not results of this demo.

#include <cmath>
#include <cstdio>
#include <functional>
#include <random>
#include <string>

#include "dynamic_array.hpp"
#include "hash_map.hpp"
#include "linked_list.hpp"
#include "min_heap.hpp"

// Counts how often an element is copied or moved. `Noexcept` controls whether the move constructor is noexcept.
template <bool Noexcept>
struct Counted {
    static inline long copies = 0;
    static inline long moves = 0;
    static void reset() { copies = moves = 0; }
    int id = 0;
    explicit Counted(int i = 0) : id(i) {}
    Counted(const Counted& o) : id(o.id) { ++copies; }
    Counted(Counted&& o) noexcept(Noexcept) : id(o.id) { ++moves; }
    Counted& operator=(const Counted& o) {
        id = o.id;
        ++copies;
        return *this;
    }
    Counted& operator=(Counted&& o) noexcept(Noexcept) {
        id = o.id;
        ++moves;
        return *this;
    }
};

// A comparator that counts how many comparisons the heap makes.
struct CountingLess {
    static inline long comparisons = 0;
    bool operator()(int a, int b) const {
        ++comparisons;
        return a < b;
    }
};

struct ConstantHash {
    std::size_t operator()(int) const noexcept { return 7; }
};

static void section(const char* title) { std::printf("\n===== %s =====\n", title); }

int main() {
    std::printf("Data structures from scratch: demo (all numbers are counts measured on this run)\n");

    // ===== SECTION 1: DynamicArray growth =====
    section("SECTION 1: DynamicArray growth (1000 push_back calls)");
    {
        DynamicArray<int> a;
        std::size_t last_capacity = 0;
        std::string growth;
        for (int i = 0; i < 1000; ++i) {
            a.push_back(i);
            if (a.capacity() != last_capacity) {
                last_capacity = a.capacity();
                growth += (growth.empty() ? "" : " -> ") + std::to_string(last_capacity);
            }
        }
        std::printf("capacity changes (measurement): %s\n", growth.c_str());
        std::printf("size=%zu capacity=%zu reallocations=%zu\n", a.size(), a.capacity(), a.reallocation_count());
    }
    {
        Counted<true>::reset();
        DynamicArray<Counted<true>> a;
        const Counted<true> proto(1);
        for (int i = 0; i < 1000; ++i) a.push_back(proto);
        std::printf("noexcept move:  copies=%ld (one per add) moves=%ld (relocation) moves per add=%.3f\n", Counted<true>::copies,
                    Counted<true>::moves, static_cast<double>(Counted<true>::moves) / 1000.0);
    }
    {
        Counted<false>::reset();
        DynamicArray<Counted<false>> a;
        const Counted<false> proto(1);
        for (int i = 0; i < 1000; ++i) a.push_back(proto);
        std::printf("throwing move:  copies=%ld moves=%ld   <- TRAP: without noexcept, relocation COPIES instead of moving\n",
                    Counted<false>::copies, Counted<false>::moves);
    }

    // ===== SECTION 2: array vs linked list, inserting at the front =====
    section("SECTION 2: insert 1000 items at the FRONT (array shifts, list relinks)");
    {
        Counted<true>::reset();
        DynamicArray<Counted<true>> a;
        for (int i = 0; i < 1000; ++i) a.insert(0, Counted<true>(i));
        std::printf("DynamicArray: element moves=%ld (each insert shifts the whole tail; n(n-1)/2 = %d shifts for n=1000, plus relocation moves)\n",
                    Counted<true>::moves, 1000 * 999 / 2);
        Counted<true>::reset();
        LinkedList<Counted<true>> l;
        for (int i = 0; i < 1000; ++i) l.push_front(Counted<true>(i));
        std::printf("LinkedList:   element copies=%ld moves=%ld (nodes are linked, elements never shift)\n", Counted<true>::copies,
                    Counted<true>::moves);
    }
    {
        LinkedList<int> l{1, 2, 3, 4, 5};
        auto it = l.begin();
        ++it;
        ++it;
        l.insert(it, 99);
        l.reverse();
        std::string text;
        for (int v : l) text += std::to_string(v) + " ";
        std::printf("after insert(99 before 3) and reverse(): %s\n", text.c_str());
    }

    // ===== SECTION 3: HashMap =====
    section("SECTION 3: HashMap (separate chaining, rehash at load factor 0.75)");
    {
        HashMap<int, int> m;
        std::string trace;
        std::size_t last = 0;
        for (int i = 0; i < 10000; ++i) {
            m.insert(i, i * i);
            if (m.bucket_count() != last) {
                last = m.bucket_count();
                trace += (trace.empty() ? "" : " -> ") + std::to_string(last);
            }
        }
        std::printf("bucket count after each rehash (measurement): %s\n", trace.c_str());
        std::printf("10000 sequential int keys: size=%zu buckets=%zu in_use=%zu load=%.3f rehashes=%zu longest_chain=%zu\n", m.size(),
                    m.bucket_count(), m.buckets_in_use(), m.load_factor(), m.rehash_count(), m.longest_chain());
    }
    {
        std::mt19937 rng(2024);
        HashMap<int, int> m;
        for (int i = 0; i < 10000; ++i) m.insert_or_assign(static_cast<int>(rng()), i);
        std::printf("10000 seeded random int keys: size=%zu buckets=%zu in_use=%zu longest_chain=%zu\n", m.size(), m.bucket_count(),
                    m.buckets_in_use(), m.longest_chain());
    }
    {
        HashMap<int, int> m;
        for (int i = 0; i < 2000; ++i) m.insert(i * 1024, i);  // keys that differ only in HIGH bits
        std::printf("2000 keys that are multiples of 1024: buckets=%zu in_use=%zu longest_chain=%zu\n", m.bucket_count(),
                    m.buckets_in_use(), m.longest_chain());
    }
    {
        HashMap<int, int, ConstantHash> bad;
        for (int i = 0; i < 1000; ++i) bad.insert(i, i);
        std::printf("1000 keys, a hash that always returns 7: buckets=%zu in_use=%zu longest_chain=%zu   <- a linked list in disguise\n",
                    bad.bucket_count(), bad.buckets_in_use(), bad.longest_chain());
        std::printf("   still correct: contains(999)=%d contains(1000)=%d\n", bad.contains(999) ? 1 : 0, bad.contains(1000) ? 1 : 0);
    }
    {
        HashMap<std::string, int> counts;
        for (const char* w : {"to", "be", "or", "not", "to", "be"}) ++counts[w];
        std::printf("word count via operator[]: to=%d be=%d or=%d not=%d size=%zu\n", counts.at("to"), counts.at("be"), counts.at("or"),
                    counts.at("not"), counts.size());
    }

    // ===== SECTION 4: MinHeap =====
    section("SECTION 4: MinHeap (binary heap in an array)");
    {
        std::mt19937 rng(42);
        MinHeap<int> heap;
        std::string drained;
        for (int i = 0; i < 12; ++i) heap.push(static_cast<int>(rng() % 100));
        while (!heap.empty()) drained += std::to_string(heap.pop()) + " ";
        std::printf("12 seeded random ints popped in order: %s\n", drained.c_str());
    }
    {
        std::mt19937 rng(7);
        const int n = 1000;
        MinHeap<int, CountingLess> heap;
        CountingLess::comparisons = 0;
        for (int i = 0; i < n; ++i) heap.push(static_cast<int>(rng()));
        const long push_comparisons = CountingLess::comparisons;
        CountingLess::comparisons = 0;
        while (!heap.empty()) (void)heap.pop();
        const long pop_comparisons = CountingLess::comparisons;
        std::printf("n=%d: comparisons for %d pushes=%ld, for %d pops=%ld (reference n*log2(n)=%.0f)\n", n, n, push_comparisons, n,
                    pop_comparisons, n * std::log2(static_cast<double>(n)));

        DynamicArray<int> items;
        std::mt19937 rng2(7);
        for (int i = 0; i < n; ++i) items.push_back(static_cast<int>(rng2()));
        CountingLess::comparisons = 0;
        MinHeap<int, CountingLess> built(std::move(items));
        std::printf("heapify of the same %d items: comparisons=%ld (heapify is O(n); compare with the push count above)\n", n, CountingLess::comparisons);
    }
    std::printf("\nDone.\n");
    return 0;
}
