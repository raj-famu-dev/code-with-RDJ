// Tags: #Java #Lambdas #Streams #MapFilterReduce | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

public class _4_MapFilterReduce {

    public static void main(String[] args) {

        List<Integer> numbers = List.of(5, 3, 8, 3, 1, 9, 8, 2);
        List<String> words = List.of("stream", "lambda", "filter", "map", "reduce");

        // ============================================
        // SECTION 1: filter - KEEP WHAT MATCHES (Predicate)
        // ============================================

        System.out.println("filter even:        " + numbers.stream().filter(n -> n % 2 == 0).toList());


        // ============================================
        // SECTION 2: map - TRANSFORM EACH ELEMENT (Function), one in, one out
        // ============================================

        System.out.println("map square:         " + numbers.stream().map(n -> n * n).toList());
        System.out.println("map to lengths:     " + words.stream().map(String::length).toList());


        // ============================================
        // SECTION 3: flatMap - ONE IN, MANY OUT, THEN FLATTEN
        // map would give a Stream of Streams / List of Lists. flatMap merges them into one stream.
        // ============================================

        List<List<Integer>> nested = List.of(List.of(1, 2), List.of(3), List.of(4, 5, 6));
        System.out.println("map gives lists:    " + nested.stream().map(l -> l).toList());
        System.out.println("flatMap flattens:   " + nested.stream().flatMap(List::stream).toList());

        List<String> sentences = List.of("to be or", "not to be");
        System.out.println("all words:          " + sentences.stream().flatMap(s -> Stream.of(s.split(" "))).toList());


        // ============================================
        // SECTION 4: sorted, distinct, limit, skip
        // ============================================

        System.out.println("sorted:             " + numbers.stream().sorted().toList());
        System.out.println("sorted descending:  " + numbers.stream().sorted(Comparator.reverseOrder()).toList());
        System.out.println("distinct:           " + numbers.stream().distinct().toList());
        System.out.println("limit 3:            " + numbers.stream().limit(3).toList());
        System.out.println("skip 5:             " + numbers.stream().skip(5).toList());
        System.out.println("sorted by length then alphabetically: "
                + words.stream().sorted(Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder())).toList());


        // ============================================
        // SECTION 5: reduce - COMBINE ALL ELEMENTS INTO ONE VALUE
        // reduce(identity, accumulator): start from 'identity', fold each element in.
        // The identity must be the "do nothing" value for the operation: 0 for +, 1 for *.
        // ============================================

        int sum = numbers.stream().reduce(0, (acc, n) -> acc + n);
        int sumShort = numbers.stream().reduce(0, Integer::sum);
        int product = Stream.of(1, 2, 3, 4).reduce(1, (a, b) -> a * b);
        System.out.println("reduce sum:         " + sum + " (same as Integer::sum: " + (sum == sumShort) + ")");
        System.out.println("reduce product 1..4: " + product);

        // Without an identity the stream might be EMPTY, so the result is an Optional
        Optional<Integer> biggest = numbers.stream().reduce(Integer::max);
        Optional<Integer> ofNothing = Stream.<Integer>empty().reduce(Integer::sum);
        System.out.println("reduce max:         " + biggest.get() + ", on an empty stream: " + ofNothing);

        // Longest word with reduce
        String longest = words.stream().reduce("", (a, b) -> b.length() > a.length() ? b : a);
        System.out.println("longest word:       " + longest);


        // ============================================
        // SECTION 6: THE EASIER WAY FOR NUMBERS - PRIMITIVE STREAMS
        // sum, min, max, average built in (no reduce needed)
        // ============================================

        System.out.println("mapToInt sum:       " + numbers.stream().mapToInt(Integer::intValue).sum());
        System.out.println("max via comparator: " + numbers.stream().max(Comparator.naturalOrder()).get());


        // ============================================
        // SECTION 7: A COMPLETE PIPELINE
        // "the three largest distinct even squares, as text"
        // ============================================

        String text = IntStream.rangeClosed(1, 10)
                .map(n -> n * n)
                .filter(n -> n % 2 == 0)
                .boxed()
                .sorted(Comparator.reverseOrder())
                .limit(3)
                .map(String::valueOf)
                .collect(Collectors.joining(", ", "[", "]"));
        System.out.println("three largest even squares up to 10^2: " + text);


        // ============================================
        // SECTION 8: ORDER MATTERS
        // filter early to do less work in later steps.
        // ============================================
        // Both give the same answer, but the first maps only the survivors:
        //   words.stream().filter(w -> w.length() > 3).map(String::toUpperCase)
        //   words.stream().map(String::toUpperCase).filter(w -> w.length() > 3)
    }
}
