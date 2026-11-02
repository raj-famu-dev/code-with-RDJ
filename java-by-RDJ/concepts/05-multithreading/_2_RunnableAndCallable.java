// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.io.IOException;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class _2_RunnableAndCallable {
    public static void main(String[] args) throws Exception {

        // ============================================
        // SECTION 1: Runnable - WORK WITH NO RESULT
        // void run(): it cannot return a value or throw a checked exception.
        // To get something out, you need a shared holder (awkward).
        // ============================================

        int[] holder = new int[1];
        Thread plain = new Thread(() -> holder[0] = 6 * 7);
        plain.start();
        plain.join();                         // without join(), the holder might still be 0
        System.out.println("Result smuggled out through an array: " + holder[0]);


        // ============================================
        // SECTION 2: Callable<V> - WORK THAT RETURNS A VALUE
        // V call() throws Exception. A FutureTask wraps a Callable so a plain
        // Thread can run it, and the result is collected with get().
        // (Executors in _8 do this wrapping for you.)
        // ============================================

        Callable<Integer> job = () -> {
            Thread.sleep(50);                 // pretend to do something slow
            return 6 * 7;
        };
        FutureTask<Integer> task = new FutureTask<>(job);
        new Thread(task, "callable-thread").start();
        System.out.println("isDone right away? " + task.isDone());
        System.out.println("get() waits, then returns: " + task.get());
        System.out.println("isDone now? " + task.isDone());


        // ============================================
        // SECTION 3: A Callable MAY THROW A CHECKED EXCEPTION
        // The exception is captured and re-delivered, wrapped in an
        // ExecutionException, when you call get(). The original is the cause.
        // ============================================

        Callable<String> risky = () -> {
            throw new IOException("disk full");
        };
        FutureTask<String> riskyTask = new FutureTask<>(risky);
        new Thread(riskyTask).start();
        try {
            riskyTask.get();
        } catch (ExecutionException e) {
            System.out.println("get() threw ExecutionException, cause = " + e.getCause());
        }
        // Runnable r = () -> { throw new IOException("x"); };   // COMPILE ERROR: unreported checked exception


        // ============================================
        // SECTION 4: DO NOT WAIT FOREVER - get WITH A TIMEOUT
        // ============================================

        FutureTask<String> slow = new FutureTask<>(() -> {
            Thread.sleep(3000);
            return "late";
        });
        Thread slowThread = new Thread(slow, "slow-thread");
        slowThread.setDaemon(true);           // so a stuck worker cannot keep the JVM alive
        slowThread.start();
        try {
            slow.get(100, TimeUnit.MILLISECONDS);
        } catch (TimeoutException e) {
            System.out.println("Gave up after 100 ms: TimeoutException");
            slow.cancel(true);                // asks the worker to stop (interrupts it)
            System.out.println("isCancelled = " + slow.isCancelled());
        }


        // ============================================
        // SECTION 5: SUMMARY
        // Runnable : run()  -> void, no checked exceptions
        // Callable : call() -> V, may throw Exception
        // Future   : a handle to a result that is not ready yet
        // get() blocks; get(timeout) can give up; cancel() asks the task to stop.
        // ============================================
    }
}
