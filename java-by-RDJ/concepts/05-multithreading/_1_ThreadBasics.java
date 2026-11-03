// Tags: #Java #Multithreading #Concurrency #ThreadBasics | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
public class _1_ThreadBasics {

    // Way 2 of describing a thread's work: subclass Thread and override run()
    static class Greeter extends Thread {
        Greeter(String name) {
            super(name);
        }

        @Override
        public void run() {
            System.out.println("  Greeter subclass running on thread: " + getName());
        }
    }

    public static void main(String[] args) throws InterruptedException {

        // ============================================
        // SECTION 1: EVERY PROGRAM ALREADY HAS ONE THREAD
        // The JVM starts a thread called "main" and runs main() on it.
        // A Thread is an independent path of execution inside one program.
        // ============================================

        System.out.println("This code runs on thread: " + Thread.currentThread().getName());


        // ============================================
        // SECTION 2: THREE WAYS TO DESCRIBE THE WORK
        // 1) a Runnable (preferred: the work is separate from the thread)
        // 2) a subclass of Thread
        // 3) an inline lambda (a Runnable written short)
        // ============================================

        Runnable task = () -> System.out.println("  Runnable running on thread: " + Thread.currentThread().getName());
        Thread worker1 = new Thread(task, "worker-1");
        Thread worker2 = new Greeter("worker-2");
        Thread worker3 = new Thread(
                () -> System.out.println("  lambda running on thread: " + Thread.currentThread().getName()), "worker-3");


        // ============================================
        // SECTION 3: THE CLASSIC MISTAKE - run() vs start()
        // run()   just calls the method on the CURRENT thread: nothing concurrent happens.
        // start() asks the JVM to create a NEW thread, which then calls run().
        // ============================================

        System.out.println("Calling worker1.run() directly:");
        worker1.run();                       // prints "main": no new thread was created

        System.out.println("Calling worker1.start():");
        worker1.start();                     // prints "worker-1": a real new thread
        worker1.join();                      // wait until it finishes (see Section 4)


        // ============================================
        // SECTION 4: join() - WAITING FOR A THREAD TO FINISH
        // Without join(), main could carry on (or even end) before the workers do.
        // Started together, worker-2 and worker-3 run at the same time, so the
        // ORDER of their two lines can differ from run to run.
        // ============================================

        worker2.start();
        worker3.start();
        worker2.join();
        worker3.join();
        System.out.println("Both workers finished, main continues.");


        // ============================================
        // SECTION 5: A THREAD CAN ONLY BE STARTED ONCE
        // ============================================

        try {
            worker1.start();                 // worker1 already ran to completion
        } catch (IllegalThreadStateException e) {
            System.out.println("Caught IllegalThreadStateException: a thread cannot be restarted");
        }


        // ============================================
        // SECTION 6: DAEMON THREADS
        // The JVM exits when the last NON-daemon thread ends. A daemon thread is
        // a background helper (like a cleaner) and does not keep the program alive.
        // ============================================

        Thread background = new Thread(() -> {
            while (true) {
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    return;
                }
            }
        }, "background");
        background.setDaemon(true);          // must be set BEFORE start()
        background.start();
        System.out.println("background.isDaemon() = " + background.isDaemon());
        // This loop never ends, but the program still exits at the end of main().


        // ============================================
        // SECTION 7: AN EXCEPTION KILLS ONLY ITS OWN THREAD
        // The other threads (including main) carry on. An uncaught-exception
        // handler lets you report it instead of the default stack trace.
        // ============================================

        Thread boom = new Thread(() -> {
            throw new IllegalStateException("boom");
        }, "boom-thread");
        boom.setUncaughtExceptionHandler((t, e) ->
                System.out.println("  handler: " + t.getName() + " died with: " + e.getMessage()));
        boom.start();
        boom.join();
        System.out.println("main is still running after boom-thread died.");
    }
}
