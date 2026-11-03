// Tags: #Cpp #Concurrency #SystemsProgramming #ConditionVariablesProducerConsumer | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * std::condition_variable and the producer/consumer pattern: a bounded
 * blocking queue, the predicate-wait rule (spurious wakeups), and a clean
 * shutdown using a close() flag. Compile with -pthread.
 */
#include <chrono>
#include <condition_variable>
#include <cstddef>
#include <iostream>
#include <mutex>
#include <optional>
#include <queue>
#include <thread>
#include <utility>
#include <vector>

// Thread-safe queue with a maximum size. push blocks when full, pop blocks when empty.
template <class T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {}

    // Returns false if the queue was closed (item not added).
    bool push(T item) {
        std::unique_lock<std::mutex> lock(mutex_);
        not_full_.wait(lock, [this] { return queue_.size() < capacity_ || closed_; });  // predicate form
        if (closed_) return false;
        queue_.push(std::move(item));
        if (queue_.size() > max_seen_) max_seen_ = queue_.size();  // measured under the lock, inside push
        not_empty_.notify_one();
        return true;
    }

    // Returns nullopt once the queue is closed AND drained.
    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        not_empty_.wait(lock, [this] { return !queue_.empty() || closed_; });
        if (queue_.empty()) return std::nullopt;  // closed and nothing left
        T item = std::move(queue_.front());
        queue_.pop();
        not_full_.notify_one();
        return item;
    }

    void close() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            closed_ = true;
        }
        not_empty_.notify_all();  // wake EVERY waiter so they can see closed_
        not_full_.notify_all();
    }

    std::size_t max_seen() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return max_seen_;
    }

private:
    mutable std::mutex mutex_;
    std::condition_variable not_empty_;
    std::condition_variable not_full_;
    std::queue<T> queue_;
    std::size_t capacity_;
    std::size_t max_seen_ = 0;
    bool closed_ = false;
};

int main() {
    std::cout << std::boolalpha;
    // ===== SECTION 1: ONE PRODUCER, ONE CONSUMER =====
    std::cout << "===== SECTION 1: ONE PRODUCER, ONE CONSUMER =====\n";
    {
        BoundedQueue<int> q(3);
        long consumed_sum = 0;
        int consumed_count = 0;
        std::vector<int> order;
        std::thread producer([&] {
            for (int i = 1; i <= 20; ++i) {
                q.push(i);
            }
            q.close();  // tell the consumer no more data is coming
        });
        std::thread consumer([&] {
            while (auto item = q.pop()) {  // loop ends when pop returns nullopt
                consumed_sum += *item;
                ++consumed_count;
                order.push_back(*item);
            }
        });
        producer.join();
        consumer.join();
        bool in_order = true;
        for (std::size_t i = 0; i < order.size(); ++i) in_order = in_order && order[i] == static_cast<int>(i) + 1;
        std::cout << "consumed " << consumed_count << " items, sum = " << consumed_sum << " (expected 210)\n";
        std::cout << "items arrived in FIFO order: " << in_order << "\n";
        std::cout << "queue never exceeded capacity 3: " << (q.max_seen() <= 3) << "\n";
    }

    // ===== SECTION 2: MANY PRODUCERS, MANY CONSUMERS =====
    std::cout << "===== SECTION 2: MANY PRODUCERS, MANY CONSUMERS =====\n";
    {
        BoundedQueue<int> q(4);
        constexpr int kProducers = 3, kConsumers = 3, kPerProducer = 1000;
        std::mutex sum_mutex;
        long total = 0;
        int count = 0;
        std::vector<std::thread> producers, consumers;
        for (int p = 0; p < kProducers; ++p)
            producers.emplace_back([&q] {
                for (int i = 1; i <= kPerProducer; ++i) q.push(i);
            });
        for (int c = 0; c < kConsumers; ++c)
            consumers.emplace_back([&] {
                long local_sum = 0;
                int local_count = 0;
                while (auto item = q.pop()) {
                    local_sum += *item;
                    ++local_count;
                }
                std::lock_guard<std::mutex> lock(sum_mutex);
                total += local_sum;
                count += local_count;
            });
        for (auto& th : producers) th.join();  // wait for ALL producers first...
        q.close();                             // ...then close, so no item is lost
        for (auto& th : consumers) th.join();
        std::cout << "items consumed = " << count << " (expected " << kProducers * kPerProducer << ")\n";
        std::cout << "sum = " << total << " (expected " << kProducers * (kPerProducer * (kPerProducer + 1) / 2) << ")\n";
        std::cout << "Which consumer got which item varies per run, but the totals never do.\n";
    }

    // ===== SECTION 3: CLEAN SHUTDOWN =====
    std::cout << "===== SECTION 3: CLEAN SHUTDOWN =====\n";
    {
        BoundedQueue<int> q(2);
        std::optional<int> result = 7;  // sentinel to prove that pop() returned
        std::thread blocked_consumer([&] { result = q.pop(); });  // queue is empty: this blocks
        std::this_thread::sleep_for(std::chrono::milliseconds(30));
        q.close();  // wakes the blocked consumer
        blocked_consumer.join();
        std::cout << "blocked pop() woke up on close() and returned nullopt: " << !result.has_value() << "\n";
        std::cout << "push after close returns: " << q.push(1) << " (rejected)\n";
    }
    {
        BoundedQueue<int> q(1);
        q.push(1);  // fills the queue
        bool push_result = true;
        std::thread blocked_producer([&] { push_result = q.push(2); });  // full: this blocks
        std::this_thread::sleep_for(std::chrono::milliseconds(30));
        q.close();
        blocked_producer.join();
        std::cout << "blocked push() woke up on close() and returned: " << push_result << " (item dropped)\n";
        auto leftover = q.pop();
        std::cout << "close() lets consumers drain what was queued: first pop = " << leftover.value_or(-1) << "\n";
    }
    std::cout << "Shutdown order: stop producers, close(), let consumers drain, then join.\n";

    // ===== SECTION 4: THE WAIT RULES (TRAPS) =====
    std::cout << "===== SECTION 4: THE WAIT RULES (TRAPS) =====\n";
    std::cout << "1. ALWAYS wait with a predicate: cv.wait(lock, [&]{ return condition; }).\n"
                 "   A bare cv.wait(lock) can wake spuriously (no notify happened) or miss a notify sent before you waited.\n";
    std::cout << "2. Change the condition while holding the same mutex the waiter uses, or a notify can be lost.\n";
    std::cout << "3. A notify with no waiter is simply forgotten; the predicate (state), not the notify, is the truth.\n";
    std::cout << "4. Use notify_all for shutdown flags; notify_one for 'one item became available'.\n";
    return 0;
}
