// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.concurrent.atomic.AtomicBoolean;

public class _3_ThreadLifecycle {

    static final Object LOCK = new Object();

    // Threads change state on their own schedule, so instead of guessing with a
    // fixed sleep, we poll until the state we want appears (or give up).
    static void waitForState(Thread t, Thread.State wanted) throws InterruptedException {
        long deadline = System.currentTimeMillis() + 2000;
        while (t.getState() != wanted && System.currentTimeMillis() < deadline) {
            Thread.sleep(5);
        }
    }

    public static void main(String[] args) throws InterruptedException {

        // ============================================
        // SECTION 1: THE SIX STATES (Thread.State)
        // NEW            created, start() not called yet
        // RUNNABLE       running, or ready to run
        // BLOCKED        waiting to enter a synchronized block someone else holds
        // WAITING        waiting with no time limit (wait(), join(), park())
        // TIMED_WAITING  waiting with a time limit (sleep(ms), wait(ms), join(ms))
        // TERMINATED     finished
        // ============================================


        // ============================================
        // SECTION 2: NEW -> TERMINATED
        // ============================================

        Thread simple = new Thread(() -> { });
        System.out.println("before start():  " + simple.getState());
        simple.start();
        simple.join();
        System.out.println("after finishing: " + simple.getState());


        // ============================================
        // SECTION 3: RUNNABLE - ACTUALLY WORKING
        // ============================================

        AtomicBoolean stop = new AtomicBoolean(false);
        Thread busy = new Thread(() -> {
            while (!stop.get()) {
                // spin
            }
        });
        busy.setDaemon(true);
        busy.start();
        waitForState(busy, Thread.State.RUNNABLE);
        System.out.println("busy loop:       " + busy.getState());
        stop.set(true);
        busy.join();


        // ============================================
        // SECTION 4: TIMED_WAITING - SLEEPING
        // ============================================

        Thread sleeper = new Thread(() -> {
            try {
                Thread.sleep(500);
            } catch (InterruptedException ignored) {
            }
        });
        sleeper.start();
        waitForState(sleeper, Thread.State.TIMED_WAITING);
        System.out.println("in sleep(500):   " + sleeper.getState());
        sleeper.join();


        // ============================================
        // SECTION 5: BLOCKED - WAITING FOR SOMEONE ELSE'S LOCK
        // main holds LOCK, so the new thread cannot enter its synchronized block.
        // ============================================

        Thread blocked = new Thread(() -> {
            synchronized (LOCK) {
                // got the lock after main let go
            }
        });
        synchronized (LOCK) {
            blocked.start();
            waitForState(blocked, Thread.State.BLOCKED);
            System.out.println("lock is taken:   " + blocked.getState());
        }
        blocked.join();


        // ============================================
        // SECTION 6: WAITING - wait() WITH NO TIME LIMIT
        // The thread gives up the lock and sleeps until someone calls notify.
        // ============================================

        Thread waiter = new Thread(() -> {
            synchronized (LOCK) {
                try {
                    LOCK.wait();
                } catch (InterruptedException ignored) {
                }
            }
        });
        waiter.start();
        waitForState(waiter, Thread.State.WAITING);
        System.out.println("in wait():       " + waiter.getState());
        synchronized (LOCK) {
            LOCK.notifyAll();
        }
        waiter.join();


        // ============================================
        // SECTION 7: interrupt() - A POLITE REQUEST TO STOP
        // It does not kill the thread. It sets a flag, and blocking methods like
        // sleep() react by throwing InterruptedException. Catching it CLEARS the
        // flag, so good code restores it with Thread.currentThread().interrupt().
        // ============================================

        Thread interruptible = new Thread(() -> {
            try {
                Thread.sleep(10_000);
                System.out.println("  (not printed: the sleep was cut short)");
            } catch (InterruptedException e) {
                System.out.println("  woke up with InterruptedException, flag now: "
                        + Thread.currentThread().isInterrupted());
                Thread.currentThread().interrupt();          // restore the flag
                System.out.println("  after restoring, flag: " + Thread.currentThread().isInterrupted());
            }
        });
        interruptible.start();
        waitForState(interruptible, Thread.State.TIMED_WAITING);
        interruptible.interrupt();
        interruptible.join();


        // ============================================
        // SECTION 8: join WITH A TIMEOUT
        // join() waits forever; join(ms) gives up after ms and carries on.
        // ============================================

        Thread slow = new Thread(() -> {
            try {
                Thread.sleep(300);
            } catch (InterruptedException ignored) {
            }
        });
        slow.start();
        slow.join(50);
        System.out.println("after join(50), still alive? " + slow.isAlive());
        slow.join();
    }
}
