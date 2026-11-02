// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.TreeMap;
import java.util.stream.Collectors;

/**
 * CAPSTONE: employee analytics with streams.
 * Questions answered, each by ONE pipeline:
 *   1. headcount and total payroll per department
 *   2. average salary per department (rounded)
 *   3. the highest-paid employee in each department
 *   4. the top 3 earners overall
 *   5. who earns more than the company average
 *   6. salary bands (partition)
 *   7. all skills known across the company, with how many people have each
 *   8. a printable report line per department
 * And at the end: the same question answered with a loop, so you can judge readability honestly.
 */
public class _8_StreamsCapstone {

    record Employee(String name, String department, int salary, List<String> skills) { }

    public static void main(String[] args) {

        List<Employee> staff = List.of(
                new Employee("Ada", "Engineering", 130_000, List.of("java", "math")),
                new Employee("Linus", "Engineering", 120_000, List.of("c", "git")),
                new Employee("Grace", "Engineering", 150_000, List.of("java", "compilers")),
                new Employee("Margaret", "Operations", 95_000, List.of("planning", "git")),
                new Employee("Tim", "Operations", 80_000, List.of("planning")),
                new Employee("Radia", "Security", 140_000, List.of("networks", "java")),
                new Employee("Whit", "Security", 135_000, List.of("crypto", "networks")));

        // ---------- 1. headcount and payroll per department ----------
        Map<String, Long> headcount = staff.stream()
                .collect(Collectors.groupingBy(Employee::department, TreeMap::new, Collectors.counting()));
        Map<String, Integer> payroll = staff.stream()
                .collect(Collectors.groupingBy(Employee::department, TreeMap::new, Collectors.summingInt(Employee::salary)));
        System.out.println("1. headcount: " + headcount);
        System.out.println("   payroll:   " + payroll);

        // ---------- 2. average salary per department ----------
        Map<String, Double> average = staff.stream()
                .collect(Collectors.groupingBy(Employee::department, TreeMap::new, Collectors.averagingInt(Employee::salary)));
        average.forEach((dept, avg) -> System.out.printf("2. average in %-11s %,10.2f%n", dept + ":", avg));

        // ---------- 3. highest paid per department ----------
        Map<String, Optional<Employee>> best = staff.stream()
                .collect(Collectors.groupingBy(Employee::department, TreeMap::new,
                        Collectors.maxBy(Comparator.comparingInt(Employee::salary))));
        best.forEach((dept, e) -> System.out.println("3. top earner in " + dept + ": " + e.get().name()));

        // ---------- 4. top 3 earners overall ----------
        List<String> top3 = staff.stream()
                .sorted(Comparator.comparingInt(Employee::salary).reversed())
                .limit(3)
                .map(e -> e.name() + " (" + e.salary() + ")")
                .toList();
        System.out.println("4. top 3: " + top3);

        // ---------- 5. above the company average ----------
        double companyAverage = staff.stream().mapToInt(Employee::salary).average().orElse(0);
        List<String> aboveAverage = staff.stream()
                .filter(e -> e.salary() > companyAverage)
                .map(Employee::name)
                .sorted()
                .toList();
        System.out.printf("5. company average %,.2f; above it: %s%n", companyAverage, aboveAverage);

        // ---------- 6. salary bands ----------
        Map<Boolean, List<String>> bands = staff.stream()
                .collect(Collectors.partitioningBy(e -> e.salary() >= 130_000,
                        Collectors.mapping(Employee::name, Collectors.toList())));
        System.out.println("6. 130k and above: " + bands.get(true));
        System.out.println("   below 130k:     " + bands.get(false));

        // ---------- 7. skills: flatMap then count ----------
        Map<String, Long> skillCounts = staff.stream()
                .flatMap(e -> e.skills().stream())
                .collect(Collectors.groupingBy(s -> s, TreeMap::new, Collectors.counting()));
        System.out.println("7. skills: " + skillCounts);
        String mostCommon = skillCounts.entrySet().stream()
                .max(Map.Entry.<String, Long>comparingByValue().thenComparing(Map.Entry.comparingByKey(Comparator.reverseOrder())))
                .map(Map.Entry::getKey)
                .orElse("none");
        System.out.println("   most common skill: " + mostCommon + " (ties broken alphabetically)");

        // ---------- 8. one report line per department ----------
        System.out.println("8. report:");
        staff.stream()
                .collect(Collectors.groupingBy(Employee::department, TreeMap::new, Collectors.toList()))
                .forEach((dept, members) -> System.out.println("   " + dept + " -> "
                        + members.stream().map(Employee::name).sorted().collect(Collectors.joining(", "))));

        // ============================================
        // HONEST COMPARISON: question 3 (top earner per department) with a plain loop
        // ============================================

        Map<String, Employee> bestLoop = new TreeMap<>();
        for (Employee e : staff) {
            Employee current = bestLoop.get(e.department());
            if (current == null || e.salary() > current.salary()) {
                bestLoop.put(e.department(), e);
            }
        }
        boolean same = true;
        for (Map.Entry<String, Optional<Employee>> entry : best.entrySet()) {
            same &= bestLoop.get(entry.getKey()).equals(entry.getValue().get());
        }
        System.out.println("loop and stream agree on question 3: " + same);
        // The loop is 7 lines and easy to follow for ONE question. The stream version
        // scales better when you need MANY different group-bys, but its collector
        // nesting takes practice to read. Neither is "always better".
    }
}
