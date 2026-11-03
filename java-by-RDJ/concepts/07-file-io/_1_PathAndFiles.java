// Tags: #Java #FileIO #PathFiles | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.io.IOException;
import java.nio.file.DirectoryNotEmptyException;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Stream;

public class _1_PathAndFiles {

    // Deletes a folder and everything inside it (children first, then the folder itself)
    static void deleteTree(Path root) throws IOException {
        try (Stream<Path> walk = Files.walk(root)) {
            for (Path p : walk.sorted(Comparator.reverseOrder()).toList()) {
                Files.delete(p);
            }
        }
    }

    public static void main(String[] args) throws IOException {

        // ============================================
        // SECTION 1: Path = A LOCATION, NOT A FILE
        // A Path is just text describing where something would be. Creating one
        // touches nothing on disk, and the file need not exist.
        // ============================================

        Path relative = Path.of("data", "reports", "2026", "summary.txt");
        System.out.println("path:        " + relative);
        System.out.println("file name:   " + relative.getFileName());
        System.out.println("parent:      " + relative.getParent());
        System.out.println("name count:  " + relative.getNameCount());
        System.out.println("is absolute: " + relative.isAbsolute());
        System.out.println("exists?      " + Files.exists(relative) + "  (it is only a description)");


        // ============================================
        // SECTION 2: COMBINING AND CLEANING PATHS
        // resolve   : append one path to another
        // normalize : remove "." and ".." segments
        // relativize: the path that leads from one location to another
        // ============================================

        Path base = Path.of("project");
        Path file = base.resolve("src").resolve("Main.java");
        System.out.println("resolve:     " + file);

        Path messy = Path.of("project", "src", "..", "docs", ".", "readme.md");
        System.out.println("normalize:   " + messy + "  ->  " + messy.normalize());

        Path from = Path.of("project", "src");
        Path to = Path.of("project", "docs", "readme.md");
        System.out.println("relativize:  " + from.relativize(to));
        // Never glue paths with "+" and "/" yourself: Windows uses "\", Linux and macOS use "/".


        // ============================================
        // SECTION 3: WORKING IN A TEMPORARY FOLDER
        // Everything below happens in a fresh temp directory that is deleted at the end,
        // so this program never touches your own files.
        // ============================================

        Path workspace = Files.createTempDirectory("rdj-fileio-");
        try {
            Path nested = workspace.resolve("a").resolve("b").resolve("c");
            Files.createDirectories(nested);                       // creates every missing level
            System.out.println("created nested folders: " + Files.isDirectory(nested));

            Path notes = workspace.resolve("notes.txt");
            Files.writeString(notes, "hello files\n");
            System.out.println("exists: " + Files.exists(notes)
                    + ", isRegularFile: " + Files.isRegularFile(notes)
                    + ", size: " + Files.size(notes) + " bytes");


            // ============================================
            // SECTION 4: COPY, MOVE, DELETE
            // By default copy and move REFUSE to overwrite an existing target.
            // ============================================

            Path copy = workspace.resolve("notes-copy.txt");
            Files.copy(notes, copy);
            try {
                Files.copy(notes, copy);                           // target already exists
            } catch (java.nio.file.FileAlreadyExistsException e) {
                System.out.println("FileAlreadyExistsException: copy will not overwrite by default");
            }
            Files.copy(notes, copy, StandardCopyOption.REPLACE_EXISTING);   // explicit permission to overwrite

            Path moved = nested.resolve("moved.txt");
            Files.move(copy, moved);
            System.out.println("after move: source exists = " + Files.exists(copy) + ", target exists = " + Files.exists(moved));


            // ============================================
            // SECTION 5: LISTING A FOLDER
            // Files.list gives the entries of ONE folder; Files.walk goes through all levels.
            // Both return a Stream that holds an open handle: ALWAYS use try-with-resources.
            // Order is not guaranteed, so we sort for a stable print.
            // ============================================

            try (Stream<Path> entries = Files.list(workspace)) {
                List<String> names = entries.map(p -> p.getFileName().toString()).sorted().toList();
                System.out.println("Files.list(workspace): " + names);
            }
            try (Stream<Path> all = Files.walk(workspace)) {
                List<String> relativeNames = all.map(p -> workspace.relativize(p).toString()).sorted().toList();
                System.out.println("Files.walk(workspace): " + relativeNames);
            }


            // ============================================
            // SECTION 6: THE EXCEPTIONS YOU WILL MEET
            // ============================================

            try {
                Files.readString(workspace.resolve("missing.txt"));
            } catch (NoSuchFileException e) {
                System.out.println("NoSuchFileException: the file does not exist");
            }

            try {
                Files.delete(workspace.resolve("a"));              // folder still has content
            } catch (DirectoryNotEmptyException e) {
                System.out.println("DirectoryNotEmptyException: delete a folder's contents first");
            }

            System.out.println("deleteIfExists on a missing file: " + Files.deleteIfExists(workspace.resolve("nope.txt")));

        } finally {
            deleteTree(workspace);
            System.out.println("cleanup done, workspace still exists: " + Files.exists(workspace));
        }

        // ============================================
        // SECTION 7: RULES TO REMEMBER
        // 1) Use java.nio.file (Path, Files), not the old java.io.File, in new code.
        // 2) A Path is only a description; Files.* talks to the disk.
        // 3) Almost every Files method throws IOException: file systems fail.
        // 4) Streams from Files.list/walk/lines must be closed.
        // 5) Tests and experiments belong in a temp directory you clean up.
        // ============================================
    }
}
