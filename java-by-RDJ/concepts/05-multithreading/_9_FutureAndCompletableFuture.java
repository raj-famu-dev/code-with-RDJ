// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class _9_FutureAndCompletableFuture {

    static void pause(int ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    // Pretend remote calls
    static String fetchUser(ExecutorService ex, int id) {
        pause(50);
        return "user-" + id;
    }

    static int fetchScore(int id) {
        pause(50);
        return id * 10;
    }

    public static void main(String[] args) throws Exception {

        // ============================================
        // SECTION 1: THE LIMIT OF A PLAIN Future
        // future.get() BLOCKS the calling thread. You cannot say "when this is
        // done, do that" without waiting. CompletableFuture lets you build a
        // PIPELINE of steps that run as results arrive.
        // We pass our own executor everywhere so we control (and shut down) the threads.
        // ============================================

        ExecutorService ex = Executors.newFixedThreadPool(4);
        try {

            // ============================================
            // SECTION 2: supplyAsync + thenApply
            // supplyAsync(supplier, executor) starts work in the background.
            // thenApply transforms the result (like map).
            // ============================================

            CompletableFuture<String> greeting = CompletableFuture
                    .supplyAsync(() -> fetchUser(ex, 7), ex)
                    .thenApply(name -> "Hello, " + name);
            System.out.println(greeting.get());


            // ============================================
            // SECTION 3: thenCompose - STEP 2 NEEDS THE RESULT OF STEP 1
            // thenApply with an async step inside would give a nested
            // CompletableFuture<CompletableFuture<..>>. thenCompose flattens it
            // (like flatMap).
            // ============================================

            CompletableFuture<Integer> score = CompletableFuture
                    .supplyAsync(() -> 3, ex)
                    .thenCompose(id -> CompletableFuture.supplyAsync(() -> fetchScore(id), ex));
            System.out.println("score of user 3 = " + score.get());


            // ============================================
            // SECTION 4: thenCombine - TWO INDEPENDENT STEPS, THEN MERGE
            // Both start immediately and run side by side: ~50 ms total, not ~100 ms.
            // ============================================

            long start = System.nanoTime();
            CompletableFuture<String> a = CompletableFuture.supplyAsync(() -> fetchUser(ex, 5), ex);
            CompletableFuture<Integer> b = CompletableFuture.supplyAsync(() -> fetchScore(5), ex);
            String combined = a.thenCombine(b, (u, s) -> u + " has score " + s).get();
            long ms = (System.nanoTime() - start) / 1_000_000;
            System.out.println(combined + "  (took about " + ms + " ms; two 50 ms calls ran in parallel)");


            // ============================================
            // SECTION 5: allOf - WAIT FOR MANY
            // allOf returns CompletableFuture<Void>, so you read each future after.
            // ============================================

            List<CompletableFuture<Integer>> many = List.of(
                    CompletableFuture.supplyAsync(() -> fetchScore(1), ex),
                    CompletableFuture.supplyAsync(() -> fetchScore(2), ex),
                    CompletableFuture.supplyAsync(() -> fetchScore(3), ex));
            CompletableFuture.allOf(many.toArray(new CompletableFuture<?>[0])).get();
            int total = 0;
            for (CompletableFuture<Integer> f : many) {
                total += f.join();                                  // join(): like get() without checked exceptions
            }
            System.out.println("total of three scores = " + total);


            // ============================================
            // SECTION 6: ERRORS TRAVEL DOWN THE PIPELINE
            // If a stage fails, later thenApply stages are SKIPPED and the failure
            // is delivered to exceptionally() / handle().
            // exceptionally: only on failure, supplies a fallback value.
            // handle:        always runs, gets (result, error).
            // ============================================

            CompletableFuture<Integer> failing = CompletableFuture
                    .<Integer>supplyAsync(() -> {
                        throw new IllegalStateException("service down");
                    }, ex)
                    .thenApply(x -> x + 1);                          // skipped

            System.out.println("exceptionally -> " + failing.exceptionally(err -> -1).get());
            System.out.println("handle        -> " + failing.handle((v, err) ->
                    err == null ? "ok " + v : "failed: " + err.getCause().getMessage()).get());

            try {
                failing.join();
            } catch (CompletionException e) {
                System.out.println("join() wraps it in CompletionException, cause = " + e.getCause());
            }


            // ============================================
            // SECTION 7: TIMEOUTS (JAVA 9+)
            // orTimeout fails the future with a TimeoutException; completeOnTimeout
            // supplies a default value instead.
            // ============================================

            CompletableFuture<String> slow = CompletableFuture
                    .supplyAsync(() -> {
                        pause(1500);
                        return "late";
                    }, ex)
                    .completeOnTimeout("default", 100, TimeUnit.MILLISECONDS);
            System.out.println("slow call with fallback: " + slow.get());


            // ============================================
            // SECTION 8: THE ASYNC SUFFIX AND THE DEFAULT POOL
            // thenApply     : runs on whichever thread finished the previous stage
            // thenApplyAsync: submits the step to a pool again
            // Without an executor argument, CompletableFuture uses the shared
            // ForkJoinPool.commonPool() (daemon threads), which is wrong for
            // blocking calls because it has very few threads. Pass your own executor.
            // ============================================
        } finally {
            ex.shutdown();
            ex.awaitTermination(3, TimeUnit.SECONDS);
            ex.shutdownNow();                                        // drops the leftover 1.5 s sleeper
        }
    }
}
