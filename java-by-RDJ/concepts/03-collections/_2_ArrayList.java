// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.*;

public class _2_ArrayList {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT ArrayList REALLY IS
        // A resizable wrapper around a plain Object[] array.
        // Elements sit side by side in memory, so jumping to index i is one
        // calculation - that is why get(i) is O(1).
        // size() = how many elements you stored; capacity = length of the
        // hidden array. They are different numbers.
        // ============================================

        List<String> list = new ArrayList<>();
        list.add("a");
        list.add("b");
        list.add("c");
        System.out.println("get(1) = " + list.get(1) + "  (O(1): direct array access)");


        // ============================================
        // SECTION 2: HOW IT GROWS
        // When the hidden array is full, ArrayList allocates a NEW bigger array
        // and copies everything over. In the OpenJDK implementation the new
        // capacity is about 1.5x the old one (and the default starting
        // capacity is 10). Those exact numbers are an implementation detail,
        // not a promise in the specification.
        // Result: add at the END is O(1) AMORTIZED - usually cheap, occasionally
        // O(n) when a resize happens, but averaged out it is constant.
        // ============================================

        List<Integer> big = new ArrayList<>(1000);   // pre-size when you know the count: avoids repeated resizing
        for (int i = 0; i < 1000; i++) {
            big.add(i);
        }
        System.out.println("big.size() = " + big.size());


        // ============================================
        // SECTION 3: ADD / REMOVE IN THE MIDDLE OR FRONT = O(n)
        // add(0, x) must shift EVERY existing element one slot right.
        // remove(i) must shift every element after i one slot left.
        // ============================================

        list.add(0, "front");          // O(n): shifts a, b, c
        System.out.println("After add(0, \"front\"): " + list);
        String removed = list.remove(1);   // O(n): shifts the elements after index 1
        System.out.println("remove(1) returned \"" + removed + "\", list is now " + list);
        list.set(0, "FRONT");          // set(i, x) replaces in place: O(1)
        System.out.println("After set(0, ...): " + list);


        // ============================================
        // SECTION 4: TRAP - remove(int) vs remove(Object)
        // On a List<Integer>, remove(1) means "remove the element AT INDEX 1".
        // To remove the VALUE 1 you must pass an Integer object.
        // ============================================

        List<Integer> nums = new ArrayList<>(List.of(10, 1, 20, 1));
        nums.remove(1);                       // index 1 -> removes the value 1 that sits at index 1
        System.out.println("remove(1) by index:           " + nums);
        nums.remove(Integer.valueOf(1));      // value 1 -> removes the first element equal to 1
        System.out.println("remove(Integer.valueOf(1)):   " + nums);
        // nums.remove(99);  // would throw IndexOutOfBoundsException: it is treated as an INDEX, and there is no index 99


        // ============================================
        // SECTION 5: TRAP - MODIFYING A LIST WHILE LOOPING OVER IT
        // The for-each loop uses an Iterator behind the scenes. If the list is
        // changed behind its back, the next step throws
        // ConcurrentModificationException (the list tracks a "modCount").
        // ============================================

        List<String> words = new ArrayList<>(List.of("x", "y", "z"));
        try {
            for (String w : words) {
                if (w.equals("x")) {
                    words.remove(w);          // structural change inside the loop
                }
            }
        } catch (ConcurrentModificationException e) {
            System.out.println("Caught ConcurrentModificationException");
        }
        // The safe fix:
        words.removeIf(w -> w.equals("y"));
        System.out.println("After removeIf: " + words);


        // ============================================
        // SECTION 6: OTHER USEFUL OPERATIONS
        // contains() and indexOf() scan the list: O(n).
        // Using the wrong index fails loudly.
        // ============================================

        List<String> fruit = new ArrayList<>(List.of("apple", "pear", "plum"));
        System.out.println("indexOf(pear) = " + fruit.indexOf("pear") + ", contains(kiwi) = " + fruit.contains("kiwi"));
        try {
            fruit.get(3);                      // valid indexes are 0..size()-1
        } catch (IndexOutOfBoundsException e) {
            System.out.println("Caught IndexOutOfBoundsException: " + e.getMessage());
        }


        // ============================================
        // SECTION 7: COMPLEXITY SUMMARY
        // get(i), set(i, x)          O(1)
        // add(x) at end              O(1) amortized
        // add(0, x) / add(i, x)      O(n)
        // remove(i) / remove(Object) O(n)
        // contains / indexOf         O(n)
        // ============================================
    }
}
