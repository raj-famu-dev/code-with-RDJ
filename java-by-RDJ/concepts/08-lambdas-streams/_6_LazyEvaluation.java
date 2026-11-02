// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.List;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class _6_LazyEvaluation {

    public static void main(String[] args) {

        List<String> names = List.of("Ada", "Linus", "Grace", "Alan", "Margaret");

        // ============================================
        // SECTION 1: NOTHING HAPPENS WITHOUT A TERMINAL OPERATION
        // Intermediate operations only DESCRIBE the pipeline. peek() lets us watch.
        // ============================================

        System.out.println("--- building a pipeline with NO terminal operation ---");
        Stream<String> pipeline = names.stream()
                .peek(n -> System.out.println("  peek saw " + n))
                .filter(n -> n.length() > 3);
        System.out.println("pipeline built. Printed anything from peek? No: it has not run.");

        System.out.println("--- now add a terminal operation ---");
        long count = pipeline.count();
        System.out.println("count = " + count);


        // ============================================
        // SECTION 2: ELEMENTS FLOW ONE AT A TIME THROUGH THE WHOLE PIPELINE
        // Not "all filters, then all maps". Each element goes through every step,
        // then the next element starts. Watch the interleaving:
        // ============================================

        System.out.println("--- vertical processing ---");
        List<String> out = names.stream()
                .filter(n -> {
                    System.out.println("  filter " + n);
                    return n.length() > 3;
                })
                .map(n -> {
                    System.out.println("  map    " + n);
                    return n.toUpperCase();
                })
                .toList();
        System.out.println("result: " + out);


        // ============================================
        // SECTION 3: SHORT-CIRCUITING - STOP AS SOON AS THE ANSWER IS KNOWN
        // findFirst, anyMatch, allMatch, noneMatch, limit stop the pipeline early.
        // ============================================

        System.out.println("--- findFirst stops at the first match ---");
        String firstLong = names.stream()
                .peek(n -> System.out.println("  looking at " + n))
                .filter(n -> n.length() > 4)
                .findFirst()
                .orElse("none");
        System.out.println("first long name: " + firstLong + "   (Alan and Margaret were never examined)");

        System.out.println("--- anyMatch stops at the first true ---");
        boolean any = names.stream()
                .peek(n -> System.out.println("  checking " + n))
                .anyMatch(n -> n.startsWith("G"));
        System.out.println("any starts with G: " + any);


        // ============================================
        // SECTION 4: INFINITE STREAMS ARE FINE BECAUSE OF LAZINESS
        // limit() short-circuits, so only what is needed is ever produced.
        // ============================================

        System.out.println("first 5 powers of two: " + Stream.iterate(1, n -> n * 2).limit(5).toList());
        System.out.println("first 3 multiples of 7 above 100: "
                + IntStream.iterate(1, n -> n + 1).filter(n -> n % 7 == 0).filter(n -> n > 100).limit(3).boxed().toList());
        // Without limit/findFirst/anyMatch an infinite stream never ends:
        //   Stream.iterate(1, n -> n + 1).count();      // never returns (do not run this)


        // ============================================
        // SECTION 5: sorted() IS A "BARRIER"
        // To sort, it must see EVERY element first, so laziness stops at that point
        // and limit() after sorted() cannot save work before it.
        // ============================================

        System.out.println("--- sorted needs all elements ---");
        List<String> firstTwoSorted = names.stream()
                .peek(n -> System.out.println("  before sorted: " + n))
                .sorted()
                .limit(2)
                .toList();
        System.out.println("first two alphabetically: " + firstTwoSorted);


        // ============================================
        // SECTION 6: SIDE EFFECTS IN A PIPELINE ARE A TRAP
        // Because of laziness and short-circuiting, code inside map/filter/peek may run
        // fewer times than you expect, or in an order you did not intend.
        // peek is for DEBUGGING only. Do not use it (or map) to do real work.
        // Counting with peek is unreliable:
        // ============================================

        int[] counter = {0};
        long n = names.stream().peek(x -> counter[0]++).count();
        System.out.println("count() = " + n + ", peek ran " + counter[0] + " times"
                + "  (since Java 9, count() may skip the pipeline if it can compute the size directly)");
    }
}
