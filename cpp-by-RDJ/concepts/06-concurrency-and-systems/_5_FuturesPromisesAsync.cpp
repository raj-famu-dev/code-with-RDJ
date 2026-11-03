// Tags: #Cpp #Concurrency #SystemsProgramming #FuturesPromisesAsync | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Getting results back from threads: std::async + std::future, std::promise,
 * std::packaged_task, exceptions travelling through futures, and the
 * "std::async future that is destroyed blocks" trap. Compile with -pthread.
 */
#include <chrono>
#include <exception>
#include <future>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

long sum_range(const std::vector<int>& data, std::size_t begin, std::size_t end) {
    return std::accumulate(data.begin() + static_cast<std::ptrdiff_t>(begin),
                           data.begin() + static_cast<std::ptrdiff_t>(end), 0L);
}

int risky(int x) {
    if (x < 0) throw std::invalid_argument("negative input");
    return x * 2;
}

int main() {
    std::cout << std::boolalpha;
    // ===== SECTION 1: std::async AND std::future =====
    std::cout << "===== SECTION 1: std::async AND std::future =====\n";
    std::vector<int> data(1000);
    std::iota(data.begin(), data.end(), 1);  // 1..1000
    // std::launch::async FORCES a new thread (the default policy may run it lazily on get()).
    std::future<long> first_half = std::async(std::launch::async, sum_range, std::cref(data), 0, 500);
    std::future<long> second_half = std::async(std::launch::async, sum_range, std::cref(data), 500, 1000);
    std::cout << "future valid before get(): " << first_half.valid() << "\n";
    long total = first_half.get() + second_half.get();  // get() blocks until the result is ready
    std::cout << "sum 1..1000 computed by two async tasks = " << total << " (expected 500500)\n";
    std::cout << "future valid after get(): " << first_half.valid() << " (a future's value can be taken only ONCE)\n";
    auto lazy = std::async(std::launch::deferred, [] { return 99; });  // runs on get(), in the calling thread
    std::cout << "deferred task result: " << lazy.get() << "\n";

    // ===== SECTION 2: EXCEPTIONS TRAVEL THROUGH FUTURES =====
    std::cout << "===== SECTION 2: EXCEPTIONS TRAVEL THROUGH FUTURES =====\n";
    auto good = std::async(std::launch::async, risky, 21);
    auto bad = std::async(std::launch::async, risky, -1);
    std::cout << "risky(21) -> " << good.get() << "\n";
    try {
        bad.get();  // the exception thrown in the other thread is rethrown HERE
    } catch (const std::invalid_argument& e) {
        std::cout << "get() rethrew the worker's exception: " << e.what() << "\n";
    }

    // ===== SECTION 3: std::promise =====
    std::cout << "===== SECTION 3: std::promise =====\n";
    std::promise<std::string> promise;
    std::future<std::string> from_promise = promise.get_future();
    std::thread setter([p = std::move(promise)]() mutable {
        p.set_value("value delivered through a promise");  // the producer side
    });
    std::cout << "main received: " << from_promise.get() << "\n";
    setter.join();
    std::promise<int> failing;
    auto failing_future = failing.get_future();
    std::thread failer([p = std::move(failing)]() mutable {
        try {
            throw std::runtime_error("worker could not finish");
        } catch (...) {
            p.set_exception(std::current_exception());  // ship the exception to the waiting side
        }
    });
    try {
        failing_future.get();
    } catch (const std::runtime_error& e) {
        std::cout << "promise::set_exception delivered: " << e.what() << "\n";
    }
    failer.join();
    {
        std::future<int> f;
        {
            std::promise<int> abandoned;
            f = abandoned.get_future();
        }  // promise destroyed without set_value or set_exception
        try {
            f.get();
        } catch (const std::future_error& e) {
            std::cout << "abandoned promise -> future_error, code is broken_promise: "
                      << (e.code() == std::future_errc::broken_promise) << "\n";
        }
    }

    // ===== SECTION 4: std::packaged_task =====
    std::cout << "===== SECTION 4: std::packaged_task =====\n";
    std::packaged_task<int(int, int)> task([](int a, int b) { return a * b; });  // wraps a callable + a future
    std::future<int> product = task.get_future();
    std::thread runner(std::move(task), 6, 7);  // you decide WHERE and WHEN it runs
    std::cout << "packaged_task result: " << product.get() << "\n";
    runner.join();
    std::vector<std::packaged_task<int()>> queue;  // typical use: a task queue for a thread pool
    std::vector<std::future<int>> results;
    for (int i = 1; i <= 3; ++i) {
        queue.emplace_back([i] { return i * 100; });
        results.push_back(queue.back().get_future());
    }
    for (auto& t : queue) t();  // run them (here on the main thread; a pool would run them on workers)
    std::cout << "queued tasks results:";
    for (auto& r : results) std::cout << " " << r.get();
    std::cout << "\n";

    // ===== SECTION 5: wait_for AND THE BLOCKING-DESTRUCTOR TRAP =====
    std::cout << "===== SECTION 5: wait_for AND THE BLOCKING-DESTRUCTOR TRAP =====\n";
    std::promise<int> slow_promise;
    std::future<int> slow = slow_promise.get_future();
    auto status = slow.wait_for(std::chrono::milliseconds(20));
    std::cout << "wait_for on an unfinished future -> timeout: " << (status == std::future_status::timeout) << "\n";
    slow_promise.set_value(1);
    std::cout << "wait_for after set_value -> ready: " << (slow.wait_for(std::chrono::milliseconds(20)) == std::future_status::ready) << "\n";
    std::cout << "TRAP: calling 'std::async(std::launch::async, f);' and ignoring the returned future makes the\n"
                 "      temporary future's destructor BLOCK until f finishes, so it is not 'fire and forget'.\n"
                 "      Always keep the future in a variable and call get() or wait().\n";
    auto t0 = std::chrono::steady_clock::now();
    (void)std::async(std::launch::async, [] { std::this_thread::sleep_for(std::chrono::milliseconds(60)); });  // discarded future
    auto waited = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - t0);
    std::cout << "the discarded async call blocked for at least 60 ms: " << (waited.count() >= 60)
              << " (MEASUREMENT: exact milliseconds vary and are not printed)\n";
    return 0;
}
