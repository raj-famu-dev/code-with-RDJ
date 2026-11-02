// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.lang.management.ManagementFactory;
import java.lang.management.ThreadInfo;
import java.lang.management.ThreadMXBean;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.TimeUnit;

public class _12_Deadlock {

    static final Object LOCK_A = new Object();
    static final Object LOCK_B = new Object();

    // Waits (up to 3 s) until the JVM reports a deadlock; returns the threads involved, or null
    static long[] waitForDeadlock() throws InterruptedException {
        ThreadMXBean mx = ManagementFactory.getThreadMXBean();
        long deadline = System.currentTimeMillis() + 3000;
        while (System.currentTimeMillis() < deadline) {
            long[] ids = mx.findDeadlockedThreads();
            if (ids != null) return ids;
            Thread.sleep(20);
        }
        return null;
    }

    public static void main(String[] args) throws Exception {

        // ============================================
        // SECTION 1: WHAT IS A DEADLOCK?
        // Thread 1 holds A and wants B. Thread 2 holds B and wants A.
        // Each waits for the other forever. All four of these must be true:
        //   1) mutual exclusion  - a lock has one owner
        //   2) hold and wait     - you keep what you hold while asking for more
        //   3) no preemption     - locks are not taken away
        //   4) circular wait     - A waits for B waits for A
        // Break ANY one of them and deadlock is impossible.
        // ============================================


        // ============================================
        // SECTION 2: CAUSING ONE ON PURPOSE (SAFELY)
        // A CyclicBarrier makes both threads hold their FIRST lock before either
        // asks for the second, so the deadlock happens every time, not just sometimes.
        // The threads are DAEMONS so this demo can never keep the JVM alive.
        // ============================================

        CyclicBarrier bothHoldFirst = new CyclicBarrier(2);

        Thread t1 = new Thread(() -> {
            synchronized (LOCK_A) {
                await(bothHoldFirst);
                synchronized (LOCK_B) {                              // never gets here
                    System.out.println("t1 got both locks");
                }
            }
        }, "deadlock-t1");

        Thread t2 = new Thread(() -> {
            synchronized (LOCK_B) {
                await(bothHoldFirst);
                synchronized (LOCK_A) {                              // never gets here
                    System.out.println("t2 got both locks");
                }
            }
        }, "deadlock-t2");

        t1.setDaemon(true);
        t2.setDaemon(true);
        t1.start();
        t2.start();


        // ============================================
        // SECTION 3: DETECTING IT
        // ThreadMXBean asks the JVM which threads are stuck in a lock cycle.
        // (A thread dump from "jstack <pid>" shows the same thing in a real app.)
        // ============================================

        long[] ids = waitForDeadlock();
        if (ids == null) {
            System.out.println("no deadlock detected (unexpected)");
        } else {
            System.out.println("DEADLOCK detected, " + ids.length + " threads involved:");
            for (ThreadInfo info : ManagementFactory.getThreadMXBean().getThreadInfo(ids)) {
                System.out.println("  " + info.getThreadName() + " is " + info.getThreadState()
                        + ", waiting for a lock owned by " + info.getLockOwnerName());
            }
        }
        // t1 and t2 are stuck for good. Nothing short of killing the JVM frees them,
        // which is exactly why this is so dangerous in a real program.


        // ============================================
        // SECTION 4: FIX 1 - ALWAYS TAKE LOCKS IN THE SAME ORDER
        // Breaks "circular wait". Both threads take A first, then B.
        // Whoever gets A first finishes; the other simply waits its turn.
        // ============================================

        // Fresh locks, because LOCK_A and LOCK_B are still held by the stuck demo threads above.
        Object a = new Object();
        Object b = new Object();
        Thread g1 = ordered(a, b, "ordered-t1");
        Thread g2 = ordered(a, b, "ordered-t2");
        g1.start();
        g2.start();
        g1.join(2000);
        g2.join(2000);
        System.out.println("ordered threads finished: " + (!g1.isAlive() && !g2.isAlive()));


        // ============================================
        // SECTION 5: FIX 2 - tryLock WITH A TIMEOUT AND BACK OFF
        // Breaks "hold and wait": if you cannot get the second lock in time,
        // let go of the first and try again (or report failure).
        // Here the threads deliberately ask in OPPOSITE orders, yet cannot deadlock.
        // ============================================

        ReentrantLock lockX = new ReentrantLock();
        ReentrantLock lockY = new ReentrantLock();
        int[] successes = new int[2];
        Thread s1 = new Thread(() -> successes[0] = tryBoth(lockX, lockY), "try-t1");
        Thread s2 = new Thread(() -> successes[1] = tryBoth(lockY, lockX), "try-t2");
        s1.start();
        s2.start();
        s1.join(3000);
        s2.join(3000);
        System.out.println("tryLock threads finished: " + (!s1.isAlive() && !s2.isAlive())
                + ", completed work: " + (successes[0] + successes[1]) + " of 2");


        // ============================================
        // SECTION 6: PREVENTION CHECKLIST
        // - Prefer fewer locks. Prefer immutable data and message passing.
        // - Take multiple locks in one global order.
        // - Never call unknown code (callbacks, overridable methods) while holding a lock.
        // - Use tryLock with a timeout when you cannot guarantee an order.
        // - Related but different: LIVELOCK (threads keep reacting to each other
        //   and make no progress) and STARVATION (one thread never gets a turn).
        // ============================================
        System.out.println("main ends; the two deadlocked daemon threads do not keep the JVM alive");
    }

    static void await(CyclicBarrier barrier) {
        try {
            barrier.await(2, TimeUnit.SECONDS);
        } catch (Exception e) {
            // interrupted or barrier broken: nothing useful to do in a demo
        }
    }

    static Thread ordered(Object first, Object second, String name) {
        return new Thread(() -> {
            synchronized (first) {
                synchronized (second) {
                    System.out.println(name + " got both locks (same order as everyone else)");
                }
            }
        }, name);
    }

    // Returns 1 if both locks were obtained and the work done, 0 if it gave up
    static int tryBoth(ReentrantLock first, ReentrantLock second) {
        for (int attempt = 1; attempt <= 20; attempt++) {
            try {
                if (first.tryLock(50, TimeUnit.MILLISECONDS)) {
                    try {
                        if (second.tryLock(50, TimeUnit.MILLISECONDS)) {
                            try {
                                return 1;                           // both held: do the work
                            } finally {
                                second.unlock();
                            }
                        }
                    } finally {
                        first.unlock();                             // back off: release what we hold
                    }
                }
                Thread.sleep((long) (Math.random() * 20));          // random pause so the two do not retry in lockstep
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return 0;
            }
        }
        return 0;
    }
}
