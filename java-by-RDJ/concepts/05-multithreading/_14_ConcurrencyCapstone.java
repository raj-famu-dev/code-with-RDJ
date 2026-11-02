// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.TreeMap;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

/**
 * CAPSTONE: a concurrent word counter.
 * 1. Create a temporary folder with 12 generated text files.
 * 2. Count words sequentially (the trusted answer).
 * 3. Count the same files in parallel with a thread pool, two ways:
 *      (a) each task returns its own private map; main merges them (no sharing = no races)
 *      (b) all tasks update ONE shared ConcurrentHashMap using merge()
 * 4. Check that all three answers are identical. Clean up.
 * Uses: threads, ExecutorService, Callable/Future, ConcurrentHashMap, try/finally.
 */
public class _14_ConcurrencyCapstone {

    static final String[] VOCABULARY = {
            "java", "thread", "lock", "queue", "pool", "future", "atomic", "volatile", "monitor", "task"
    };

    // ---------- STEP 1: generate files (seeded Random so every run is identical) ----------
    static List<Path> createFiles(Path dir, int fileCount, int wordsPerFile) throws IOException {
        List<Path> files = new ArrayList<>();
        Random random = new Random(42);
        for (int f = 0; f < fileCount; f++) {
            StringBuilder text = new StringBuilder();
            for (int w = 0; w < wordsPerFile; w++) {
                text.append(VOCABULARY[random.nextInt(VOCABULARY.length)]);
                text.append(w % 10 == 9 ? "\n" : " ");
            }
            Path file = dir.resolve("file-" + f + ".txt");
            Files.writeString(file, text.toString());
            files.add(file);
        }
        return files;
    }

    // ---------- the actual work: count the words in ONE file ----------
    static Map<String, Integer> countFile(Path file) throws IOException {
        Map<String, Integer> counts = new TreeMap<>();
        for (String word : Files.readString(file).split("\\s+")) {
            if (!word.isEmpty()) {
                counts.merge(word, 1, Integer::sum);
            }
        }
        return counts;
    }

    // ---------- STEP 2: sequential baseline ----------
    static Map<String, Integer> countSequential(List<Path> files) throws IOException {
        Map<String, Integer> total = new TreeMap<>();
        for (Path file : files) {
            countFile(file).forEach((w, c) -> total.merge(w, c, Integer::sum));
        }
        return total;
    }

    // ---------- STEP 3a: each task returns a private map, main merges ----------
    static Map<String, Integer> countWithFutures(List<Path> files, ExecutorService pool) throws Exception {
        List<Future<Map<String, Integer>>> futures = new ArrayList<>();
        for (Path file : files) {
            Callable<Map<String, Integer>> task = () -> countFile(file);
            futures.add(pool.submit(task));
        }
        Map<String, Integer> total = new TreeMap<>();
        for (Future<Map<String, Integer>> f : futures) {
            f.get(5, TimeUnit.SECONDS).forEach((w, c) -> total.merge(w, c, Integer::sum));
        }
        return total;
    }

    // ---------- STEP 3b: all tasks update one shared concurrent map ----------
    static Map<String, Integer> countWithSharedMap(List<Path> files, ExecutorService pool) throws Exception {
        ConcurrentHashMap<String, Integer> shared = new ConcurrentHashMap<>();
        List<Future<?>> futures = new ArrayList<>();
        for (Path file : files) {
            futures.add(pool.submit(() -> {
                try {
                    for (String word : Files.readString(file).split("\\s+")) {
                        if (!word.isEmpty()) {
                            shared.merge(word, 1, Integer::sum);     // atomic update: safe from many threads
                        }
                    }
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }));
        }
        for (Future<?> f : futures) {
            f.get(5, TimeUnit.SECONDS);                              // also surfaces any task exception
        }
        return new TreeMap<>(shared);
    }

    static void deleteRecursively(Path dir) throws IOException {
        try (Stream<Path> walk = Files.walk(dir)) {
            walk.sorted(Comparator.reverseOrder()).forEach(p -> p.toFile().delete());
        }
    }

    public static void main(String[] args) throws Exception {

        int fileCount = 12;
        int wordsPerFile = 20_000;
        Path dir = Files.createTempDirectory("rdj-capstone-");
        ExecutorService pool = Executors.newFixedThreadPool(4);

        try {
            List<Path> files = createFiles(dir, fileCount, wordsPerFile);
            System.out.println("created " + files.size() + " files of " + wordsPerFile + " words in a temp folder");

            Map<String, Integer> sequential = countSequential(files);
            Map<String, Integer> viaFutures = countWithFutures(files, pool);
            Map<String, Integer> viaSharedMap = countWithSharedMap(files, pool);

            int total = sequential.values().stream().mapToInt(Integer::intValue).sum();
            System.out.println("total words counted: " + total + " (expected " + fileCount * wordsPerFile + ")");

            System.out.println("top words (count desc, then alphabetical):");
            sequential.entrySet().stream()
                    .sorted(Map.Entry.<String, Integer>comparingByValue().reversed()
                            .thenComparing(Map.Entry.comparingByKey()))
                    .limit(5)
                    .forEach(e -> System.out.println("  " + e.getKey() + " = " + e.getValue()));

            System.out.println("futures result equals sequential:   " + sequential.equals(viaFutures));
            System.out.println("shared map result equals sequential: " + sequential.equals(viaSharedMap));
        } finally {
            pool.shutdown();
            if (!pool.awaitTermination(5, TimeUnit.SECONDS)) {
                pool.shutdownNow();
            }
            deleteRecursively(dir);
            System.out.println("cleanup done, temp folder still exists: " + Files.exists(dir));
        }

        // ============================================
        // WHAT THE CAPSTONE SHOWS
        // - Design (a) shares NOTHING while counting. It is the easiest to reason about.
        // - Design (b) shares ONE map, made safe by merge(). Fine, but you must know
        //   which operations are atomic.
        // - Both are checked against the single-threaded answer: ALWAYS test a
        //   concurrent version against a simple sequential one.
        // - Always shut the pool down and clean up in finally.
        // ============================================
    }
}
