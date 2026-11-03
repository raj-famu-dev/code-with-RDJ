// Tags: #Java #FileIO #FileIOCapstone | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Stream;

/**
 * CAPSTONE: a log analyzer.
 * 1. Generate a log file in a temp folder (7 valid lines + 3 broken ones).
 * 2. Read it line by line with a BufferedReader (try-with-resources).
 * 3. Parse each line; malformed lines are counted and reported, not allowed to crash the run.
 * 4. Count entries per level and per service; find the slowest request.
 * 5. Write the summary as a CSV, saved safely (temp file then move).
 * 6. Read the CSV back, verify it, clean up.
 * Uses: Path/Files, buffered reading, exceptions, CSV, safe saving, cleanup in finally.
 */
public class _7_FileIOCapstone {

    // One parsed log line:   2026-03-01T10:15:30 INFO payments 120ms Payment accepted
    record LogEntry(String timestamp, String level, String service, int millis, String message) { }

    static class ParseException extends Exception {
        private static final long serialVersionUID = 1L;

        ParseException(String message) {
            super(message);
        }
    }

    static LogEntry parse(String line) throws ParseException {
        String[] parts = line.split(" ", 5);                       // at most 5 pieces: the message keeps its spaces
        if (parts.length < 5) {
            throw new ParseException("expected 5 parts but found " + parts.length);
        }
        String level = parts[1];
        if (!List.of("INFO", "WARN", "ERROR").contains(level)) {
            throw new ParseException("unknown level '" + level + "'");
        }
        if (!parts[3].endsWith("ms")) {
            throw new ParseException("duration must end with 'ms' but was '" + parts[3] + "'");
        }
        int millis;
        try {
            millis = Integer.parseInt(parts[3].substring(0, parts[3].length() - 2));
        } catch (NumberFormatException e) {
            throw new ParseException("duration is not a number: '" + parts[3] + "'");
        }
        return new LogEntry(parts[0], level, parts[2], millis, parts[4]);
    }

    static void deleteTree(Path root) throws IOException {
        try (Stream<Path> walk = Files.walk(root)) {
            for (Path p : walk.sorted(Comparator.reverseOrder()).toList()) {
                Files.delete(p);
            }
        }
    }

    static void saveSafely(Path target, List<String> lines) throws IOException {
        Path temp = Files.createTempFile(target.getParent(), "summary-", ".tmp");
        try {
            Files.write(temp, lines);
            try {
                Files.move(temp, target, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException e) {
                Files.move(temp, target, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally {
            Files.deleteIfExists(temp);
        }
    }

    public static void main(String[] args) throws IOException {

        Path dir = Files.createTempDirectory("rdj-capstone-io-");
        try {
            // ---------- STEP 1: create the input ----------
            Path log = dir.resolve("app.log");
            Files.write(log, List.of(
                    "2026-03-01T10:15:30 INFO payments 120ms Payment accepted",
                    "2026-03-01T10:15:31 INFO search 45ms Query served",
                    "2026-03-01T10:15:32 WARN payments 900ms Slow card check",
                    "this line is garbage",
                    "2026-03-01T10:15:34 ERROR payments 2500ms Card gateway timeout",
                    "2026-03-01T10:15:35 INFO search 52ms Query served",
                    "2026-03-01T10:15:36 DEBUG search 10ms Unknown level on purpose",
                    "2026-03-01T10:15:37 INFO auth 33ms User logged in",
                    "2026-03-01T10:15:38 WARN auth fastms Duration is not a number",
                    "2026-03-01T10:15:39 ERROR auth 15ms Bad password"));

            // ---------- STEP 2 + 3: read and parse ----------
            List<LogEntry> entries = new ArrayList<>();
            List<String> problems = new ArrayList<>();
            try (BufferedReader reader = Files.newBufferedReader(log)) {
                String line;
                int lineNumber = 0;
                while ((line = reader.readLine()) != null) {
                    lineNumber++;
                    try {
                        entries.add(parse(line));
                    } catch (ParseException e) {
                        problems.add("line " + lineNumber + ": " + e.getMessage());
                    }
                }
            }
            System.out.println("parsed " + entries.size() + " valid lines, skipped " + problems.size());
            problems.forEach(p -> System.out.println("  skipped -> " + p));

            // ---------- STEP 4: analyse ----------
            Map<String, Integer> byLevel = new TreeMap<>();
            Map<String, Integer> totalMillis = new TreeMap<>();
            Map<String, Integer> countByService = new TreeMap<>();
            LogEntry slowest = null;
            for (LogEntry e : entries) {
                byLevel.merge(e.level(), 1, Integer::sum);
                totalMillis.merge(e.service(), e.millis(), Integer::sum);
                countByService.merge(e.service(), 1, Integer::sum);
                if (slowest == null || e.millis() > slowest.millis()) {
                    slowest = e;
                }
            }
            System.out.println("entries per level: " + byLevel);
            System.out.println("slowest request: " + slowest.service() + " " + slowest.millis() + "ms (" + slowest.message() + ")");

            // ---------- STEP 5: write the summary CSV safely ----------
            List<String> csv = new ArrayList<>();
            csv.add("service,requests,avg_ms");
            for (String service : countByService.keySet()) {
                int count = countByService.get(service);
                csv.add(service + "," + count + "," + (totalMillis.get(service) / count));   // integer average
            }
            Path summary = dir.resolve("summary.csv");
            saveSafely(summary, csv);

            // ---------- STEP 6: read back and verify ----------
            List<String> readBack = Files.readAllLines(summary);
            System.out.println("--- summary.csv ---");
            readBack.forEach(System.out::println);
            System.out.println("summary matches what we wrote: " + readBack.equals(csv));
            try (Stream<Path> left = Files.list(dir)) {
                System.out.println("leftover .tmp files: " + left.filter(p -> p.toString().endsWith(".tmp")).count());
            }

        } finally {
            deleteTree(dir);
            System.out.println("cleanup done, temp folder still exists: " + Files.exists(dir));
        }

        // ============================================
        // WHAT THE CAPSTONE SHOWS
        // - Bad input is EXPECTED: validate each line, report the problem with its line
        //   number, and keep going instead of crashing on the first bad line.
        // - Stream the file (BufferedReader) so the file size does not matter.
        // - Save results with temp-then-move so a crash never leaves a half-written file.
        // - Everything is created in a temp folder and deleted in finally.
        // ============================================
    }
}
