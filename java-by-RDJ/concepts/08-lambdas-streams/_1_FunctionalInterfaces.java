// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.List;
import java.util.function.BiFunction;
import java.util.function.BinaryOperator;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.function.UnaryOperator;

public class _1_FunctionalInterfaces {

    // ============================================
    // SECTION 1: WHAT IS A FUNCTIONAL INTERFACE?
    // An interface with EXACTLY ONE abstract method. Because there is only one
    // thing to implement, Java lets you write that one method as a short lambda.
    // @FunctionalInterface asks the compiler to CHECK this for you.
    // ============================================

    @FunctionalInterface
    interface Greeter {
        String greet(String name);                                 // the single abstract method

        // default and static methods do not count against the "one abstract method" rule
        default String greetLoudly(String name) {
            return greet(name).toUpperCase() + "!";
        }
    }

    // @FunctionalInterface
    // interface Broken {                                          // COMPILE ERROR: two abstract methods
    //     void a();
    //     void b();
    // }

    public static void main(String[] args) {

        // ============================================
        // SECTION 2: YOUR OWN FUNCTIONAL INTERFACE
        // ============================================

        Greeter friendly = name -> "Hello, " + name;
        System.out.println(friendly.greet("Ada"));
        System.out.println(friendly.greetLoudly("Ada"));


        // ============================================
        // SECTION 3: THE BUILT-IN ONES (java.util.function)
        // You rarely write your own: these cover almost every shape.
        //
        //   Function<T,R>        T -> R            apply
        //   Predicate<T>         T -> boolean      test
        //   Consumer<T>          T -> nothing      accept
        //   Supplier<T>          nothing -> T      get
        //   BiFunction<T,U,R>    (T,U) -> R        apply
        //   UnaryOperator<T>     T -> T            apply   (a Function with the same in and out type)
        //   BinaryOperator<T>    (T,T) -> T        apply
        // ============================================

        // Function: transform
        Function<String, Integer> length = s -> s.length();
        System.out.println("Function length(\"streams\") = " + length.apply("streams"));

        // Predicate: yes/no question
        Predicate<Integer> isEven = n -> n % 2 == 0;
        System.out.println("Predicate isEven(10) = " + isEven.test(10) + ", isEven(7) = " + isEven.test(7));

        // Consumer: do something, return nothing
        Consumer<String> shout = s -> System.out.println("Consumer says: " + s.toUpperCase());
        shout.accept("hello");

        // Supplier: produce a value on demand (it can be different each call)
        Supplier<String> greeting = () -> "made on demand";
        System.out.println("Supplier gives: " + greeting.get());

        // BiFunction: two inputs
        BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
        System.out.println("BiFunction add(3, 4) = " + add.apply(3, 4));

        // UnaryOperator and BinaryOperator: the "same type" shortcuts
        UnaryOperator<String> trim = String::trim;
        BinaryOperator<Integer> max = Math::max;
        System.out.println("UnaryOperator trim = [" + trim.apply("  padded  ") + "], BinaryOperator max = " + max.apply(8, 5));


        // ============================================
        // SECTION 4: PRIMITIVE VERSIONS
        // Function<Integer,Integer> boxes every int into an Integer object.
        // IntPredicate, IntFunction, ToIntFunction, IntUnaryOperator... avoid that.
        // ============================================

        java.util.function.IntPredicate positive = n -> n > 0;
        java.util.function.ToIntFunction<String> len = String::length;
        System.out.println("IntPredicate positive(5) = " + positive.test(5) + ", ToIntFunction len(\"four\") = " + len.applyAsInt("four"));


        // ============================================
        // SECTION 5: COMBINING FUNCTIONS
        // The built-in interfaces carry default methods that build bigger ones.
        // ============================================

        Predicate<String> notEmpty = s -> !s.isEmpty();
        Predicate<String> shortWord = s -> s.length() < 5;
        Predicate<String> both = notEmpty.and(shortWord);
        Predicate<String> either = shortWord.or(s -> s.startsWith("z"));
        Predicate<String> opposite = shortWord.negate();
        System.out.println("and:    \"tree\" -> " + both.test("tree") + ", \"\" -> " + both.test(""));
        System.out.println("or:     \"zebra\" -> " + either.test("zebra"));
        System.out.println("negate: \"elephant\" -> " + opposite.test("elephant"));

        Function<Integer, Integer> plusOne = n -> n + 1;
        Function<Integer, Integer> doubled = n -> n * 2;
        // andThen: first this, then that.   compose: first that, then this.
        System.out.println("plusOne.andThen(doubled)(5) = " + plusOne.andThen(doubled).apply(5) + "   (5+1)*2");
        System.out.println("plusOne.compose(doubled)(5) = " + plusOne.compose(doubled).apply(5) + "   (5*2)+1");

        Function<String, String> identity = Function.identity();
        System.out.println("Function.identity() returns its input: " + identity.apply("same"));


        // ============================================
        // SECTION 6: FUNCTIONS ARE VALUES
        // You can pass them to methods, store them in variables and put them in collections.
        // That is the whole idea behind streams (the next files).
        // ============================================

        List<Function<Integer, Integer>> pipeline = List.of(n -> n + 1, n -> n * 10, n -> n - 3);
        int value = 4;
        for (Function<Integer, Integer> step : pipeline) {
            value = step.apply(value);
        }
        System.out.println("pipeline (+1, *10, -3) applied to 4 = " + value);
        System.out.println("apply the same function twice: " + applyTwice(n -> n * n, 3));
    }

    static int applyTwice(Function<Integer, Integer> f, int input) {
        return f.apply(f.apply(input));
    }
}
