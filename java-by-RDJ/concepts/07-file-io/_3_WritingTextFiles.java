// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Stream;

public class _3_WritingTextFiles {

    static void deleteTree(Path root) throws IOException {
        try (Stream<Path> walk = Files.walk(root)) {
            for (Path p : walk.sorted(Comparator.reverseOrder()).toList()) {
                Files.delete(p);
            }
        }
    }

    // A SAFER WAY TO SAVE: write to a temp file next to the target, then move it into place.
    // If the program crashes halfway, the old file is still intact instead of half-written.
    static void saveSafely(Path target, String content) throws IOException {
        Path temp = Files.createTempFile(target.getParent(), "save-", ".tmp");
        try {
            Files.writeString(temp, content, StandardCharsets.UTF_8);
            try {
                Files.move(temp, target, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException e) {
                Files.move(temp, target, StandardCopyOption.REPLACE_EXISTING);   // fallback when the file system cannot do it atomically
            }
        } finally {
            Files.deleteIfExists(temp);                            // nothing left behind on failure
        }
    }

    public static void main(String[] args) throws IOException {

        Path dir = Files.createTempDirectory("rdj-write-");
        try {
            Path file = dir.resolve("log.txt");

            // ============================================
            // SECTION 1: Files.writeString - THE SIMPLE WAY
            // Default behaviour: CREATE the file if missing, or TRUNCATE (erase) it if it exists.
            // That default is why careless code silently destroys data.
            // ============================================

            Files.writeString(file, "first run\n");
            Files.writeString(file, "second run\n");               // replaces everything
            System.out.println("after two plain writes: " + Files.readString(file).trim());


            // ============================================
            // SECTION 2: APPEND INSTEAD OF REPLACE
            // OpenOption flags change the behaviour.
            // ============================================

            Files.writeString(file, "third line\n", StandardOpenOption.APPEND);
            System.out.println("after append: " + Files.readAllLines(file));


            // ============================================
            // SECTION 3: CREATE_NEW - FAIL RATHER THAN OVERWRITE
            // ============================================

            try {
                Files.writeString(file, "oops", StandardOpenOption.CREATE_NEW);
            } catch (FileAlreadyExistsException e) {
                System.out.println("CREATE_NEW refused to overwrite an existing file");
            }


            // ============================================
            // SECTION 4: WRITING A LIST OF LINES
            // ============================================

            Path list = dir.resolve("names.txt");
            Files.write(list, List.of("Ada", "Linus", "Grace"));
            System.out.println("Files.write(lines) -> " + Files.readAllLines(list));


            // ============================================
            // SECTION 5: BufferedWriter - MANY SMALL WRITES, EFFICIENTLY
            // Collects text in memory and writes in big chunks. try-with-resources
            // FLUSHES and CLOSES it. If you forget to close, the last part may be lost.
            // ============================================

            Path table = dir.resolve("table.txt");
            try (BufferedWriter writer = Files.newBufferedWriter(table)) {
                for (int i = 1; i <= 3; i++) {
                    writer.write("row " + i);
                    writer.newLine();                              // uses the platform's line separator
                }
            }
            System.out.println("BufferedWriter wrote " + Files.readAllLines(table).size() + " lines");


            // ============================================
            // SECTION 6: PrintWriter - printf AND println FOR FILES
            // ============================================

            Path report = dir.resolve("report.txt");
            try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(report))) {
                out.printf("%-8s %5.1f%n", "alpha", 3.14159);
                out.printf("%-8s %5.1f%n", "beta", 42.0);
            }
            System.out.print("PrintWriter output:\n" + Files.readString(report));
            // Note: PrintWriter never throws IOException; check out.checkError() if it matters.


            // ============================================
            // SECTION 7: SAFE SAVING (WRITE TEMP, THEN MOVE)
            // ============================================

            Path settings = dir.resolve("settings.txt");
            saveSafely(settings, "theme=dark\n");
            saveSafely(settings, "theme=light\n");                 // replaces the old file in one step
            System.out.println("settings after two safe saves: " + Files.readString(settings).trim());
            try (Stream<Path> left = Files.list(dir)) {
                long tmpFiles = left.filter(p -> p.getFileName().toString().endsWith(".tmp")).count();
                System.out.println("leftover .tmp files: " + tmpFiles);
            }


            // ============================================
            // SECTION 8: RULES TO REMEMBER
            // 1) The default write ERASES the file. Choose APPEND or CREATE_NEW on purpose.
            // 2) Always close writers (try-with-resources): closing flushes the buffer.
            // 3) Write a temp file and move it for anything important.
            // 4) Pass the charset explicitly if the file is shared with other systems.
            // ============================================

        } finally {
            deleteTree(dir);
        }
    }
}
