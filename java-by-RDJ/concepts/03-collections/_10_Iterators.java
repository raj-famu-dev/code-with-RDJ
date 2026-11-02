// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.*;

public class _10_Iterators {

    // Any class that implements Iterable can be used in a for-each loop
    static class Countdown implements Iterable<Integer> {
        private final int start;

        Countdown(int start) {
            this.start = start;
        }

        @Override
        public Iterator<Integer> iterator() {
            return new Iterator<>() {
                int next = start;

                @Override
                public boolean hasNext() {
                    return next > 0;
                }

                @Override
                public Integer next() {
                    if (next <= 0) throw new NoSuchElementException();
                    return next--;
                }
            };
        }
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT AN ITERATOR IS
        // A cursor that walks a collection one element at a time.
        // hasNext() = is there another one?   next() = give it to me and advance.
        // The for-each loop is just shorthand for this.
        // ============================================

        List<String> list = new ArrayList<>(List.of("a", "b", "c", "d"));
        Iterator<String> it = list.iterator();
        while (it.hasNext()) {
            System.out.println("visit " + it.next());
        }


        // ============================================
        // SECTION 2: REMOVING SAFELY WITH it.remove()
        // The iterator removes the element it just returned and keeps its own
        // position correct.
        // ============================================

        it = list.iterator();
        while (it.hasNext()) {
            if (it.next().equals("b")) {
                it.remove();
            }
        }
        System.out.println("After it.remove(): " + list);


        // ============================================
        // SECTION 3: FAIL-FAST - THE ConcurrentModificationException
        // ArrayList counts structural changes (modCount). The iterator checks
        // that count on every next(). If the list changed behind its back, it
        // throws instead of continuing with unreliable data.
        // ============================================

        List<String> crash = new ArrayList<>(List.of("a", "b", "c", "d"));
        try {
            for (String s : crash) {
                if (s.equals("a")) {
                    crash.remove(s);
                }
            }
        } catch (ConcurrentModificationException e) {
            System.out.println("Caught ConcurrentModificationException");
        }


        // ============================================
        // SECTION 4: TRAP - THE CASE THAT DOES NOT THROW (AND IS WORSE)
        // Remove the SECOND-TO-LAST element and hasNext() returns false before
        // the check ever runs. No exception, but the last element is skipped.
        // Fail-fast is "best effort", never a guarantee, so never rely on it.
        // ============================================

        List<String> quirk = new ArrayList<>(List.of("a", "b", "c"));
        List<String> visited = new ArrayList<>();
        for (String s : quirk) {
            visited.add(s);
            if (s.equals("b")) {
                quirk.remove(s);
            }
        }
        System.out.println("Visited " + visited + " - \"c\" was silently skipped");


        // ============================================
        // SECTION 5: THREE SAFE WAYS TO REMOVE WHILE LOOPING
        // ============================================

        List<Integer> nums = new ArrayList<>(List.of(1, 2, 3, 4, 5, 6));
        nums.removeIf(n -> n % 2 == 0);                  // 1) removeIf: shortest and clearest
        System.out.println("removeIf even: " + nums);

        List<Integer> copy = new ArrayList<>(nums);      // 2) loop over a COPY, change the original
        for (Integer n : copy) {
            if (n == 3) nums.remove(n);
        }
        System.out.println("loop over a copy: " + nums);
        // 3) the explicit Iterator + it.remove() from Section 2


        // ============================================
        // SECTION 6: ListIterator - GOES BOTH WAYS AND CAN EDIT
        // ============================================

        List<String> letters = new ArrayList<>(List.of("x", "y", "z"));
        ListIterator<String> li = letters.listIterator();
        while (li.hasNext()) {
            String s = li.next();
            if (s.equals("y")) {
                li.set("Y");              // replace the element just returned
                li.add("y2");             // insert right after it
            }
        }
        System.out.print("Backwards:");
        while (li.hasPrevious()) {
            System.out.print(" " + li.previous());
        }
        System.out.println();


        // ============================================
        // SECTION 7: MAKING YOUR OWN CLASS WORK IN for-each
        // ============================================

        System.out.print("Countdown:");
        for (int n : new Countdown(3)) {
            System.out.print(" " + n);
        }
        System.out.println();
    }
}
