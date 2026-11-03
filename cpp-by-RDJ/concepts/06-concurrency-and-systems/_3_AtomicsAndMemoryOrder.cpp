// Tags: #Cpp #Concurrency #SystemsProgramming #AtomicsMemoryOrder | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * std::atomic counters, compare_exchange (the lock-free "try to update"
 * primitive), and memory ordering: relaxed vs acquire/release, explained with
 * a publish-data-then-set-flag example. Compile with -pthread.
 */
#include <atomic>
#include <iostream>
#include <thread>
#include <vector>

// A lock-free "keep the maximum" using a compare_exchange retry loop.
void update_max(std::atomic<int>& target, int candidate) {
    int current = target.load(std::memory_order_relaxed);
    // If target still equals 'current', store 'candidate'. If another thread
    // changed it, 'current' is refreshed with the new value and we retry.
    while (current < candidate &&
           !target.compare_exchange_weak(current, candidate, std::memory_order_relaxed)) {
    }
}

// A tiny spin lock built from atomic_flag, to show acquire/release in use.
class SpinLock {
public:
    void lock() {
        while (flag_.test_and_set(std::memory_order_acquire)) {
            std::this_thread::yield();
        }
    }
    void unlock() { flag_.clear(std::memory_order_release); }

private:
    std::atomic_flag flag_ = ATOMIC_FLAG_INIT;
};

int main() {
    std::cout << std::boolalpha;
    constexpr int kThreads = 4;
    constexpr int kPerThread = 100000;

    // ===== SECTION 1: ATOMIC COUNTER =====
    std::cout << "===== SECTION 1: ATOMIC COUNTER =====\n";
    std::atomic<long> counter{0};
    {
        std::vector<std::thread> pool;
        for (int t = 0; t < kThreads; ++t)
            pool.emplace_back([&counter] {
                for (int i = 0; i < kPerThread; ++i) counter.fetch_add(1, std::memory_order_relaxed);
            });
        for (auto& th : pool) th.join();
    }
    std::cout << kThreads << " threads x " << kPerThread << " fetch_add = " << counter.load() << " (expected "
              << kThreads * kPerThread << ")\n";
    std::cout << "A plain 'long' with ++ in the same loops would be a data race (undefined behaviour); not run here.\n";
    std::atomic<int> a{5};
    std::cout << "operators work too: ++a -> " << ++a << ", a += 10 -> " << (a += 10) << ", exchange(0) returned "
              << a.exchange(0) << ", now " << a.load() << "\n";
    std::cout << "std::atomic<int> is lock free on this machine: " << std::atomic<int>::is_always_lock_free << "\n";

    // ===== SECTION 2: compare_exchange =====
    std::cout << "===== SECTION 2: compare_exchange =====\n";
    std::atomic<int> value{10};
    int expected = 10;
    bool ok = value.compare_exchange_strong(expected, 20);
    std::cout << "expected 10, actual 10 -> success=" << ok << ", value=" << value.load() << "\n";
    expected = 10;  // stale guess
    ok = value.compare_exchange_strong(expected, 30);
    std::cout << "expected 10, actual 20 -> success=" << ok << ", value=" << value.load()
              << ", expected was refreshed to " << expected << "\n";
    std::atomic<int> maximum{0};
    {
        std::vector<std::thread> pool;
        for (int t = 0; t < kThreads; ++t)
            pool.emplace_back([&maximum, t] {
                for (int i = 0; i < 1000; ++i) update_max(maximum, t * 1000 + i);
            });
        for (auto& th : pool) th.join();
    }
    std::cout << "lock-free maximum over all threads = " << maximum.load() << " (expected 3999)\n";
    std::cout << "TRAP: 'if (x.load() == 0) x.store(1);' is NOT atomic as a pair; another thread can slip in between."
                 " Use compare_exchange.\n";
    std::cout << "compare_exchange_weak may fail spuriously (so use it in a loop); _strong does not.\n";

    // ===== SECTION 3: ACQUIRE / RELEASE: PUBLISHING DATA =====
    std::cout << "===== SECTION 3: ACQUIRE / RELEASE: PUBLISHING DATA =====\n";
    int payload = 0;                  // ordinary, non-atomic data
    std::atomic<bool> ready{false};   // the flag that guards it
    std::thread producer([&] {
        payload = 1234;                                    // 1. write the data
        ready.store(true, std::memory_order_release);      // 2. RELEASE: everything above becomes visible to an acquirer
    });
    std::thread consumer([&] {
        while (!ready.load(std::memory_order_acquire)) {   // ACQUIRE: pairs with the release store
            std::this_thread::yield();
        }
        std::cout << "consumer saw payload = " << payload << " (guaranteed, because acquire pairs with release)\n";
    });
    producer.join();
    consumer.join();
    std::cout << "With memory_order_relaxed on both sides the flag itself stays atomic, but the payload write\n"
                 "would NOT be guaranteed visible: relaxed gives atomicity without ordering.\n";

    // ===== SECTION 4: A SPIN LOCK FROM acquire/release =====
    std::cout << "===== SECTION 4: A SPIN LOCK FROM acquire/release =====\n";
    SpinLock spin;
    long protected_sum = 0;  // plain long: safe ONLY because the spin lock orders access
    {
        std::vector<std::thread> pool;
        for (int t = 0; t < kThreads; ++t)
            pool.emplace_back([&] {
                for (int i = 0; i < 20000; ++i) {
                    spin.lock();
                    ++protected_sum;
                    spin.unlock();
                }
            });
        for (auto& th : pool) th.join();
    }
    std::cout << "protected_sum = " << protected_sum << " (expected " << kThreads * 20000 << ")\n";
    std::cout << "lock = acquire, unlock = release: the unlock publishes this thread's writes to the next locker.\n";
    std::cout << "Default is memory_order_seq_cst (strongest, simplest). Reach for relaxed/acquire/release only with a reason.\n";
    return 0;
}
