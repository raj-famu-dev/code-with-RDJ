// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class _8_ExecutorService {

    public static void main(String[] args) throws Exception {

        // ============================================
        // SECTION 1: WHY NOT JUST new Thread() EVERY TIME?
        // - Creating a thread is expensive, and thousands of them can exhaust memory.
        // - You get no result, no error handling, no way to cancel.
        // An ExecutorService is a POOL of reusable worker threads plus a queue of
        // tasks. You hand it tasks; it decides which thread runs them.
        // ============================================


        // ============================================
        // SECTION 2: A FIXED POOL
        // 3 worker threads take tasks from a queue. 6 tasks means the threads
        // are REUSED (look at the set of names used: never more than 3).
        // ============================================

        ExecutorService pool = Executors.newFixedThreadPool(3);
        try {
            List<Future<String>> futures = new ArrayList<>();
            for (int i = 1; i <= 6; i++) {
                int id = i;
                futures.add(pool.submit(() -> {
                    Thread.sleep(50);
                    return "task " + id + " ran on " + Thread.currentThread().getName();
                }));
            }
            java.util.Set<String> threadNames = new java.util.TreeSet<>();
            for (Future<String> f : futures) {
                String line = f.get();                                   // blocks until that task is done
                System.out.println("  " + line);
                threadNames.add(line.substring(line.lastIndexOf(' ') + 1));
            }
            System.out.println("distinct worker threads used: " + threadNames.size() + " (at most 3)");


            // ============================================
            // SECTION 3: execute() vs submit()
            // execute(Runnable)  : fire and forget, an exception just kills the task.
            // submit(...)        : returns a Future. An exception is HIDDEN inside the
            //                      Future until you call get(): forget get() and the
            //                      error vanishes silently.
            // ============================================

            Future<?> failing = pool.submit(() -> {
                throw new IllegalStateException("task failed");
            });
            try {
                failing.get();
            } catch (ExecutionException e) {
                System.out.println("submit() hid the exception until get(): " + e.getCause());
            }


            // ============================================
            // SECTION 4: invokeAll - RUN A BATCH, WAIT FOR ALL
            // ============================================

            List<Callable<Integer>> squares = new ArrayList<>();
            for (int i = 1; i <= 5; i++) {
                int n = i;
                squares.add(() -> n * n);
            }
            int sum = 0;
            for (Future<Integer> f : pool.invokeAll(squares)) {          // results come back in submit order
                sum += f.get();
            }
            System.out.println("sum of squares 1..5 = " + sum);
        } finally {


            // ============================================
            // SECTION 5: SHUTTING DOWN (THE PART PEOPLE FORGET)
            // Pool threads are non-daemon: if you never shut the pool down, the
            // JVM never exits. The standard pattern:
            //   shutdown()         stop accepting new tasks, finish the queued ones
            //   awaitTermination() wait (with a timeout) for them to finish
            //   shutdownNow()      last resort: interrupt anything still running
            // ============================================

            pool.shutdown();
            if (!pool.awaitTermination(5, TimeUnit.SECONDS)) {
                pool.shutdownNow();
            }
            System.out.println("pool.isShutdown() = " + pool.isShutdown() + ", isTerminated() = " + pool.isTerminated());
        }


        // ============================================
        // SECTION 6: SUBMITTING AFTER SHUTDOWN IS REJECTED
        // ============================================

        try {
            pool.submit(() -> { });
        } catch (java.util.concurrent.RejectedExecutionException e) {
            System.out.println("RejectedExecutionException: a shut-down pool takes no new tasks");
        }


        // ============================================
        // SECTION 7: A SCHEDULED POOL
        // Run something repeatedly (or after a delay). Here: 3 ticks, 40 ms apart.
        // ============================================

        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
        AtomicInteger ticks = new AtomicInteger();
        scheduler.scheduleAtFixedRate(() -> ticks.incrementAndGet(), 0, 40, TimeUnit.MILLISECONDS);
        Thread.sleep(150);
        scheduler.shutdown();
        scheduler.awaitTermination(2, TimeUnit.SECONDS);
        System.out.println("ticks in ~150 ms at 40 ms intervals: " + ticks.get() + " (about 4, timing varies)");


        // ============================================
        // SECTION 8: CHOOSING A POOL
        // newFixedThreadPool(n)   : CPU-bound work, n about the number of cores
        //                           (Runtime.getRuntime().availableProcessors())
        // newCachedThreadPool()   : many short tasks, but UNBOUNDED threads: risky
        // newSingleThreadExecutor : tasks must run one after another
        // newVirtualThreadPerTaskExecutor() : blocking I/O work (see _13)
        // ============================================
    }
}
