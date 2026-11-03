// Tags: #Java #Multithreading #Concurrency #VolatileMemoryModel | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
public class _6_VolatileAndMemoryModel {

    static boolean plainStop = false;               // NOT volatile
    static volatile boolean volatileStop = false;   // volatile
    static volatile int volatileCounter = 0;

    public static void main(String[] args) throws InterruptedException {

        // ============================================
        // SECTION 1: TWO DIFFERENT PROBLEMS
        // VISIBILITY - when one thread writes a variable, will another thread SEE it?
        //   Each thread may keep a private cached copy (in a CPU cache or register),
        //   and the compiler/JIT may reorder or reuse reads. Without a rule, a
        //   change in one thread may NOT become visible to another for a long time.
        // ATOMICITY  - can a multi-step operation (value++) be interrupted midway?
        //
        // 'volatile' solves visibility (and ordering). It does NOT give atomicity.
        // ============================================


        // ============================================
        // SECTION 2: volatile FIXES VISIBILITY
        // Every write to a volatile variable is visible to every later read of it,
        // from any thread. A volatile stop-flag is the classic correct use.
        // ============================================

        Thread worker = new Thread(() -> {
            long spins = 0;
            while (!volatileStop) {
                spins++;
            }
            System.out.println("  volatile worker saw the flag and stopped");
        }, "volatile-worker");
        worker.setDaemon(true);
        worker.start();
        Thread.sleep(100);
        volatileStop = true;
        worker.join(1000);
        System.out.println("volatile worker still alive? " + worker.isAlive());


        // ============================================
        // SECTION 3: volatile DOES NOT MAKE ++ ATOMIC
        // volatileCounter++ is still read, add, write. Two threads can still
        // interleave and lose updates, even though the variable is volatile.
        // ============================================

        Runnable bump = () -> {
            for (int i = 0; i < 200_000; i++) {
                volatileCounter++;
            }
        };
        Thread a = new Thread(bump);
        Thread b = new Thread(bump);
        a.start();
        b.start();
        a.join();
        b.join();
        System.out.println("volatile counter: expected 400000, got " + volatileCounter
                + "  (can be less: visibility is not atomicity; varies per run)");
        // Fixes: synchronized (_5) or AtomicInteger (_10).


        // ============================================
        // SECTION 4: THE BUG volatile PREVENTS (NON-DETERMINISTIC)
        // Same stop-flag idea, but the flag is a plain boolean. The Java memory
        // model ALLOWS the worker to keep using a stale 'false' forever, and the JIT
        // compiler can turn the loop into "while (true)". Whether you SEE the
        // problem depends on your JVM and CPU, so both outcomes below are legal.
        // The worker is a daemon, so even if it never stops the program still ends.
        // ============================================

        Thread plain = new Thread(() -> {
            long spins = 0;
            while (!plainStop) {
                spins++;
            }
            System.out.println("  plain worker eventually saw the flag");
        }, "plain-worker");
        plain.setDaemon(true);
        plain.start();
        Thread.sleep(300);
        plainStop = true;
        plain.join(500);
        if (plain.isAlive()) {
            System.out.println("plain worker is STILL RUNNING: it never saw plainStop = true");
        } else {
            System.out.println("plain worker stopped this time (allowed, but not guaranteed on every JVM)");
        }


        // ============================================
        // SECTION 5: HAPPENS-BEFORE (THE IDEA BEHIND ALL OF THIS)
        // The memory model defines when one action is guaranteed to be visible to
        // another. The main ones:
        // - a write to a volatile happens-before every later read of it
        // - unlocking a monitor happens-before the next lock of the SAME monitor
        // - Thread.start() happens-before anything in the started thread
        // - everything in a thread happens-before another thread's join() returns
        // ============================================


        // ============================================
        // SECTION 6: WHEN TO USE volatile
        // YES: a simple flag (stop/ready) written by one thread, read by others.
        // NO : counters or anything with read-modify-write: use synchronized or atomics.
        // ============================================
    }
}
