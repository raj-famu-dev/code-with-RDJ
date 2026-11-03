// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// Minimal reproducer used to decide whether the ThreadSanitizer reports in this project come from ThreadPool
// or from the standard library. It does NOT use ThreadPool: just std::promise, std::future and std::thread.
// A worker stores an exception into a promise; the main thread rethrows it with get() and prints e.what().
// Build it with -fsanitize=thread (see `make tsan-repro`). With the GCC 13 libstdc++ on this machine, TSan reports
// a data race around exception_ptr / the exception object even though this code is correct.
// Always exits 0 itself; the verdict is whatever TSan prints (and its own exit code, 66, when it reports).

#include <cstdio>
#include <exception>
#include <future>
#include <stdexcept>
#include <thread>

int main() {
    for (int i = 0; i < 200; ++i) {
        std::promise<int> promise;
        std::future<int> future = promise.get_future();
        std::thread worker([p = std::move(promise)]() mutable {
            try {
                throw std::runtime_error("task failed on purpose");
            } catch (...) {
                p.set_exception(std::current_exception());
            }
        });
        try {
            (void)future.get();
        } catch (const std::runtime_error& e) {
            char text[64];
            std::snprintf(text, sizeof text, "%s", e.what());  // read the message, as the demo does with printf
            if (i == 0) std::printf("caught: %s\n", text);
        }
        worker.join();
    }
    std::printf("tsan_repro finished 200 rounds\n");
    return 0;
}
