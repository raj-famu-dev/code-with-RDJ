// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.stream.Collectors;

public class _5_Collectors {

    // (Records are covered in 09-modern-java. Read this as a tiny class with fields
    //  and accessor methods name(), city(), age().)
    record Person(String name, String city, int age) { }

    public static void main(String[] args) {

        List<Person> people = List.of(
                new Person("Ada", "London", 36),
                new Person("Alan", "London", 41),
                new Person("Grace", "New York", 85),
                new Person("Linus", "Helsinki", 55),
                new Person("Margaret", "New York", 29),
                new Person("Tim", "London", 29));

        // ============================================
        // SECTION 1: WHAT A COLLECTOR IS
        // collect(...) is the terminal operation that gathers a stream into a result.
        // A Collector describes HOW. Collectors.* has ready-made ones.
        // (Many Map and Set results below are copied into a TreeMap/TreeSet so the printed
        //  order is stable: HashMap iteration order is not something to rely on.)
        // ============================================

        // toList / toSet / toCollection
        List<String> names = people.stream().map(Person::name).collect(Collectors.toList());
        Set<String> cities = people.stream().map(Person::city).collect(Collectors.toCollection(TreeSet::new));
        System.out.println("toList:       " + names);
        System.out.println("toCollection: " + cities + "  (a TreeSet: sorted, distinct)");
        System.out.println("Stream.toList() (Java 16+) is a shortcut for an unmodifiable list: "
                + people.stream().map(Person::age).toList());


        // ============================================
        // SECTION 2: joining - STRINGS
        // ============================================

        System.out.println("joining:      " + people.stream().map(Person::name).collect(Collectors.joining(", ", "{", "}")));


        // ============================================
        // SECTION 3: toMap - KEY AND VALUE FUNCTIONS
        // Throws IllegalStateException if two elements produce the SAME KEY, unless you
        // supply a merge function as a third argument.
        // ============================================

        Map<String, Integer> ageByName = people.stream().collect(Collectors.toMap(Person::name, Person::age));
        System.out.println("toMap name->age: " + new TreeMap<>(ageByName));

        try {
            people.stream().collect(Collectors.toMap(Person::city, Person::name));   // London appears 3 times
        } catch (IllegalStateException e) {
            System.out.println("duplicate key -> IllegalStateException: " + e.getMessage());
        }

        Map<String, String> merged = people.stream().collect(
                Collectors.toMap(Person::city, Person::name, (a, b) -> a + "+" + b));   // merge function resolves clashes
        System.out.println("toMap with merge function: " + new TreeMap<>(merged));


        // ============================================
        // SECTION 4: groupingBy - THE MOST USEFUL ONE ("GROUP BY" IN SQL)
        // groupingBy(classifier) -> Map<Key, List<Element>>
        // ============================================

        Map<String, List<String>> namesByCity = people.stream().collect(
                Collectors.groupingBy(Person::city, TreeMap::new, Collectors.mapping(Person::name, Collectors.toList())));
        System.out.println("names by city:     " + namesByCity);

        // The second argument ("downstream collector") decides what happens inside each group
        Map<String, Long> countByCity = people.stream().collect(
                Collectors.groupingBy(Person::city, TreeMap::new, Collectors.counting()));
        System.out.println("count by city:     " + countByCity);

        Map<String, Double> averageAgeByCity = people.stream().collect(
                Collectors.groupingBy(Person::city, TreeMap::new, Collectors.averagingInt(Person::age)));
        System.out.println("average age by city: " + averageAgeByCity);

        Map<String, Integer> totalAgeByCity = people.stream().collect(
                Collectors.groupingBy(Person::city, TreeMap::new, Collectors.summingInt(Person::age)));
        System.out.println("sum of ages by city: " + totalAgeByCity);

        Map<String, java.util.Optional<Person>> oldestByCity = people.stream().collect(
                Collectors.groupingBy(Person::city, TreeMap::new,
                        Collectors.maxBy(java.util.Comparator.comparingInt(Person::age))));
        oldestByCity.forEach((city, p) -> System.out.println("oldest in " + city + ": " + p.get().name()));


        // ============================================
        // SECTION 5: partitioningBy - EXACTLY TWO GROUPS (true / false)
        // Always returns both keys, even if one group is empty.
        // ============================================

        Map<Boolean, List<String>> adultsVsRest = people.stream().collect(
                Collectors.partitioningBy(p -> p.age() >= 40, Collectors.mapping(Person::name, Collectors.toList())));
        System.out.println("age >= 40:  " + adultsVsRest.get(true));
        System.out.println("age <  40:  " + adultsVsRest.get(false));


        // ============================================
        // SECTION 6: SUMMARY NUMBERS
        // ============================================

        System.out.println("summarizingInt: " + people.stream().collect(Collectors.summarizingInt(Person::age)));
        System.out.println("averagingInt:   " + people.stream().collect(Collectors.averagingInt(Person::age)));
        System.out.println("counting:       " + people.stream().collect(Collectors.counting()));


        // ============================================
        // SECTION 7: WHICH ONE?
        // a list/set                  -> toList() / toSet() / toCollection(...)
        // one string                  -> joining
        // lookup table                -> toMap (mind duplicate keys)
        // group + something per group -> groupingBy(classifier, downstream)
        // yes/no split                -> partitioningBy
        // ============================================
    }
}
