// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
public class _5_Synchronized {

    // The broken version from _4, for comparison
    static class UnsafeCounter {
        int value;

        void increment() {
            value++;
        }
    }

    // Fix 1: synchronized METHOD - locks on 'this' (the object the method is called on)
    static class MethodLockCounter {
        private int value;

        synchronized void increment() {
            value++;
        }

        synchronized int get() {
            return value;
        }
    }

    // Fix 2: synchronized BLOCK on a private lock object - locks only the code that needs it
    static class BlockLockCounter {
        private final Object lock = new Object();
        private int value;

        void increment() {
            synchronized (lock) {
                value++;
            }
        }

        int get() {
            synchronized (lock) {
                return value;
            }
        }
    }

    // Fix 3: static synchronized - locks on the CLASS object, shared by all instances
    static int staticValue = 0;

    static synchronized void incrementStatic() {
        staticValue++;
    }

    // BUG ON PURPOSE: every call locks a brand new object, so nobody ever waits for anybody
    static class WrongLockCounter {
        int value;

        void increment() {
            synchronized (new Object()) {
                value++;
            }
        }
    }

    // Reentrancy: a thread that already holds a lock can enter other code locked by the same lock
    static class Reentrant {
        synchronized void outer() {
            System.out.println("  outer() holds the lock");
            inner();
        }

        synchronized void inner() {
            System.out.println("  inner() enters the SAME lock again: no deadlock");
        }
    }

    // Runs the same operation from several threads and waits for all of them
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

    public static void main(String[] args) throws InterruptedException {

        int threads = 2;
        int times = 500_000;
        int expected = threads * times;

        // ============================================
        // SECTION 1: WHAT synchronized DOES
        // Every Java object has a built-in lock (a "monitor"). Only ONE thread at
        // a time can hold it. A thread entering a synchronized block must take
        // the lock first; if another thread has it, the newcomer WAITS (BLOCKED).
        // It also guarantees that changes made inside become visible to the next
        // thread that takes the same lock.
        // ============================================

        UnsafeCounter unsafe = new UnsafeCounter();
        hammer(unsafe::increment, threads, times);
        System.out.println("unsafe:          expected " + expected + ", got " + unsafe.value + "  (can be less; varies per run)");


        // ============================================
        // SECTION 2: THE FIX, THREE WAYS - EXACT EVERY TIME
        // ============================================

        MethodLockCounter methodLock = new MethodLockCounter();
        hammer(methodLock::increment, threads, times);
        System.out.println("synchronized method: " + methodLock.get());

        BlockLockCounter blockLock = new BlockLockCounter();
        hammer(blockLock::increment, threads, times);
        System.out.println("synchronized block:  " + blockLock.get());

        hammer(_5_Synchronized::incrementStatic, threads, times);
        System.out.println("static synchronized: " + staticValue);


        // ============================================
        // SECTION 3: WHAT, EXACTLY, IS BEING LOCKED?
        // synchronized instance method      -> lock on 'this'
        // synchronized (someObject) { ... } -> lock on someObject
        // static synchronized method        -> lock on the Class object
        // Two threads only exclude each other if they use the SAME lock object.
        // Two different Counter objects have different locks and do not block each other.
        // ============================================


        // ============================================
        // SECTION 4: TRAP - SYNCHRONIZING ON A DIFFERENT OBJECT EACH TIME
        // It compiles and looks protected, but it protects nothing.
        // ============================================

        WrongLockCounter wrong = new WrongLockCounter();
        hammer(wrong::increment, threads, times);
        System.out.println("wrong lock:      expected " + expected + ", got " + wrong.value + "  (can be less: no real protection; varies per run)");


        // ============================================
        // SECTION 5: REENTRANCY
        // Java's intrinsic locks are reentrant: the thread that owns the lock can
        // take it again. Without this, outer() calling inner() would deadlock itself.
        // ============================================

        new Reentrant().outer();


        // ============================================
        // SECTION 6: KEEP THE LOCKED PART SMALL
        // Anything inside synchronized runs one thread at a time. Lock only the
        // shared-data steps, never slow work like file or network calls.
        // Too much locking = a "multithreaded" program that is really sequential.
        // ============================================
    }
}
