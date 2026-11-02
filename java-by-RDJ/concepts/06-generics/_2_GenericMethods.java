// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Function;

public class _2_GenericMethods {

    // ============================================
    // SECTION 1: A GENERIC METHOD HAS ITS OWN <T>
    // The <T> goes BEFORE the return type. The method works for any type,
    // even inside a class that is not generic at all.
    // ============================================

    static <T> void printAll(List<T> items) {
        for (T item : items) {
            System.out.println("  item: " + item);
        }
    }

    static <T> T firstOf(List<T> items) {
        return items.get(0);
    }

    // ============================================
    // SECTION 2: SWAPPING TWO ELEMENTS OF ANY ARRAY
    // ============================================

    static <T> void swap(T[] array, int i, int j) {
        T temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }

    // ============================================
    // SECTION 3: TWO TYPE PARAMETERS - A GENERIC "map"
    // Turns a List<A> into a List<B> using a conversion function.
    // ============================================

    static <A, B> List<B> mapAll(List<A> input, Function<A, B> converter) {
        List<B> result = new ArrayList<>();
        for (A a : input) {
            result.add(converter.apply(a));
        }
        return result;
    }

    // ============================================
    // SECTION 4: VARARGS + GENERICS
    // Collects any number of values into a List<T>.
    // (Java has List.of for this; writing it shows how generics and varargs combine.)
    // ============================================

    @SafeVarargs
    static <T> List<T> listOf(T... values) {
        List<T> result = new ArrayList<>();
        for (T value : values) {
            result.add(value);
        }
        return result;
    }

    // ============================================
    // SECTION 5: GENERIC CONSTRUCTOR-LIKE FACTORY ("static factory")
    // A generic static method on a generic class: the class's T is NOT available
    // in a static context, so a static method needs its OWN type parameter.
    // ============================================

    static class Holder<T> {
        private final T value;

        private Holder(T value) {
            this.value = value;
        }

        static <U> Holder<U> of(U value) {              // U, not T: static methods cannot use the class's T
            return new Holder<>(value);
        }

        T get() {
            return value;
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 6: TYPE INFERENCE
        // Normally you do NOT write the type: the compiler works it out from the arguments.
        // ============================================

        List<String> names = List.of("Ada", "Linus", "Grace");
        System.out.println("printAll with strings:");
        printAll(names);                                  // T is inferred as String

        List<Integer> numbers = List.of(3, 1, 2);
        System.out.println("printAll with integers:");
        printAll(numbers);                                // T is inferred as Integer

        String first = firstOf(names);                    // no cast: the return type is T = String
        int firstNumber = firstOf(numbers);
        System.out.println("firstOf: " + first + ", " + firstNumber);

        // You CAN state the type explicitly, rarely needed:
        List<String> explicit = _2_GenericMethods.<String>listOf("x", "y");
        System.out.println("explicit type argument: " + explicit);

        // --- swap on two different array types ---
        String[] words = {"one", "two", "three"};
        swap(words, 0, 2);
        System.out.println("swapped words: " + Arrays.toString(words));

        Integer[] digits = {1, 2, 3};
        swap(digits, 0, 1);
        System.out.println("swapped digits: " + Arrays.toString(digits));

        // int[] primitives = {1, 2};
        // swap(primitives, 0, 1);                        // COMPILE ERROR: T cannot be a primitive; use Integer[]

        // --- mapAll: String -> Integer (two type parameters) ---
        List<Integer> lengths = mapAll(names, String::length);
        System.out.println("lengths of names: " + lengths);

        List<String> labels = mapAll(numbers, n -> "#" + n);
        System.out.println("numbers as labels: " + labels);

        // --- varargs ---
        List<Double> doubles = listOf(1.5, 2.5, 3.5);
        System.out.println("listOf doubles: " + doubles);

        // --- static factory ---
        Holder<String> holder = Holder.of("kept");
        System.out.println("Holder.of: " + holder.get());

        // ============================================
        // SECTION 7: RULES TO REMEMBER
        // 1) <T> comes before the return type: static <T> T first(List<T> l)
        // 2) A static method cannot use the class's own T: give it its own letter.
        // 3) Inference usually works from the arguments; the return type can help too.
        // 4) Type arguments are always objects: use Integer[] not int[].
        // ============================================
    }
}
