// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.ArrayList;
import java.util.List;

public class _1_GenericClasses {

    // ============================================
    // SECTION 1: THE PROBLEM - A BOX THAT HOLDS "ANYTHING"
    // Before generics you wrote Object. It compiles, but you lose the type.
    // ============================================

    static class ObjectBox {
        private Object value;

        ObjectBox(Object value) {
            this.value = value;
        }

        Object get() {
            return value;
        }
    }

    // ============================================
    // SECTION 2: THE FIX - A TYPE PARAMETER
    // <T> is a placeholder filled in by whoever USES the class.
    // Box<String> means "a Box where T is String".
    // ============================================

    static class Box<T> {
        private T value;

        Box(T value) {
            this.value = value;
        }

        T get() {
            return value;
        }

        void set(T value) {
            this.value = value;
        }

        @Override
        public String toString() {
            return "Box[" + value + "]";
        }
    }

    // ============================================
    // SECTION 3: MORE THAN ONE TYPE PARAMETER
    // ============================================

    static class Pair<A, B> {
        private final A first;
        private final B second;

        Pair(A first, B second) {
            this.first = first;
            this.second = second;
        }

        A first() {
            return first;
        }

        B second() {
            return second;
        }

        // Returns a NEW pair with the types swapped: Pair<A,B> -> Pair<B,A>
        Pair<B, A> swap() {
            return new Pair<>(second, first);
        }

        @Override
        public String toString() {
            return "(" + first + ", " + second + ")";
        }
    }

    // ============================================
    // SECTION 4: A GENERIC CLASS THAT USES ITS OWN TYPE
    // A tiny typed holder of many items.
    // ============================================

    static class Bag<T> {
        private final List<T> items = new ArrayList<>();

        void add(T item) {
            items.add(item);
        }

        int size() {
            return items.size();
        }

        T first() {
            return items.get(0);
        }
    }

    public static void main(String[] args) {

        // --- The Object version: the compiler cannot protect you ---
        ObjectBox oldBox = new ObjectBox("hello");
        String s = (String) oldBox.get();                 // you must CAST
        System.out.println("ObjectBox, after a cast: " + s);

        ObjectBox wrong = new ObjectBox(42);              // compiles fine...
        try {
            String bad = (String) wrong.get();            // ...but fails only when this line RUNS
            System.out.println(bad);
        } catch (ClassCastException e) {
            System.out.println("ClassCastException at RUNTIME: the compiler could not warn us");
        }

        // --- The generic version: the compiler checks everything ---
        Box<String> name = new Box<>("Ada");              // <> is the "diamond": Java infers String
        String n = name.get();                            // no cast needed
        System.out.println("Box<String>: " + name + ", get() = " + n);
        // Box<String> broken = new Box<>(42);            // COMPILE ERROR: int cannot become String
        // name.set(99);                                  // COMPILE ERROR: caught before the program runs

        Box<Integer> number = new Box<>(10);
        number.set(number.get() + 5);                     // Integer unboxed and boxed automatically
        System.out.println("Box<Integer>: " + number);

        // --- Pair ---
        Pair<String, Integer> entry = new Pair<>("age", 30);
        System.out.println("Pair: " + entry + ", swapped: " + entry.swap());
        String key = entry.first();
        int value = entry.second();                       // unboxed from Integer
        System.out.println("key = " + key + ", value = " + value);

        // --- Bag ---
        Bag<Double> prices = new Bag<>();
        prices.add(9.99);
        prices.add(4.5);
        System.out.println("Bag<Double> size = " + prices.size() + ", first = " + prices.first());

        // ============================================
        // SECTION 5: RULES TO REMEMBER
        // 1) Type arguments must be OBJECT types: Box<Integer>, never Box<int>.
        //    (Primitives are wrapped automatically: int <-> Integer.)
        // 2) Convention for names: T = type, E = element, K = key, V = value, A/B = several types.
        // 3) The diamond <> lets the compiler infer the type on the right-hand side.
        // 4) You cannot do "new T()" or "new T[10]" inside a generic class (see _5_TypeErasure).
        // ============================================
    }
}
