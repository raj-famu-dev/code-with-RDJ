// Tags: #Java #Multithreading #Concurrency #RaceConditions | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;

public class _4_RaceConditions {

    static class Counter {
        int value = 0;

        void increment() {
            value++;                    // LOOKS like one step, but is three (see Section 1)
        }
    }

    static class Account {
        int balance = 100;

        void withdraw(int amount) {
            if (balance >= amount) {    // CHECK
                Thread.yield();         // gives the other thread a chance to slip in (makes the bug easier to see)
                balance -= amount;      // ACT
            }
        }
    }

    static int countWithThreads(int threads, int incrementsEach) throws InterruptedException {
        Counter counter = new Counter();
        Thread[] workers = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            workers[i] = new Thread(() -> {
                for (int j = 0; j < incrementsEach; j++) {
                    counter.increment();
                }
            });
        }
        for (Thread t : workers) t.start();
        for (Thread t : workers) t.join();
        return counter.value;
    }

    public static void main(String[] args) throws Exception {

        // ============================================
        // SECTION 1: WHY value++ IS NOT ONE STEP
        // It is three: READ value, ADD 1, WRITE it back.
        //
        //   thread A reads 5          thread B reads 5
        //   thread A writes 6         thread B writes 6     <- two increments, counter only moved by 1
        //
        // One update is LOST. This is a "read-modify-write" race condition.
        // ============================================


        // ============================================
        // SECTION 2: WATCH UPDATES GET LOST
        // Two threads, 500,000 increments each: the answer should be 1,000,000.
        // The wrong totals differ on every run and on every machine.
        // On a lucky run you may even see the correct number: that is exactly
        // why race conditions are so hard to catch.
        // ============================================

        int expected = 2 * 500_000;
        for (int run = 1; run <= 5; run++) {
            int got = countWithThreads(2, 500_000);
            System.out.println("run " + run + ": expected " + expected + ", got " + got
                    + (got == expected ? "  (lucky: no update lost this time)" : "  (lost " + (expected - got) + ")"));
        }


        // ============================================
        // SECTION 3: ONE THREAD IS ALWAYS CORRECT
        // The bug needs two or more threads touching the same data.
        // ============================================

        System.out.println("single thread: " + countWithThreads(1, 1_000_000) + " (always correct)");


        // ============================================
        // SECTION 4: A SECOND KIND - CHECK-THEN-ACT
        // Balance is 100. Two threads each try to withdraw 80. Only one should
        // succeed. A barrier makes both threads start at the same instant.
        // If both pass the CHECK before either does the ACT, the balance goes negative.
        // ============================================

        int negative = 0;
        int trials = 2000;
        for (int i = 0; i < trials; i++) {
            Account account = new Account();
            CyclicBarrier startTogether = new CyclicBarrier(2);
            Runnable attempt = () -> {
                try {
                    startTogether.await();
                } catch (InterruptedException | BrokenBarrierException e) {
                    return;
                }
                account.withdraw(80);
            };
            Thread a = new Thread(attempt);
            Thread b = new Thread(attempt);
            a.start();
            b.start();
            a.join();
            b.join();
            if (account.balance < 0) negative++;
        }
        System.out.println("balance went negative in " + negative + " of " + trials
                + " trials (varies; can be 0 on a slow or single-core machine)");


        // ============================================
        // SECTION 5: WHAT MAKES IT A RACE CONDITION?
        // 1) shared data  2) at least one thread modifies it  3) no coordination.
        // The fixes (next files): make the steps atomic with 'synchronized'
        // (_5), locks and atomic variables (_10), or avoid sharing (_14).
        // ============================================
    }
}
