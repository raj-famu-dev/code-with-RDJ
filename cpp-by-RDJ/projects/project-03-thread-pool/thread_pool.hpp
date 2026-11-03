// Tags: #Cpp #Project #ThreadPool #Concurrency | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
//
// ThreadPool: a fixed set of worker threads (std::jthread) that pull tasks from one shared queue.
//
//   submit(f, args...)   queues f(args...) and returns a std::future<R> for its result (or its exception)
//   shutdown()           graceful: stop accepting new work, let the workers FINISH everything already queued, join
//   discard_pending()    drop tasks that have not started; their futures throw std::future_error (broken_promise)
//   ~ThreadPool()        calls shutdown(), so leaving the scope never leaves threads running or tasks unrun
//
// How the pieces fit:
//   * one std::mutex guards the queue and the `accepting_` flag
//   * std::condition_variable_any::wait(lock, stop_token, predicate) lets an idle worker sleep until there is
//     a task OR a stop is requested (jthread::request_stop wakes it, so there is no lost wake-up)
//   * a worker exits only when a stop was requested AND the queue is empty: that is the "graceful drain"
//   * std::packaged_task catches any exception thrown by the task and stores it in the future, so a failing
//     task never kills a worker; future.get() rethrows it in the caller
//
// Not provided (on purpose, to stay small): work stealing, priorities, task cancellation, resizing.
#pragma once

#include <condition_variable>
#include <cstddef>
#include <functional>
#include <future>
#include <memory>
#include <mutex>
#include <queue>
#include <stdexcept>
#include <stop_token>
#include <thread>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

class ThreadPool {
public:
    // threads == 0 means "ask the hardware"; hardware_concurrency() may itself return 0, so use at least 1.
    explicit ThreadPool(std::size_t threads = std::thread::hardware_concurrency()) {
        if (threads == 0) threads = std::thread::hardware_concurrency();
        if (threads == 0) threads = 1;
        workers_.reserve(threads);
        for (std::size_t i = 0; i < threads; ++i) {
            workers_.emplace_back([this](std::stop_token stop) { worker_loop(stop); });
        }
    }

    ThreadPool(const ThreadPool&) = delete;  // threads and a mutex cannot be copied or moved sensibly
    ThreadPool& operator=(const ThreadPool&) = delete;

    ~ThreadPool() { shutdown(); }

    template <class F, class... Args>
    [[nodiscard]] auto submit(F&& f, Args&&... args) -> std::future<std::invoke_result_t<std::decay_t<F>, std::decay_t<Args>...>> {
        using Result = std::invoke_result_t<std::decay_t<F>, std::decay_t<Args>...>;
        // packaged_task is move-only; std::function needs copyable, so the task lives behind a shared_ptr.
        auto task = std::make_shared<std::packaged_task<Result()>>(
            [fn = std::forward<F>(f), tup = std::make_tuple(std::forward<Args>(args)...)]() mutable -> Result {
                return std::apply(std::move(fn), std::move(tup));
            });
        std::future<Result> future = task->get_future();
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (!accepting_) throw std::runtime_error("ThreadPool::submit: the pool has been shut down");
            tasks_.emplace([task]() { (*task)(); });
        }
        cv_.notify_one();
        return future;
    }

    // Graceful shutdown. Safe to call more than once (and from the destructor).
    void shutdown() {
        std::lock_guard<std::mutex> shutdown_guard(shutdown_mutex_);  // two threads must not join the same thread
        {
            std::lock_guard<std::mutex> lock(mutex_);
            accepting_ = false;  // from now on submit() throws
        }
        for (std::jthread& w : workers_) w.request_stop();  // wakes sleeping workers; they drain the queue, then exit
        for (std::jthread& w : workers_) {
            if (w.joinable()) w.join();
        }
    }

    // Remove every queued task that no worker has started. Returns how many were dropped.
    // Each dropped task's future throws std::future_error(broken_promise) from get().
    std::size_t discard_pending() {
        std::queue<std::function<void()>> dropped;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            dropped.swap(tasks_);
        }
        return dropped.size();  // the tasks are destroyed here, outside the lock, which breaks their promises
    }

    std::size_t thread_count() const noexcept { return workers_.size(); }

    std::size_t pending() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return tasks_.size();
    }

private:
    void worker_loop(std::stop_token stop) {
        for (;;) {
            std::function<void()> task;
            {
                std::unique_lock<std::mutex> lock(mutex_);
                // Sleeps until the queue is non-empty or a stop is requested. Returns with the queue still empty
                // only when stopping.
                cv_.wait(lock, stop, [this] { return !tasks_.empty(); });
                if (tasks_.empty()) return;  // stop requested and nothing left to drain
                task = std::move(tasks_.front());
                tasks_.pop();
            }
            task();  // run OUTSIDE the lock so other workers can take tasks meanwhile
        }
    }

    mutable std::mutex mutex_;
    std::condition_variable_any cv_;
    std::queue<std::function<void()>> tasks_;
    bool accepting_ = true;
    std::mutex shutdown_mutex_;
    std::vector<std::jthread> workers_;  // declared last: destroyed first, after the members the workers use are still alive
};
