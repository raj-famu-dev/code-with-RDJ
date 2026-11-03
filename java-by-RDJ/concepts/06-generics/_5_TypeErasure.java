// Tags: #Java #Generics #TypeErasure | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.List;

public class _5_TypeErasure {

    // ============================================
    // SECTION 1: WHAT "ERASURE" MEANS
    // Generics exist only for the COMPILER. After checking your types, the
    // compiler REMOVES them: List<String> becomes plain List in the .class file,
    // and a cast is inserted where you read. This keeps old pre-generics code compatible.
    // ============================================

    static class Box<T> {
        T value;

        Box(T value) {
            this.value = value;
        }
    }

    // ============================================
    // SECTION 2: THINGS YOU CANNOT DO BECAUSE T IS GONE AT RUNTIME
    // ============================================

    static class Broken<T> {
        // T item = new T();                              // COMPILE ERROR: which constructor? T does not exist at runtime
        // T[] array = new T[10];                         // COMPILE ERROR: generic array creation
        // boolean test(Object o) { return o instanceof T; }   // COMPILE ERROR: cannot check against T
        // static T shared;                               // COMPILE ERROR: static cannot use the class's T
        // class MyException<T> extends Exception { }     // COMPILE ERROR: generic exceptions are not allowed
    }

    // ============================================
    // SECTION 3: THE STANDARD WORKAROUND FOR A GENERIC ARRAY
    // Create an Object[] and cast it. Keep the array PRIVATE so a wrong type
    // can never leak out. The cast is unchecked, so we suppress the warning
    // deliberately and explain why it is safe.
    // ============================================

    static class SimpleList<T> {
        private T[] data;
        private int size;

        @SuppressWarnings("unchecked")                    // safe: 'data' never leaves this class as a T[]
        SimpleList() {
            data = (T[]) new Object[4];
        }

        void add(T item) {
            if (size == data.length) {
                data = java.util.Arrays.copyOf(data, size * 2);
            }
            data[size++] = item;
        }

        T get(int index) {
            return data[index];
        }

        int size() {
            return size;
        }
    }

    // ============================================
    // SECTION 4: A WORKAROUND FOR "new T()" - PASS A Class<T> OR A SUPPLIER
    // ============================================

    static <T> T create(java.util.function.Supplier<T> factory) {
        return factory.get();
    }

    // ============================================
    // SECTION 5: ERASURE MAKES OVERLOADS COLLIDE
    // void process(List<String> l) and void process(List<Integer> l) have the SAME
    // erasure (process(List)), so you cannot have both in one class:
    //     static void process(List<String> l) { }
    //     static void process(List<Integer> l) { }   // COMPILE ERROR: name clash, same erasure
    // ============================================

    public static void main(String[] args) {

        // --- At runtime the type arguments are gone ---
        List<String> strings = new ArrayList<>();
        List<Integer> integers = new ArrayList<>();
        System.out.println("List<String>.getClass()  = " + strings.getClass().getName());
        System.out.println("List<Integer>.getClass() = " + integers.getClass().getName());
        System.out.println("Same runtime class? " + (strings.getClass() == integers.getClass()));
        // if (strings instanceof List<String>) { }       // COMPILE ERROR: cannot check a parameterized type at runtime
        System.out.println("instanceof List<?> is allowed: " + (strings instanceof List<?>));

        // --- Heap pollution: breaking type safety through a raw type ---
        // Mixing raw types with generics lets a wrong type in; the failure then appears LATER,
        // at a place that looks innocent. This is what erasure makes possible.
        List<String> names = new ArrayList<>();
        @SuppressWarnings({"rawtypes", "unchecked"})
        List raw = names;                                 // a raw List (no type argument)
        raw.add(42);                                      // compiles with a warning; an Integer is now inside List<String>
        System.out.println("list claims to be List<String> yet holds: " + raw.get(0).getClass().getSimpleName());
        try {
            String s = names.get(0);                      // the compiler-inserted cast to String fails HERE
            System.out.println(s);
        } catch (ClassCastException e) {
            System.out.println("ClassCastException far away from the real mistake (the raw add)");
        }

        // --- The generic array workaround in use ---
        SimpleList<String> list = new SimpleList<>();
        for (String s : List.of("a", "b", "c", "d", "e", "f")) {      // 6 > initial capacity 4: forces a resize
            list.add(s);
        }
        System.out.println("SimpleList size = " + list.size() + ", get(5) = " + list.get(5));

        // --- Supplier instead of new T() ---
        StringBuilder sb = create(StringBuilder::new);
        sb.append("built by a supplier");
        System.out.println(sb);

        // --- Arrays vs generics ---
        // List<String>[] lists = new List<String>[3];     // COMPILE ERROR: generic array creation
        List<?>[] ok = new List<?>[3];                    // allowed: an array of unbounded wildcards
        System.out.println("array of List<?> created, length " + ok.length);

        // ============================================
        // SECTION 6: RULES TO REMEMBER
        // 1) Generics are checked at COMPILE time and erased before runtime.
        // 2) No new T(), new T[], instanceof T, or static fields of type T.
        // 3) Never use raw types (List instead of List<String>) in new code.
        // 4) Arrays are "reified" (they know their type at runtime); generics are not:
        //    that is why the two do not mix well.
        // ============================================
    }
}
