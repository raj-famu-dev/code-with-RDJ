// Tags: #Java #Collections #UtilityImmutableCollections | @rdj_369 | Java 21 (JDK 21)
// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.*;

public class _12_UtilityAndImmutableCollections {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE Collections HELPER CLASS (note the s)
        // Collection = an interface. Collections = a class of static helpers.
        // ============================================

        List<Integer> nums = new ArrayList<>(List.of(5, 3, 9, 1, 7, 3));

        Collections.sort(nums);
        System.out.println("sorted:    " + nums);
        Collections.reverse(nums);
        System.out.println("reversed:  " + nums);
        Collections.shuffle(nums, new Random(42));        // seeded Random = repeatable shuffle
        System.out.println("shuffled (seed 42): " + nums);
        System.out.println("max=" + Collections.max(nums) + ", min=" + Collections.min(nums)
                + ", frequency of 3 = " + Collections.frequency(nums, 3));
        Collections.swap(nums, 0, nums.size() - 1);


        // ============================================
        // SECTION 2: binarySearch NEEDS A SORTED LIST
        // On an unsorted list the result is meaningless.
        // A negative result means "not found" (it encodes where it would go).
        // ============================================

        List<Integer> sorted = new ArrayList<>(List.of(1, 3, 5, 7, 9));
        System.out.println("binarySearch 7: index " + Collections.binarySearch(sorted, 7));
        System.out.println("binarySearch 4: " + Collections.binarySearch(sorted, 4) + " (negative = not found)");


        // ============================================
        // SECTION 3: List.of IS IMMUTABLE
        // Cannot add, remove, or set. Also refuses null elements.
        // ============================================

        List<String> fixed = List.of("a", "b");
        try {
            fixed.add("c");
        } catch (UnsupportedOperationException e) {
            System.out.println("List.of(...).add -> UnsupportedOperationException");
        }
        try {
            List.of("a", null);
        } catch (NullPointerException e) {
            System.out.println("List.of(..., null) -> NullPointerException");
        }
        // Set.of and Map.of are immutable too. Set.of / Map.of reject duplicates,
        // and their iteration order is deliberately unspecified.


        // ============================================
        // SECTION 4: TRAP - Arrays.asList IS FIXED-SIZE, NOT IMMUTABLE
        // You CAN set() elements, you CANNOT add/remove, and the list is a
        // VIEW of the array: changing one changes the other.
        // ============================================

        String[] array = {"x", "y", "z"};
        List<String> view = Arrays.asList(array);
        view.set(0, "X");
        System.out.println("array[0] after view.set: " + array[0]);
        try {
            view.add("w");
        } catch (UnsupportedOperationException e) {
            System.out.println("Arrays.asList(...).add -> UnsupportedOperationException");
        }


        // ============================================
        // SECTION 5: unmodifiableList IS A READ-ONLY VIEW, List.copyOf IS A SNAPSHOT
        // The view still changes when the underlying list changes.
        // ============================================

        List<String> source = new ArrayList<>(List.of("a", "b"));
        List<String> readOnlyView = Collections.unmodifiableList(source);
        List<String> snapshot = List.copyOf(source);

        source.add("c");
        System.out.println("view after source.add:     " + readOnlyView + "   (sees the change)");
        System.out.println("snapshot after source.add: " + snapshot + "      (does not)");
        try {
            readOnlyView.add("d");
        } catch (UnsupportedOperationException e) {
            System.out.println("Cannot change through the view");
        }


        // ============================================
        // SECTION 6: WHY IMMUTABLE COLLECTIONS?
        // - Safe to share and return from methods (defensive copying)
        // - Safe to use from several threads
        // - Clear intent: "this data does not change"
        // Rule of thumb: return List.copyOf(...) or an unmodifiable view from a
        // getter instead of exposing your internal list.
        // ============================================
    }
}
