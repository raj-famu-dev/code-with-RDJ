// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.time.Duration;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public class _13_VirtualThreads {

    // Simulates a blocking call such as a database query or HTTP request
    static void fakeIoCall() {
        try {
            Thread.sleep(Duration.ofMillis(200));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    static long runTasks(ExecutorService executor, int tasks, AtomicInteger finished) {
        long start = System.nanoTime();
        for (int i = 0; i < tasks; i++) {
            executor.submit(() -> {
                fakeIoCall();
                finished.incrementAndGet();
            });
        }
        executor.shutdown();
        try {
            executor.awaitTermination(30, java.util.concurrent.TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return (System.nanoTime() - start) / 1_000_000;
    }

    public static void main(String[] args) throws Exception {

        // ============================================
        // SECTION 1: PLATFORM THREADS vs VIRTUAL THREADS
        // A normal ("platform") thread is a thin wrapper over an operating-system
        // thread: heavy (about a megabyte of stack reserved), so a machine
        // supports only thousands. A VIRTUAL thread (Java 21) is managed by the
        // JVM: very light, so you can have hundreds of thousands. When a virtual
        // thread blocks (sleep, I/O), the JVM parks it and lets the real OS thread
        // run another virtual thread.
        // ============================================


        // ============================================
        // SECTION 2: CREATING ONE
        // ============================================

        Thread v = Thread.ofVirtual().name("my-virtual").start(() ->
                System.out.println("inside: isVirtual = " + Thread.currentThread().isVirtual()));
        v.join();

        Thread p = Thread.ofPlatform().name("my-platform").start(() ->
                System.out.println("inside: isVirtual = " + Thread.currentThread().isVirtual()));
        p.join();

        Thread quick = Thread.startVirtualThread(() -> { });          // shortcut
        quick.join();
        System.out.println("virtual threads are always daemon threads: " + quick.isDaemon());


        // ============================================
        // SECTION 3: ONE VIRTUAL THREAD PER TASK
        // Executors.newVirtualThreadPerTaskExecutor() creates a NEW virtual thread
        // for every task. Do NOT pool virtual threads: they are cheap on purpose.
        // ============================================

        int tasks = 2_000;
        AtomicInteger finishedVirtual = new AtomicInteger();
        long virtualMs = runTasks(Executors.newVirtualThreadPerTaskExecutor(), tasks, finishedVirtual);
        System.out.println(tasks + " tasks x 200 ms of blocking, virtual threads: finished "
                + finishedVirtual.get() + ", about " + virtualMs + " ms");


        // ============================================
        // SECTION 4: THE SAME WORK ON A FIXED POOL OF 50 PLATFORM THREADS
        // 2000 tasks / 50 threads = 40 rounds x 200 ms, so roughly 8 seconds.
        // We use only 500 tasks here (10 rounds, about 2 s) to keep the demo short.
        // The timings below are measurements from THIS machine and will differ on yours.
        // ============================================

        int smallTasks = 500;
        AtomicInteger finishedPool = new AtomicInteger();
        long poolMs = runTasks(Executors.newFixedThreadPool(50), smallTasks, finishedPool);
        System.out.println(smallTasks + " tasks x 200 ms of blocking, 50 platform threads: finished "
                + finishedPool.get() + ", about " + poolMs + " ms");


        // ============================================
        // SECTION 5: WHAT VIRTUAL THREADS ARE FOR (AND NOT FOR)
        // FOR: lots of tasks that spend most of their time WAITING (network,
        //      database, files). Code stays simple and blocking, yet scales.
        // NOT FOR: CPU-bound work. If tasks calculate all the time, you are
        //      limited by CPU cores and virtual threads give no speed-up.
        // ============================================


        // ============================================
        // SECTION 6: THINGS TO KNOW
        // - Do not pool them. Use one per task.
        // - Avoid long synchronized blocks around blocking calls in Java 21: the
        //   virtual thread can get "pinned" to its OS thread. Prefer ReentrantLock there.
        // - Thread-locals still work but are costly when you have millions of threads.
        // - Spring Boot can run web requests on virtual threads
        //   (spring.threads.virtual.enabled=true in recent versions).
        // ============================================
    }
}
