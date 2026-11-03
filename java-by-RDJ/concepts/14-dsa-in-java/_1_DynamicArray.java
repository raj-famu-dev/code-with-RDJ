// Tags: #Java #DSA #DataStructures #DynamicArray | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * DYNAMIC ARRAY (what ArrayList is inside). Built on a plain Object[]; NO java.util collections inside the structure.
 * java.util.ArrayList appears ONLY in main(), as a trusted "oracle" to check our answers against.
 *
 * Big-O (n = current size):
 *   get(i), set(i, x)        O(1)
 *   add(x) at the end        O(1) AMORTIZED (O(n) on the rare resize)
 *   insert(i, x), remove(i)  O(n)   (shifts elements)
 *   contains / indexOf       O(n)
 *   memory                   O(capacity), up to about 2x the size
 */
public class _1_DynamicArray {

    static class DynamicArray<T> {
        private static final int INITIAL_CAPACITY = 4;

        private Object[] data = new Object[INITIAL_CAPACITY];
        private int size;
        long copies;                                               // total elements copied by resizes (for the amortized demo)
        int resizes;

        int size() {
            return size;
        }

        int capacity() {
            return data.length;
        }

        boolean isEmpty() {
            return size == 0;
        }

        @SuppressWarnings("unchecked")
        T get(int index) {
            checkIndex(index);
            return (T) data[index];
        }

        void set(int index, T value) {
            checkIndex(index);
            data[index] = value;
        }

        void add(T value) {
            ensureCapacity();
            data[size++] = value;
        }

        // insert at index (0..size): shift everything from index one step to the right
        void insert(int index, T value) {
            if (index < 0 || index > size) {
                throw new IndexOutOfBoundsException("index " + index + ", size " + size);
            }
            ensureCapacity();
            System.arraycopy(data, index, data, index + 1, size - index);
            data[index] = value;
            size++;
        }

        @SuppressWarnings("unchecked")
        T remove(int index) {
            checkIndex(index);
            T removed = (T) data[index];
            System.arraycopy(data, index + 1, data, index, size - index - 1);   // shift left over the gap
            data[--size] = null;                                   // IMPORTANT: clear the old slot so the GC can free the object
            shrinkIfSparse();
            return removed;
        }

        int indexOf(Object o) {
            for (int i = 0; i < size; i++) {
                if (o == null ? data[i] == null : o.equals(data[i])) {
                    return i;
                }
            }
            return -1;
        }

        boolean contains(Object o) {
            return indexOf(o) >= 0;
        }

        private void checkIndex(int index) {
            if (index < 0 || index >= size) {
                throw new IndexOutOfBoundsException("index " + index + ", size " + size);
            }
        }

        private void ensureCapacity() {
            if (size == data.length) {
                resize(data.length * 2);                           // DOUBLING is what makes add() amortized O(1)
            }
        }

        private void shrinkIfSparse() {
            if (data.length > INITIAL_CAPACITY && size <= data.length / 4) {
                resize(data.length / 2);                           // shrink at 1/4 (not 1/2) so add/remove at the edge cannot thrash
            }
        }

        private void resize(int newCapacity) {
            Object[] bigger = new Object[newCapacity];
            System.arraycopy(data, 0, bigger, 0, size);
            copies += size;
            resizes++;
            data = bigger;
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < size; i++) {
                if (i > 0) sb.append(", ");
                sb.append(data[i]);
            }
            return sb.append("]").toString();
        }
    }

    static boolean sameContents(DynamicArray<Integer> ours, List<Integer> oracle) {
        if (ours.size() != oracle.size()) return false;
        for (int i = 0; i < ours.size(); i++) {
            if (!ours.get(i).equals(oracle.get(i))) return false;
        }
        return true;
    }

    public static void main(String[] args) {

        // ---------- basic behaviour ----------
        DynamicArray<String> names = new DynamicArray<>();
        names.add("Ada");
        names.add("Linus");
        names.add("Grace");
        names.insert(1, "Alan");
        System.out.println("after adds and insert: " + names + ", size " + names.size() + ", capacity " + names.capacity());
        System.out.println("remove(0) returned " + names.remove(0) + ", now " + names);
        System.out.println("indexOf(\"Grace\") = " + names.indexOf("Grace") + ", contains(\"Zed\") = " + names.contains("Zed"));
        try {
            names.get(10);
        } catch (IndexOutOfBoundsException e) {
            System.out.println("IndexOutOfBoundsException: " + e.getMessage());
        }

        // ---------- capacity growth: doubles every time it fills ----------
        DynamicArray<Integer> growth = new DynamicArray<>();
        StringBuilder capacities = new StringBuilder("capacity changes while adding 1..40: " + growth.capacity());
        int last = growth.capacity();
        for (int i = 1; i <= 40; i++) {
            growth.add(i);
            if (growth.capacity() != last) {
                last = growth.capacity();
                capacities.append(" -> ").append(last);
            }
        }
        System.out.println(capacities);

        // ---------- AMORTIZED O(1): total copying work stays below 2n ----------
        DynamicArray<Integer> big = new DynamicArray<>();
        int n = 100_000;
        for (int i = 0; i < n; i++) {
            big.add(i);
        }
        System.out.println("added " + n + " items using " + big.resizes + " resizes and " + big.copies
                + " element copies (" + String.format("%.2f", (double) big.copies / n) + " copies per add, always below 2)");

        // ---------- shrinking ----------
        DynamicArray<Integer> shrinking = new DynamicArray<>();
        for (int i = 0; i < 64; i++) shrinking.add(i);
        int cap64 = shrinking.capacity();
        while (shrinking.size() > 10) shrinking.remove(shrinking.size() - 1);
        System.out.println("capacity at 64 items: " + cap64 + ", after removing down to 10: " + shrinking.capacity());

        // ---------- ORACLE TEST: 20,000 random operations, compared with java.util.ArrayList after each ----------
        Random random = new Random(12345);                         // fixed seed: the same sequence every run
        DynamicArray<Integer> ours = new DynamicArray<>();
        List<Integer> oracle = new ArrayList<>();
        boolean allMatch = true;
        int removals = 0;
        for (int step = 0; step < 20_000; step++) {
            int action = random.nextInt(4);
            if (action == 0 || oracle.isEmpty()) {
                int v = random.nextInt(1000);
                ours.add(v);
                oracle.add(v);
            } else if (action == 1) {
                int index = random.nextInt(oracle.size() + 1);
                int v = random.nextInt(1000);
                ours.insert(index, v);
                oracle.add(index, v);
            } else if (action == 2) {
                int index = random.nextInt(oracle.size());
                int a = ours.remove(index);
                int b = oracle.remove(index);
                removals++;
                allMatch &= a == b;
            } else {
                int index = random.nextInt(oracle.size());
                ours.set(index, -1);
                oracle.set(index, -1);
            }
            allMatch &= ours.size() == oracle.size();
        }
        allMatch &= sameContents(ours, oracle);
        System.out.println("oracle test: 20000 random operations (" + removals + " removals), identical to ArrayList: " + allMatch);

        // ============================================
        // THINGS TO BREAK ON PURPOSE (when you retype this)
        // 1) Remove the line `data[--size] = null` : the program still works, but the removed objects can never be
        //    garbage-collected ("a memory leak in a managed language").
        // 2) Grow by +1 instead of doubling: watch "copies per add" explode (O(n^2) overall).
        // 3) Shrink at size <= capacity/2 instead of 1/4 and alternate add/remove at the boundary: it resizes every time.
        // ============================================
    }
}
