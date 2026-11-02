// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class _3_StreamBasics {

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT A STREAM IS (AND IS NOT)
        // A stream is a PIPELINE that describes what to do with a sequence of values.
        //   - It is NOT a collection: it stores nothing.
        //   - It does NOT change its source.
        //   - It can be used ONCE.
        // A pipeline has three parts:
        //   SOURCE  ->  zero or more INTERMEDIATE operations  ->  one TERMINAL operation
        //   list        filter, map, sorted ...                   collect, count, forEach ...
        // Nothing runs until the terminal operation is called (see _6_LazyEvaluation).
        // ============================================

        List<String> names = List.of("Linus", "Ada", "Grace", "Alan", "Margaret", "Ada");

        // the whole pipeline in one go:
        List<String> result = names.stream()                       // SOURCE
                .filter(n -> n.length() > 3)                       // intermediate: keep long names
                .map(String::toUpperCase)                          // intermediate: transform
                .sorted()                                          // intermediate: order
                .toList();                                         // TERMINAL: produce a list
        System.out.println("pipeline result: " + result);
        System.out.println("source is unchanged: " + names);


        // ============================================
        // SECTION 2: WAYS TO CREATE A STREAM (SOURCES)
        // ============================================

        Stream<String> fromList = names.stream();
        Stream<String> fromValues = Stream.of("x", "y", "z");
        Stream<Integer> fromArray = Arrays.stream(new Integer[]{3, 1, 2});
        IntStream range = IntStream.range(0, 5);                   // 0,1,2,3,4 (end excluded)
        IntStream rangeClosed = IntStream.rangeClosed(1, 5);       // 1,2,3,4,5 (end included)
        Stream<Integer> generated = Stream.iterate(1, n -> n * 2).limit(6);   // 1,2,4,8,16,32: infinite source, limited
        Stream<String> empty = Stream.empty();

        System.out.println("fromValues:  " + fromValues.toList());
        System.out.println("fromArray:   " + fromArray.toList());
        System.out.println("range:       " + range.boxed().toList());
        System.out.println("rangeClosed: " + rangeClosed.boxed().toList());
        System.out.println("iterate:     " + generated.toList());
        System.out.println("empty:       " + empty.toList());
        System.out.println("fromList count: " + fromList.count());

        Map<String, Integer> ages = Map.of("Ada", 36);
        System.out.println("from a map's entries: " + ages.entrySet().stream().map(e -> e.getKey() + "=" + e.getValue()).toList());
        System.out.println("characters of a string: " + "abc".chars().mapToObj(c -> String.valueOf((char) c)).toList());


        // ============================================
        // SECTION 3: INTERMEDIATE vs TERMINAL
        // Intermediate: return ANOTHER Stream (so you can keep chaining). They are lazy.
        //   filter, map, flatMap, sorted, distinct, limit, skip, peek
        // Terminal: return something else (or nothing) and START the pipeline.
        //   collect, toList, forEach, count, sum, min, max, reduce, anyMatch, allMatch, noneMatch, findFirst
        // ============================================

        long count = names.stream().filter(n -> n.startsWith("A")).count();
        boolean anyLong = names.stream().anyMatch(n -> n.length() > 7);
        boolean allNonEmpty = names.stream().noneMatch(String::isEmpty);
        System.out.println("count of names starting with A: " + count);
        System.out.println("any name longer than 7: " + anyLong + ", none empty: " + allNonEmpty);
        System.out.println("first long name: " + names.stream().filter(n -> n.length() > 4).findFirst().orElse("none"));


        // ============================================
        // SECTION 4: A STREAM CAN ONLY BE USED ONCE
        // ============================================

        Stream<String> once = names.stream();
        System.out.println("first use works: " + once.count());
        try {
            once.count();                                          // second terminal operation on the same stream
        } catch (IllegalStateException e) {
            System.out.println("IllegalStateException: " + e.getMessage());
        }
        // Need it again? Create a NEW stream from the source: names.stream()


        // ============================================
        // SECTION 5: PRIMITIVE STREAMS - IntStream, LongStream, DoubleStream
        // Avoid boxing and add numeric terminals: sum(), average(), min(), max(), summaryStatistics().
        // ============================================

        int sumOfSquares = IntStream.rangeClosed(1, 5).map(n -> n * n).sum();
        System.out.println("sum of squares 1..5 = " + sumOfSquares);
        System.out.println("average of 1..5 = " + IntStream.rangeClosed(1, 5).average().orElse(0));
        System.out.println("statistics: " + IntStream.of(4, 8, 15, 16, 23, 42).summaryStatistics());


        // ============================================
        // SECTION 6: STREAM vs LOOP - AN HONEST NOTE
        // Streams shine for filter/transform/collect pipelines. A plain loop can
        // be clearer when you need several mutable variables, early 'break'/'continue'
        // with complicated conditions, or checked exceptions inside the body.
        // Choose the one a teammate can read fastest.
        // ============================================
    }
}
