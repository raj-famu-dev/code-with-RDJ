// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.List;

public class _4_Wildcards {

    // A small type family used throughout: Animal <- Dog, Cat
    static class Animal {
        String name() {
            return "animal";
        }
    }

    static class Dog extends Animal {
        @Override
        String name() {
            return "dog";
        }
    }

    static class Cat extends Animal {
        @Override
        String name() {
            return "cat";
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE SURPRISE - List<Dog> IS NOT A List<Animal>
        // A Dog is an Animal, but a LIST of dogs is not a LIST of animals.
        // If it were, this would be legal and would break type safety:
        //     List<Dog> dogs = new ArrayList<>();
        //     List<Animal> animals = dogs;    // COMPILE ERROR (and good that it is)
        //     animals.add(new Cat());         // a Cat would end up in a list of Dogs!
        // Same reason: List<Object> is NOT a supertype of List<String>.
        // Arrays DO allow this (Dog[] is an Animal[]), and it fails at RUNTIME instead:
        // ============================================

        Animal[] animalArray = new Dog[1];                // legal for arrays
        try {
            animalArray[0] = new Cat();                   // compiles, then...
        } catch (ArrayStoreException e) {
            System.out.println("Arrays: ArrayStoreException at runtime. Generics stop this at compile time.");
        }

        // ============================================
        // SECTION 2: WILDCARD ? = "A LIST OF SOMETHING, I DON'T CARE WHAT"
        // Good for code that only needs the list itself (size, printing).
        // ============================================

        List<Dog> dogs = new ArrayList<>(List.of(new Dog(), new Dog()));
        List<Cat> cats = new ArrayList<>(List.of(new Cat()));
        System.out.println("count of dogs: " + count(dogs));
        System.out.println("count of cats: " + count(cats));

        // ============================================
        // SECTION 3: ? extends T  (PRODUCER - you can READ from it)
        // "a list of T or any subtype of T". Everything in it IS-A T, so reading is safe.
        // But you cannot ADD: the compiler doesn't know which exact subtype the list holds.
        // ============================================

        System.out.println("names from List<Dog>:");
        printNames(dogs);                                 // List<Dog> accepted by List<? extends Animal>
        System.out.println("names from List<Cat>:");
        printNames(cats);

        List<? extends Animal> readOnlyView = dogs;
        Animal a = readOnlyView.get(0);                   // reading works
        System.out.println("read from ? extends: " + a.name());
        // readOnlyView.add(new Dog());                   // COMPILE ERROR: could be a List<Cat> underneath
        // readOnlyView.add(new Animal());                // COMPILE ERROR for the same reason
        readOnlyView.add(null);                           // only null is allowed
        readOnlyView.remove(null);                        // clean up the null again

        // ============================================
        // SECTION 4: ? super T  (CONSUMER - you can WRITE into it)
        // "a list of T or any SUPERtype of T". Adding a Dog is always safe, because
        // whatever the real list type is (Dog, Animal, Object), a Dog fits.
        // But reading gives you only Object, as you don't know the exact type.
        // ============================================

        List<Animal> animals = new ArrayList<>();
        List<Object> objects = new ArrayList<>();
        addDogs(animals);                                 // List<Animal> accepted by List<? super Dog>
        addDogs(objects);                                 // List<Object> accepted too
        System.out.println("animals after addDogs: " + animals.size() + ", objects after addDogs: " + objects.size());

        List<? super Dog> sink = animals;
        sink.add(new Dog());                              // writing works
        Object o = sink.get(0);                           // reading only gives Object
        System.out.println("read from ? super gives only Object: " + o.getClass().getSimpleName());
        // Dog d = sink.get(0);                           // COMPILE ERROR: could be a List<Object>

        // ============================================
        // SECTION 5: PECS = "Producer Extends, Consumer Super"
        // If the collection PRODUCES values you read   -> ? extends T
        // If the collection CONSUMES values you write  -> ? super T
        // Both at once? Then use an exact type (no wildcard).
        // Classic example: copy(source, destination) - the source produces, the destination consumes.
        // ============================================

        List<Animal> destination = new ArrayList<>();
        copy(dogs, destination);                          // dogs PRODUCE, destination CONSUMES
        System.out.println("copied dogs into List<Animal>: " + destination.size() + " items");

        // ============================================
        // SECTION 6: SUMMARY TABLE
        //   List<?>             read: Object          write: nothing (only null)
        //   List<? extends T>   read: T               write: nothing (only null)
        //   List<? super T>     read: Object          write: T (and its subtypes)
        //   List<T>             read: T               write: T
        // ============================================
    }

    // Wildcard with no bound: only uses size()
    static int count(List<?> list) {
        return list.size();
    }

    // PRODUCER: reads Animals out of the list
    static void printNames(List<? extends Animal> animals) {
        for (Animal animal : animals) {
            System.out.println("  " + animal.name());
        }
    }

    // CONSUMER: writes Dogs into the list
    static void addDogs(List<? super Dog> target) {
        target.add(new Dog());
        target.add(new Dog());
    }

    // PECS in one method
    static <T> void copy(List<? extends T> source, List<? super T> destination) {
        for (T item : source) {
            destination.add(item);
        }
    }
}
