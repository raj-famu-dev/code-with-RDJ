// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.Scanner;
import java.util.stream.Stream;

public class _2_ReadingTextFiles {

    static void deleteTree(Path root) throws IOException {
        try (Stream<Path> walk = Files.walk(root)) {
            for (Path p : walk.sorted(Comparator.reverseOrder()).toList()) {
                Files.delete(p);
            }
        }
    }

    public static void main(String[] args) throws IOException {

        Path dir = Files.createTempDirectory("rdj-read-");
        try {
            Path file = dir.resolve("poem.txt");
            Files.writeString(file, "roses are red\nviolets are blue\n\nJava has streams\nand so do you\n", StandardCharsets.UTF_8);

            // ============================================
            // SECTION 1: THE WHOLE FILE AS ONE STRING
            // Easiest. Fine for small files: the entire content is held in memory.
            // ============================================

            String whole = Files.readString(file);
            System.out.println("readString length: " + whole.length() + " characters");


            // ============================================
            // SECTION 2: ALL LINES AS A LIST
            // Still loads everything, but gives you the lines already split.
            // The line terminator is removed from each line.
            // ============================================

            List<String> lines = Files.readAllLines(file);
            System.out.println("readAllLines: " + lines.size() + " lines");
            System.out.println("  line 3 is empty: " + lines.get(2).isEmpty());


            // ============================================
            // SECTION 3: LINE BY LINE WITHOUT LOADING EVERYTHING
            // BufferedReader reads a chunk at a time: the right tool for big files.
            // try-with-resources CLOSES the reader even if an exception happens.
            // readLine() returns null at the end of the file.
            // ============================================

            int lineNumber = 0;
            int nonBlank = 0;
            try (BufferedReader reader = Files.newBufferedReader(file)) {
                String line;
                while ((line = reader.readLine()) != null) {
                    lineNumber++;
                    if (!line.isBlank()) {
                        nonBlank++;
                    }
                }
            }
            System.out.println("BufferedReader: " + lineNumber + " lines, " + nonBlank + " non-blank");


            // ============================================
            // SECTION 4: Files.lines - A STREAM OF LINES (LAZY)
            // The stream holds the file open, so it MUST be closed (try-with-resources).
            // ============================================

            try (Stream<String> stream = Files.lines(file)) {
                long withAre = stream.filter(l -> l.contains("are")).count();
                System.out.println("lines containing \"are\": " + withAre);
            }


            // ============================================
            // SECTION 5: Scanner - WHEN YOU NEED TOKENS (WORDS, NUMBERS)
            // ============================================

            try (Scanner scanner = new Scanner(file)) {
                int words = 0;
                while (scanner.hasNext()) {
                    scanner.next();
                    words++;
                }
                System.out.println("Scanner counted " + words + " words");
            }


            // ============================================
            // SECTION 6: CHARACTER ENCODING
            // Text on disk is bytes. A charset says how bytes become characters.
            // Since Java 18 the default is UTF-8, but older code and other systems
            // may differ, so being explicit is the safest habit.
            // ============================================

            Path accents = dir.resolve("accents.txt");
            String cafe = "caf\u00e9";                                // "cafe" with an accented e, written as an escape to keep this source ASCII
            Files.writeString(accents, cafe, StandardCharsets.UTF_8);
            System.out.println("the word has " + cafe.length() + " chars but takes " + Files.size(accents) + " bytes in UTF-8");
            String asLatin1 = Files.readString(accents, StandardCharsets.ISO_8859_1);
            System.out.println("read as ISO-8859-1 (WRONG charset): " + asLatin1.length() + " chars, same text as before: " + asLatin1.equals(cafe));


            // ============================================
            // SECTION 7: A MISSING FILE
            // ============================================

            try {
                Files.readString(dir.resolve("nothing.txt"));
            } catch (NoSuchFileException e) {
                System.out.println("NoSuchFileException: the file does not exist");
            }
            // new Scanner(path) / new FileReader(name) throw FileNotFoundException (older API).
            // Files.* throws NoSuchFileException. Both are IOExceptions.


            // ============================================
            // SECTION 8: WHICH ONE?
            // small file, need all of it  -> Files.readString / readAllLines
            // big file, process each line -> Files.lines or BufferedReader (close it!)
            // numbers and words           -> Scanner
            // ============================================

        } finally {
            deleteTree(dir);
        }
    }
}
