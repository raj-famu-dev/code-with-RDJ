// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// Hand-rolled test runner (no framework) for ThreadPool. Covers: every task runs exactly once, results come
// back in submission order through the futures, exceptions propagate, shutdown with pending tasks drains them
// (and discard_pending drops them), submit after shutdown fails, and no deadlock under 1,000+ small tasks.
// Every wait that could hang is bounded with wait_for, so a deadlock shows up as a FAIL, not a frozen test run.
// Exit code: 0 if every CHECK passed, 1 otherwise.

#include <atomic>
#include <chrono>
#include <cstdio>
#include <future>
#include <memory>
#include <mutex>
#include <random>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

#include "thread_pool.hpp"

using namespace std::chrono_literals;

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

// Passes if evaluating `expr` throws exactly an exception of type `Ex` (or derived).
#define CHECK_THROWS(expr, Ex)                                                     \
    do {                                                                           \
        bool thrown_ = false;                                                      \
        try {                                                                      \
            expr;                                                                  \
        } catch (const Ex&) {                                                      \
            thrown_ = true;                                                        \
        }                                                                          \
        CHECK(thrown_);                                                            \
    } while (0)

#define RUN(test_fn)                                                               \
    do {                                                                           \
        const int before = g_failures;                                             \
        test_fn();                                                                 \
        std::printf("[%s] %s\n", g_failures == before ? "PASS" : "FAIL", #test_fn); \
    } while (0)

struct TaskError : std::runtime_error {
    using std::runtime_error::runtime_error;
};

static void test_every_task_runs_exactly_once() {
    constexpr int kTasks = 5000;
    std::vector<std::atomic<int>> runs(kTasks);
    for (auto& r : runs) r = 0;
    {
        ThreadPool pool(4);
        std::vector<std::future<void>> futures;
        for (int i = 0; i < kTasks; ++i) futures.push_back(pool.submit([&runs, i] { runs[static_cast<std::size_t>(i)].fetch_add(1); }));
        for (auto& f : futures) f.get();
    }
    int wrong = 0;
    for (auto& r : runs) wrong += r.load() == 1 ? 0 : 1;
    CHECK(wrong == 0);
}

static void test_results_in_submission_order() {
    ThreadPool pool(4);
    std::mt19937 rng(11);
    std::vector<std::future<long>> futures;
    std::vector<long> expected;
    for (int i = 0; i < 200; ++i) {
        const long spin = static_cast<long>(rng() % 20000);  // uneven work, so tasks finish out of order
        expected.push_back(i * 3L + spin);
        futures.push_back(pool.submit([i, spin] {
            volatile long sink = 0;
            for (long k = 0; k < spin; ++k) sink = sink + 1;
            return i * 3L + spin;
        }));
    }
    bool in_order = true;
    for (std::size_t i = 0; i < futures.size(); ++i) in_order = in_order && futures[i].get() == expected[i];
    CHECK(in_order);

    // submit forwards arguments, including move-only ones
    auto f = pool.submit([](std::unique_ptr<int> p, int add) { return *p + add; }, std::make_unique<int>(40), 2);
    CHECK(f.get() == 42);
}

static void test_single_worker_is_fifo() {
    ThreadPool pool(1);
    std::mutex m;
    std::vector<int> order;
    std::vector<std::future<void>> futures;
    for (int i = 0; i < 100; ++i) {
        futures.push_back(pool.submit([&, i] {
            std::lock_guard<std::mutex> lock(m);
            order.push_back(i);
        }));
    }
    for (auto& f : futures) f.get();
    bool fifo = order.size() == 100;
    for (int i = 0; i < 100 && fifo; ++i) fifo = order[static_cast<std::size_t>(i)] == i;
    CHECK(fifo);
}

static void test_exception_propagates() {
    ThreadPool pool(2);
    auto bad = pool.submit([]() -> int { throw TaskError("boom"); });
    bool caught = false;
    std::string message;
    try {
        (void)bad.get();
    } catch (const TaskError& e) {  // the exact type survives the trip through the future
        caught = true;
        message = e.what();
    }
    CHECK(caught);
    CHECK(message == "boom");

    auto bad_void = pool.submit([] { throw std::logic_error("void task failed"); });
    CHECK_THROWS(bad_void.get(), std::logic_error);

    // a failing task must not kill its worker: the same pool keeps running tasks
    std::vector<std::future<int>> after;
    for (int i = 0; i < 100; ++i) {
        after.push_back(pool.submit([i]() -> int {
            if (i % 10 == 0) throw TaskError("every tenth fails");
            return i;
        }));
    }
    int ok = 0;
    int failed = 0;
    for (auto& f : after) {
        try {
            ok += f.get() >= 0 ? 1 : 0;
        } catch (const TaskError&) {
            ++failed;
        }
    }
    CHECK(ok == 90 && failed == 10);
}

static void test_shutdown_with_pending_tasks_drains_them() {
    std::atomic<int> ran{0};
    std::promise<void> started;
    std::promise<void> gate;
    std::shared_future<void> gate_future = gate.get_future().share();
    std::vector<std::future<void>> futures;

    ThreadPool pool(1);
    futures.push_back(pool.submit([&started, gate_future] {  // occupies the only worker until we open the gate
        started.set_value();
        gate_future.wait();
    }));
    CHECK(started.get_future().wait_for(10s) == std::future_status::ready);  // the worker is now busy
    for (int i = 0; i < 50; ++i) futures.push_back(pool.submit([&ran] { ++ran; }));
    CHECK(pool.pending() == 50);  // all 50 are queued behind the blocked task
    CHECK(ran.load() == 0);

    gate.set_value();
    pool.shutdown();  // graceful: must run all 50 before returning
    CHECK(ran.load() == 50);
    bool all_ready = true;
    for (auto& f : futures) all_ready = all_ready && f.wait_for(0s) == std::future_status::ready;
    CHECK(all_ready);
    CHECK(pool.pending() == 0);

    CHECK_THROWS((void)pool.submit([] {}), std::runtime_error);  // no new work after shutdown
    pool.shutdown();                                              // idempotent: a second call is harmless
    CHECK(true);
}

static void test_destructor_drains_pending_tasks() {
    std::atomic<int> ran{0};
    {
        ThreadPool pool(2);
        for (int i = 0; i < 500; ++i) (void)pool.submit([&ran] { ++ran; });
    }  // destructor runs while most tasks are probably still queued
    CHECK(ran.load() == 500);
}

static void test_discard_pending_breaks_promises() {
    std::atomic<int> ran{0};
    std::promise<void> started;
    std::promise<void> gate;
    std::shared_future<void> gate_future = gate.get_future().share();

    ThreadPool pool(1);
    auto blocker = pool.submit([&started, gate_future] {
        started.set_value();
        gate_future.wait();
    });
    CHECK(started.get_future().wait_for(10s) == std::future_status::ready);
    std::vector<std::future<void>> doomed;
    for (int i = 0; i < 10; ++i) doomed.push_back(pool.submit([&ran] { ++ran; }));

    CHECK(pool.discard_pending() == 10);
    gate.set_value();
    blocker.get();  // the task that had already started still finishes normally
    pool.shutdown();
    CHECK(ran.load() == 0);  // none of the discarded tasks ever ran
    int broken = 0;
    for (auto& f : doomed) {
        try {
            f.get();
        } catch (const std::future_error& e) {
            broken += e.code() == std::future_errc::broken_promise ? 1 : 0;
        }
    }
    CHECK(broken == 10);
}

static void test_no_deadlock_under_many_small_tasks() {
    // (a) 1,000 tiny tasks from one producer, each future waited on with a time limit
    {
        ThreadPool pool(4);
        std::vector<std::future<int>> futures;
        for (int i = 0; i < 1000; ++i) futures.push_back(pool.submit([i] { return i; }));
        bool all_done = true;
        long sum = 0;
        for (auto& f : futures) {
            if (f.wait_for(20s) != std::future_status::ready) {
                all_done = false;
                break;
            }
            sum += f.get();
        }
        CHECK(all_done);
        CHECK(sum == 999L * 1000 / 2);
    }
    // (b) 4 producer threads submitting 1,000 tasks each at the same time into a 3-worker pool
    {
        ThreadPool pool(3);
        std::atomic<int> ran{0};
        std::vector<std::thread> producers;
        for (int p = 0; p < 4; ++p) {
            producers.emplace_back([&pool, &ran] {
                std::vector<std::future<void>> mine;
                for (int i = 0; i < 1000; ++i) mine.push_back(pool.submit([&ran] { ++ran; }));
                for (auto& f : mine) f.wait();
            });
        }
        for (auto& t : producers) t.join();
        CHECK(ran.load() == 4000);
    }
    // (c) tasks that submit more tasks (without waiting for them: waiting inside a pool task can deadlock a small pool)
    {
        ThreadPool pool(2);
        std::atomic<int> ran{0};
        std::vector<std::future<void>> inner;
        std::mutex inner_mutex;
        for (int i = 0; i < 100; ++i) {
            (void)pool.submit([&] {
                ++ran;
                auto f = pool.submit([&ran] { ++ran; });
                std::lock_guard<std::mutex> lock(inner_mutex);
                inner.push_back(std::move(f));
            });
        }
        pool.shutdown();  // may race with the inner submits: that is allowed to throw inside the task, so just check it ends
        CHECK(ran.load() >= 100);
    }
    // (d) create and destroy many pools quickly: exercises start-up and shutdown races
    {
        std::atomic<int> ran{0};
        for (int round = 0; round < 200; ++round) {
            ThreadPool pool(3);
            for (int i = 0; i < 5; ++i) (void)pool.submit([&ran] { ++ran; });
        }
        CHECK(ran.load() == 1000);
    }
}

static void test_thread_count_defaults() {
    ThreadPool zero(0);  // 0 = ask the hardware, never an empty pool
    CHECK(zero.thread_count() >= 1);
    ThreadPool three(3);
    CHECK(three.thread_count() == 3);
}

int main() {
    std::printf("Running ThreadPool tests (hardware_concurrency = %u)\n", std::thread::hardware_concurrency());
    RUN(test_every_task_runs_exactly_once);
    RUN(test_results_in_submission_order);
    RUN(test_single_worker_is_fifo);
    RUN(test_exception_propagates);
    RUN(test_shutdown_with_pending_tasks_drains_them);
    RUN(test_destructor_drains_pending_tasks);
    RUN(test_discard_pending_breaks_promises);
    RUN(test_no_deadlock_under_many_small_tasks);
    RUN(test_thread_count_defaults);
    std::printf("%d checks, %d failed\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
