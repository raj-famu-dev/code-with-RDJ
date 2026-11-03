// Tags: #Java #FileIO #BinaryIO | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Comparator;
import java.util.stream.Stream;

public class _4_BinaryIO {

    static void deleteTree(Path root) throws IOException {
        try (Stream<Path> walk = Files.walk(root)) {
            for (Path p : walk.sorted(Comparator.reverseOrder()).toList()) {
                Files.delete(p);
            }
        }
    }

    // A made-up file format: 4-byte magic "RDJ1", then a count, then (id, score) pairs
    static final int MAGIC = 0x52444A31;                          // the bytes 'R' 'D' 'J' '1'

    public static void main(String[] args) throws IOException {

        Path dir = Files.createTempDirectory("rdj-binary-");
        try {

            // ============================================
            // SECTION 1: BYTES ARE THE BASIC UNIT
            // Text files are just bytes with an agreed meaning. Binary files (images,
            // zips, your own formats) carry other meanings. A byte holds 0..255,
            // but Java's byte is SIGNED (-128..127), so mask with & 0xFF to read it.
            // ============================================

            byte negative = (byte) 200;
            System.out.println("(byte) 200 = " + negative + ", as 0..255 = " + (negative & 0xFF));


            // ============================================
            // SECTION 2: WHOLE FILE AS A byte[]
            // ============================================

            Path raw = dir.resolve("raw.bin");
            Files.write(raw, new byte[]{1, 2, 3, (byte) 255});
            byte[] back = Files.readAllBytes(raw);
            System.out.println("readAllBytes: " + Arrays.toString(back) + ", size " + Files.size(raw));


            // ============================================
            // SECTION 3: STREAMS + A BUFFER - COPYING ANY SIZE OF FILE
            // Read a chunk into a byte[], write exactly the bytes read, repeat until -1.
            // Never load a huge file whole when you can stream it.
            // ============================================

            byte[] payload = new byte[10_000];
            for (int i = 0; i < payload.length; i++) {
                payload[i] = (byte) (i % 251);
            }
            Path source = dir.resolve("source.bin");
            Path copy = dir.resolve("copy.bin");
            Files.write(source, payload);

            long total = 0;
            try (InputStream in = new BufferedInputStream(Files.newInputStream(source));
                 OutputStream out = new BufferedOutputStream(Files.newOutputStream(copy))) {
                byte[] buffer = new byte[1024];
                int read;
                while ((read = in.read(buffer)) != -1) {
                    out.write(buffer, 0, read);                    // write 'read' bytes, NOT buffer.length
                    total += read;
                }
            }
            System.out.println("copied " + total + " bytes, identical: " + Arrays.equals(Files.readAllBytes(source), Files.readAllBytes(copy)));


            // ============================================
            // SECTION 4: DataOutputStream / DataInputStream - TYPED VALUES
            // Writes ints, longs, doubles, booleans, strings in a fixed binary layout
            // (big-endian). You must READ in exactly the SAME ORDER you wrote.
            // ============================================

            Path scores = dir.resolve("scores.dat");
            try (DataOutputStream out = new DataOutputStream(new BufferedOutputStream(Files.newOutputStream(scores)))) {
                out.writeInt(MAGIC);
                out.writeInt(3);                                   // number of records that follow
                out.writeUTF("ada");
                out.writeDouble(91.5);
                out.writeUTF("linus");
                out.writeDouble(78.25);
                out.writeUTF("grace");
                out.writeDouble(99.0);
            }
            System.out.println("scores.dat is " + Files.size(scores) + " bytes");

            try (DataInputStream in = new DataInputStream(new BufferedInputStream(Files.newInputStream(scores)))) {
                int magic = in.readInt();
                if (magic != MAGIC) {
                    throw new IOException("not our file format");
                }
                int count = in.readInt();
                for (int i = 0; i < count; i++) {
                    String name = in.readUTF();
                    double score = in.readDouble();
                    System.out.println("  record " + (i + 1) + ": " + name + " = " + score);
                }
                try {
                    in.readInt();                                  // nothing left
                } catch (EOFException e) {
                    System.out.println("EOFException: tried to read past the end");
                }
            }


            // ============================================
            // SECTION 5: WRONG ORDER = GARBAGE, NOT AN ERROR
            // The file has no labels. Read the first 4 bytes as a double and Java
            // happily gives you nonsense.
            // ============================================

            try (DataInputStream in = new DataInputStream(Files.newInputStream(scores))) {
                double nonsense = in.readDouble();
                System.out.println("reading an int and an int as one double gives: " + nonsense + " (silent garbage)");
            }


            // ============================================
            // SECTION 6: BYTE ORDER (ENDIANNESS)
            // The int 1 can be stored as 00 00 00 01 (big-endian) or 01 00 00 00 (little-endian).
            // Java's Data*Stream and ByteBuffer default to big-endian; many file
            // formats and CPUs use little-endian. ByteBuffer lets you choose.
            // ============================================

            byte[] big = ByteBuffer.allocate(4).order(ByteOrder.BIG_ENDIAN).putInt(1).array();
            byte[] little = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(1).array();
            System.out.println("1 big-endian:    " + Arrays.toString(big));
            System.out.println("1 little-endian: " + Arrays.toString(little));


            // ============================================
            // SECTION 7: TEXT IS JUST BYTES WITH A CHARSET
            // ============================================

            String text = "Hi \u00e9";                              // "Hi" plus an accented e (an escape keeps this source ASCII)
            byte[] encoded = text.getBytes(StandardCharsets.UTF_8);
            System.out.println("4 characters, but " + encoded.length + " bytes in UTF-8: " + Arrays.toString(encoded));
            System.out.println("decoded back equals the original: " + new String(encoded, StandardCharsets.UTF_8).equals(text));

        } finally {
            deleteTree(dir);
        }
    }
}
