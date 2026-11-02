// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.function.Function;
import java.util.function.Supplier;

public class _2_LambdasAndMethodReferences {

    static class Person {
        private final String name;
        private final int age;

        Person(String name, int age) {
            this.name = name;
            this.age = age;
        }

        String getName() {
            return name;
        }

        int getAge() {
            return age;
        }

        static int compareByAge(Person a, Person b) {
            return Integer.compare(a.age, b.age);
        }

        @Override
        public String toString() {
            return name + "(" + age + ")";
        }
    }

    private int counter = 0;                                       // used in the "capture" demo (Section 5)

    public static void main(String[] args) {

        List<Person> people = new ArrayList<>(List.of(
                new Person("Linus", 55), new Person("Ada", 36), new Person("Grace", 85)));

        // ============================================
        // SECTION 1: THE SAME BEHAVIOUR IN THREE STYLES
        // Goal: sort people by age.
        // ============================================

        // Style 1 - anonymous class (the pre-Java-8 way): lots of ceremony
        List<Person> a = new ArrayList<>(people);
        a.sort(new Comparator<Person>() {
            @Override
            public int compare(Person p1, Person p2) {
                return Integer.compare(p1.getAge(), p2.getAge());
            }
        });
        System.out.println("anonymous class: " + a);

        // Style 2 - lambda: only parameters and the body remain
        List<Person> b = new ArrayList<>(people);
        b.sort((p1, p2) -> Integer.compare(p1.getAge(), p2.getAge()));
        System.out.println("lambda:          " + b);

        // Style 3 - method reference: just the NAME of an existing method
        List<Person> c = new ArrayList<>(people);
        c.sort(Person::compareByAge);
        System.out.println("method reference: " + c);

        // Style 4 - Comparator.comparing, the idiomatic form
        List<Person> d = new ArrayList<>(people);
        d.sort(Comparator.comparingInt(Person::getAge));
        System.out.println("comparingInt:    " + d);


        // ============================================
        // SECTION 2: LAMBDA SYNTAX
        //   (parameters) -> expression
        //   (parameters) -> { statements; return value; }
        // ============================================

        Function<Integer, Integer> square1 = (Integer n) -> n * n;     // full form with a type
        Function<Integer, Integer> square2 = (n) -> n * n;             // type inferred
        Function<Integer, Integer> square3 = n -> n * n;               // one parameter: parentheses optional
        Function<Integer, Integer> square4 = n -> {                    // block body: needs 'return'
            int result = n * n;
            return result;
        };
        System.out.println("four spellings of 'square' agree: "
                + (square1.apply(6) == 36 && square2.apply(6) == 36 && square3.apply(6) == 36 && square4.apply(6) == 36));

        Supplier<String> noParams = () -> "no parameters needs empty parentheses";
        System.out.println(noParams.get());


        // ============================================
        // SECTION 3: THE FOUR KINDS OF METHOD REFERENCE
        // 1) static method             ClassName::staticMethod       Person::compareByAge
        // 2) method on a given object  object::method                System.out::println
        // 3) method on the parameter   ClassName::instanceMethod     Person::getName   (s -> s.getName())
        // 4) constructor               ClassName::new                ArrayList::new
        // ============================================

        Function<String, Integer> parse = Integer::parseInt;           // 1) static
        System.out.println("static reference: " + (parse.apply("41") + 1));

        String prefix = "Hello, ";
        Function<String, String> concat = prefix::concat;              // 2) on a particular object
        System.out.println("bound reference: " + concat.apply("world"));

        Function<Person, String> nameOf = Person::getName;             // 3) on the parameter
        System.out.println("unbound reference: " + nameOf.apply(people.get(0)));

        Supplier<List<String>> newList = ArrayList::new;               // 4) constructor
        List<String> fresh = newList.get();
        fresh.add("created via ArrayList::new");
        System.out.println(fresh);

        people.forEach(System.out::println);                           // the most common one


        // ============================================
        // SECTION 4: A LAMBDA IS NOT AN ANONYMOUS CLASS
        // 'this' inside an anonymous class is the anonymous object.
        // 'this' inside a lambda is the SURROUNDING object (the lambda has no identity of its own).
        // ============================================

        new _2_LambdasAndMethodReferences().demonstrateThis();


        // ============================================
        // SECTION 5: CAPTURING VARIABLES - "EFFECTIVELY FINAL"
        // A lambda can use local variables of the surrounding method, but only if they
        // never change after being set. The lambda copies the VALUE.
        // ============================================

        int base = 100;                                                // effectively final: never reassigned
        Function<Integer, Integer> addBase = n -> n + base;
        System.out.println("captured local: " + addBase.apply(5));

        // int total = 0;
        // people.forEach(p -> total += p.getAge());                   // COMPILE ERROR: total is modified
        // Fix: do not mutate outside state; use a stream (_4) or sum with a normal loop.
        int[] box = {0};                                               // a one-element array "works" but is a code smell
        people.forEach(p -> box[0] += p.getAge());
        System.out.println("sum via array hack (avoid this): " + box[0]);

        // Fields CAN be changed from a lambda (they live on an object, not on the stack):
        _2_LambdasAndMethodReferences holder = new _2_LambdasAndMethodReferences();
        people.forEach(p -> holder.counter++);
        System.out.println("field changed from a lambda: " + holder.counter + "  (works, but shared mutable state is risky with streams)");
    }

    void demonstrateThis() {
        Runnable lambda = () -> System.out.println("lambda 'this' is the outer object, class = " + this.getClass().getSimpleName());
        Runnable anonymous = new Runnable() {
            @Override
            public void run() {
                System.out.println("anonymous 'this' is the anonymous object, class name empty: "
                        + this.getClass().getSimpleName().isEmpty());
            }
        };
        lambda.run();
        anonymous.run();
    }
}
