# `_4_ConditionVariablesAndProducerConsumer.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
A condition variable lets a thread sleep until another thread signals that something has changed, instead of wasting CPU in a loop. The classic use is producer/consumer: a bounded queue where producers wait when it is full and consumers wait when it is empty. The rules are strict: always wait with a predicate, always change the condition while holding the same mutex, and design an explicit shutdown (here a `close()` flag) so blocked threads can wake up and exit. Compile with `-pthread`.

## Full Line-by-Line Breakdown

### SECTION 1: ONE PRODUCER, ONE CONSUMER
`BoundedQueue<T>` holds a mutex, two condition variables (`not_full_`, `not_empty_`), a `std::queue` and a `closed_` flag. `push` waits until there is room (or the queue closes), adds the item, and wakes one consumer. `pop` waits until there is an item (or the queue closes); it returns `std::nullopt` only when the queue is closed AND empty. One producer pushes 1..20 into a queue of capacity 3, then calls `close()`. One consumer loops `while (auto item = q.pop())` until `nullopt`. The program checks the sum (210), FIFO order, and that the largest size ever seen inside `push` (measured under the lock) never exceeded 3.

Output from a real run:

```text
===== SECTION 1: ONE PRODUCER, ONE CONSUMER =====
consumed 20 items, sum = 210 (expected 210)
items arrived in FIFO order: true
queue never exceeded capacity 3: true
```

### SECTION 2: MANY PRODUCERS, MANY CONSUMERS
Three producers each push 1..1000 and three consumers pop until closed. The producers must ALL finish before `close()` is called (the `join` loop comes first), otherwise a late `push` would be rejected and items lost. Each consumer keeps local totals and adds them to the shared totals under a mutex once at the end. Which consumer gets which item varies run to run, but the count (3000) and sum (1501500) are always the same.

Output from a real run:

```text
===== SECTION 2: MANY PRODUCERS, MANY CONSUMERS =====
items consumed = 3000 (expected 3000)
sum = 1501500 (expected 1501500)
Which consumer got which item varies per run, but the totals never do.
```

### SECTION 3: CLEAN SHUTDOWN
Shutdown is where many producer/consumer programs hang. A consumer is blocked in `pop()` on an empty queue; `close()` sets the flag under the lock and then `notify_all()`s both condition variables, so the waiter re-checks its predicate, sees `closed_`, and returns `nullopt`. Likewise a producer blocked in `push()` on a full queue wakes up and gets `false` (its item is dropped). After close, items already in the queue are still delivered (the first `pop()` returns 1). The correct order is: stop producers, `close()`, let consumers drain, then join. The 30 ms sleeps only give the worker time to start waiting; the result is the same without them.

Output from a real run:

```text
===== SECTION 3: CLEAN SHUTDOWN =====
blocked pop() woke up on close() and returned nullopt: true
push after close returns: false (rejected)
blocked push() woke up on close() and returned: false (item dropped)
close() lets consumers drain what was queued: first pop = 1
Shutdown order: stop producers, close(), let consumers drain, then join.
```

### SECTION 4: THE WAIT RULES (TRAPS)
The four rules, printed as text. (1) Always wait with a predicate: `cv.wait(lock, pred)` loops until the condition is true, which protects against spurious wakeups (the OS may wake you with no notify) and notifies sent before you started waiting. (2) Change the condition while holding the same mutex the waiter uses. (3) A notify with nobody waiting is lost; the state in the predicate, not the notify, is the truth. (4) Use `notify_all` for state changes everyone should see, such as shutdown; `notify_one` when a single waiter can use the change.

Output from a real run:

```text
===== SECTION 4: THE WAIT RULES (TRAPS) =====
1. ALWAYS wait with a predicate: cv.wait(lock, [&]{ return condition; }).
   A bare cv.wait(lock) can wake spuriously (no notify happened) or miss a notify sent before you waited.
2. Change the condition while holding the same mutex the waiter uses, or a notify can be lost.
3. A notify with no waiter is simply forgotten; the predicate (state), not the notify, is the truth.
4. Use notify_all for shutdown flags; notify_one for 'one item became available'.
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `BlockingQueue` / `ArrayBlockingQueue` with `put()` / `take()`. | No ready-made one in the standard library; build it from a mutex plus condition variables as here. |
| `wait()` / `notify()` / `notifyAll()` on any object, inside `synchronized`. | `std::condition_variable` is a separate object used with a `std::unique_lock<std::mutex>`. |
| `while (!condition) wait();` is the recommended pattern. | `cv.wait(lock, predicate)` is the same loop, built in. |
| `Condition` objects from a `ReentrantLock`. | Closest analogue; here each queue condition has its own `condition_variable`. |
| Poison pill objects or `interrupt()` to stop workers. | A `closed` flag checked in the predicate, then `notify_all()`; or `std::stop_token` with `jthread`. |
| `ExecutorService.shutdown()` handles worker lifecycle. | You write the shutdown protocol yourself. |

## Key Rules / Gotchas Recap
- Always `cv.wait(lock, predicate)`; never a bare `wait(lock)`.
- The predicate and the state it checks must be protected by the same mutex.
- Notify after changing the state; it is fine to notify after releasing the lock, but never skip changing state under the lock.
- Close/shutdown must wake ALL waiters (`notify_all`).
- Join producers before closing so nothing is lost.
- Do not hold the lock while doing slow work.
- Condition variables need `std::unique_lock`, not `lock_guard`.

## Why This Structure Exists
Job queues feeding worker threads are the backbone of model-serving servers, crawlers and scanners. A bounded queue gives back-pressure (producers slow down instead of using all memory), and a clean shutdown path is what separates a tool that exits quietly from one that hangs forever.
