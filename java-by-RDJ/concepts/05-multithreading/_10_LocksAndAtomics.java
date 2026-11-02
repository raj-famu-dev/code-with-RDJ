// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.atomic.LongAdder;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class _10_LocksAndAtomics {

    // ReentrantLock: same idea as synchronized, but explicit and with extra abilities
    static class LockedCounter {
        private final ReentrantLock lock = new ReentrantLock();
        private int value;

        void increment() {
            lock.lock();
            try {
                value++;
            } finally {
                lock.unlock();              // ALWAYS in finally, or an exception leaves the lock held forever
            }
        }

        int get() {
            lock.lock();
            try {
                return value;
            } finally {
                lock.unlock();
            }
        }
    }

    // ReadWriteLock: many readers at once, but a writer needs exclusive access
    static class Cache {
        private final ReentrantReadWriteLock rw = new ReentrantReadWriteLock();
        private String data = "v1";

        String read() {
            rw.readLock().lock();
            try {
                return data;
            } finally {
                rw.readLock().unlock();
            }
        }

        void write(String newData) {
            rw.writeLock().lock();
            try {
                data = newData;
            } finally {
                rw.writeLock().unlock();
            }
        }
    }

    static void hammer(Runnable op, int threads, int times) throws InterruptedException {
        Thread[] workers = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            workers[i] = new Thread(() -> {
                for (int j = 0; j < times; j++) {
                    op.run();
                }
            });
        }
        for (Thread t : workers) t.start();
        for (Thread t : workers) t.join();
    }

    public static void main(String[] args) throws Exception {

        int threads = 4;
        int times = 250_000;
        int expected = threads * times;

        // ============================================
        // SECTION 1: ReentrantLock
        // lock()/unlock() instead of synchronized. More code, but it offers
        // things synchronized cannot: tryLock, timeouts, fairness, interruptible waits.
        // ============================================

        LockedCounter locked = new LockedCounter();
        hammer(locked::increment, threads, times);
        System.out.println("ReentrantLock counter: " + locked.get() + " (expected " + expected + ")");


        // ============================================
        // SECTION 2: tryLock - DON'T WAIT IF THE LOCK IS BUSY
        // Another thread holds the lock. tryLock returns false instead of blocking.
        // Note: a lock is owned by a THREAD, so the holder must be a different one.
        // ============================================

        ReentrantLock busy = new ReentrantLock();
        Thread holder = new Thread(() -> {
            busy.lock();
            try {
                Thread.sleep(300);
            } catch (InterruptedException ignored) {
            } finally {
                busy.unlock();
            }
        });
        holder.start();
        while (!busy.isLocked()) {
            Thread.sleep(1);
        }
        System.out.println("tryLock() while another thread holds it: " + busy.tryLock());
        boolean gotIt = busy.tryLock(50, TimeUnit.MILLISECONDS);
        System.out.println("tryLock(50 ms): " + gotIt);
        holder.join();
        if (busy.tryLock()) {
            System.out.println("after the holder finished, tryLock(): true");
            busy.unlock();
        }


        // ============================================
        // SECTION 3: ReadWriteLock
        // Good when reads vastly outnumber writes. Readers never block each other.
        // ============================================

        Cache cache = new Cache();
        System.out.println("cache read: " + cache.read());
        cache.write("v2");
        System.out.println("cache read: " + cache.read());


        // ============================================
        // SECTION 4: ATOMIC VARIABLES - NO LOCK AT ALL
        // AtomicInteger.incrementAndGet() is ONE indivisible step, done with a
        // special CPU instruction (compare-and-swap). Correct and usually faster
        // than a lock for simple counters.
        // ============================================

        AtomicInteger atomic = new AtomicInteger();
        hammer(atomic::incrementAndGet, threads, times);
        System.out.println("AtomicInteger counter: " + atomic.get() + " (expected " + expected + ")");


        // ============================================
        // SECTION 5: compareAndSet - HOW IT WORKS
        // "Set it to NEW only if it is still EXPECTED; tell me whether it worked."
        // If it failed, someone else changed it: read again and retry.
        // ============================================

        AtomicInteger value = new AtomicInteger(10);
        System.out.println("compareAndSet(10, 11): " + value.compareAndSet(10, 11) + ", value = " + value.get());
        System.out.println("compareAndSet(10, 99): " + value.compareAndSet(10, 99) + ", value = " + value.get() + "  (fails: it is 11 now)");

        // A hand-written retry loop: "double the value atomically"
        int old;
        do {
            old = value.get();
        } while (!value.compareAndSet(old, old * 2));
        System.out.println("doubled with a CAS loop: " + value.get());
        // Or simply: value.updateAndGet(v -> v * 2)


        // ============================================
        // SECTION 6: OTHER ATOMICS
        // AtomicReference<T>: atomically swap an object reference.
        // LongAdder: a counter built for heavy write contention (many threads
        // only adding); read the total with sum().
        // ============================================

        AtomicReference<String> ref = new AtomicReference<>("A");
        ref.compareAndSet("A", "B");
        System.out.println("AtomicReference: " + ref.get());

        LongAdder adder = new LongAdder();
        hammer(adder::increment, threads, times);
        System.out.println("LongAdder sum: " + adder.sum() + " (expected " + expected + ")");


        // ============================================
        // SECTION 7: SO WHICH TOOL?
        // One variable, simple update      -> Atomic* (or LongAdder if heavy contention)
        // Several variables must change together -> a lock (synchronized or ReentrantLock)
        // Need tryLock / timeout / fairness      -> ReentrantLock
        // Mostly reads, rare writes              -> ReadWriteLock (measure first)
        // Atomics make each SINGLE operation safe; two atomic calls in a row are NOT atomic together.
        // ============================================
    }
}
