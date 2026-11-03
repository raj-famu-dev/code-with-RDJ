// Tags: #Cpp #Concurrency #SystemsProgramming #MutexLockGuard | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Protecting shared data with std::mutex: lock_guard, unique_lock,
 * scoped_lock, and deadlock avoidance. The UNLOCKED data race is described in
 * the walkthrough only; this file never runs it, so its output is deterministic.
 * Compile with -pthread.
 */
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

// A counter whose data is only reachable while holding its mutex.
class SafeCounter {
public:
    void increment() {
        std::lock_guard<std::mutex> lock(mutex_);  // locks now, unlocks at end of scope (RAII)
        ++value_;
    }
    long get() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return value_;
    }

private:
    mutable std::mutex mutex_;  // mutable so const methods can lock it
    long value_ = 0;
};

struct Account {
    std::mutex m;
    long balance;
    explicit Account(long b) : balance(b) {}
};

// Moves money between two accounts. scoped_lock locks BOTH mutexes using a
// deadlock-avoidance algorithm, so the order of arguments does not matter.
void transfer(Account& from, Account& to, long amount) {
    std::scoped_lock lock(from.m, to.m);
    from.balance -= amount;
    to.balance += amount;
}

int main() {
    // ===== SECTION 1: lock_guard AND A DETERMINISTIC TOTAL =====
    std::cout << "===== SECTION 1: lock_guard AND A DETERMINISTIC TOTAL =====\n";
    SafeCounter counter;
    constexpr int kThreads = 4;
    constexpr int kPerThread = 50000;
    {
        std::vector<std::thread> pool;
        for (int t = 0; t < kThreads; ++t) {
            pool.emplace_back([&counter] {
                for (int i = 0; i < kPerThread; ++i) counter.increment();
            });
        }
        for (auto& th : pool) th.join();
    }
    std::cout << kThreads << " threads x " << kPerThread << " increments = " << counter.get()
              << " (expected " << kThreads * kPerThread << ")\n";
    std::cout << "The result is the same every run because each ++value_ happens while holding the mutex.\n";
    std::cout << "(The UNLOCKED version is described in the walkthrough; it is a data race and is not run here.)\n";

    // ===== SECTION 2: unique_lock =====
    std::cout << "===== SECTION 2: unique_lock =====\n";
    std::mutex m;
    int shared = 0;
    {
        std::unique_lock<std::mutex> lock(m);  // locked on construction
        shared = 1;
        std::cout << "owns_lock while inside: " << std::boolalpha << lock.owns_lock() << "\n";
        lock.unlock();                         // can release early, unlike lock_guard
        std::cout << "owns_lock after unlock(): " << lock.owns_lock() << "\n";
        lock.lock();                           // and re-acquire
        shared = 2;
    }  // destructor unlocks only if it still owns the lock
    std::cout << "shared = " << shared << "\n";
    {
        std::unique_lock<std::mutex> deferred(m, std::defer_lock);  // construct WITHOUT locking
        std::cout << "defer_lock owns_lock: " << deferred.owns_lock() << "\n";
        if (deferred.try_lock()) std::cout << "try_lock succeeded because nobody holds the mutex\n";
    }
    {
        std::lock_guard<std::mutex> holder(m);
        // try_lock from ANOTHER thread, because locking a std::mutex twice in one thread is undefined behaviour.
        bool got = true;
        std::thread other([&] {
            got = m.try_lock();
            if (got) m.unlock();
        });
        other.join();
        std::cout << "try_lock from another thread while main holds the mutex: " << got << "\n";
    }
    std::cout << "TRAP: locking a std::mutex you already hold in the same thread is undefined behaviour (usually a hang).\n";

    // ===== SECTION 3: scoped_lock AND DEADLOCK AVOIDANCE =====
    std::cout << "===== SECTION 3: scoped_lock AND DEADLOCK AVOIDANCE =====\n";
    Account alice(1000), bob(1000);
    {
        std::thread t1([&] {
            for (int i = 0; i < 20000; ++i) transfer(alice, bob, 1);
        });
        std::thread t2([&] {
            for (int i = 0; i < 20000; ++i) transfer(bob, alice, 1);  // opposite order on purpose
        });
        t1.join();
        t2.join();
    }
    std::cout << "alice=" << alice.balance << " bob=" << bob.balance << " total=" << alice.balance + bob.balance
              << " (opposite-direction transfers did not deadlock)\n";
    std::cout << "TRAP: with two separate lock_guards (lock from, then lock to), thread 1 can hold A and wait for B\n"
                 "      while thread 2 holds B and waits for A: a deadlock. scoped_lock(a, b) locks both atomically.\n";
    std::cout << "Other rule: if you must lock several mutexes by hand, always lock them in one global order.\n";

    // ===== SECTION 4: KEEP CRITICAL SECTIONS SMALL =====
    std::cout << "===== SECTION 4: KEEP CRITICAL SECTIONS SMALL =====\n";
    std::mutex log_mutex;
    std::vector<std::string> log;
    {
        std::vector<std::thread> pool;
        for (int t = 0; t < 4; ++t) {
            pool.emplace_back([&log_mutex, &log, t] {
                std::string line = "worker " + std::to_string(t) + " done";  // slow work stays OUTSIDE the lock
                std::lock_guard<std::mutex> lock(log_mutex);
                log.push_back(std::move(line));                              // only the shared write is locked
            });
        }
        for (auto& th : pool) th.join();
    }
    std::cout << "log has " << log.size() << " entries (order depends on scheduling, so we do not print it)\n";
    return 0;
}
