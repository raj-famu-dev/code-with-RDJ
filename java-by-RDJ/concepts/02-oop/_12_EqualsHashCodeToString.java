import java.util.HashSet;
import java.util.HashMap;

public class _12_EqualsHashCodeToString {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: THE DEFAULT toString() PROBLEM
        // Every class implicitly extends Object (recap from Inheritance),
        // which provides a default toString() - but it's not very useful
        // ============================================

        PersonUnoverridden person1 = new PersonUnoverridden("Alice", 30);
        System.out.println("Default toString(): " + person1);
        // prints something like: PersonUnoverridden@1b6d3586
        // (class name + hashcode in hex) - completely useless for debugging


        // ============================================
        // SECTION 2: OVERRIDING toString()
        // Provide a MEANINGFUL, readable representation of the object
        // ============================================

        Person person2 = new Person("Bob", 25);
        System.out.println("Overridden toString(): " + person2);
        // Now prints something actually useful, like: Person{name='Bob', age=25}

        // toString() is called AUTOMATICALLY whenever you print an object,
        // or concatenate it into a String - you never need to call it explicitly
        System.out.println("Concatenated directly: " + "Info -> " + person2);


        // ============================================
        // SECTION 3: THE DEFAULT equals() PROBLEM
        // By default, equals() just checks if two references point to the
        // EXACT SAME object in memory (identical to using ==)
        // ============================================

        PersonUnoverridden p1 = new PersonUnoverridden("Charlie", 40);
        PersonUnoverridden p2 = new PersonUnoverridden("Charlie", 40);

        System.out.println("Same content, default equals(): " + p1.equals(p2));
        // FALSE! Even though the content is identical, default equals() only
        // checks if they're the SAME object in memory - and they're not,
        // they're two SEPARATE objects that just happen to have equal fields


        // ============================================
        // SECTION 4: OVERRIDING equals() PROPERLY
        // Define what "equal" actually MEANS for your class - usually,
        // comparing the meaningful fields rather than memory identity
        // ============================================

        Person person3 = new Person("Dana", 28);
        Person person4 = new Person("Dana", 28);

        System.out.println("Same content, overridden equals(): " + person3.equals(person4));
        // TRUE now - because we defined equality as "same name AND same age"

        Person person5 = new Person("Dana", 99);
        System.out.println("Different age, overridden equals(): " + person3.equals(person5));
        // FALSE - ages differ, so they're correctly NOT equal


        // ============================================
        // SECTION 5: THE equals()/hashCode() CONTRACT (CRITICAL RULE)
        // RULE: if two objects are equal() to each other, they MUST have
        // the SAME hashCode(). If you override equals() WITHOUT overriding
        // hashCode() to match, you break this contract - and things silently
        // malfunction in hash-based collections (HashMap, HashSet, HashTable)
        // ============================================

        System.out.println("person3 hashCode: " + person3.hashCode());
        System.out.println("person4 hashCode: " + person4.hashCode());
        System.out.println("Equal objects have equal hashCodes: " +
                (person3.hashCode() == person4.hashCode()));
        // TRUE - because we overrode hashCode() consistently with equals()


        // ============================================
        // SECTION 6: WHY THIS CONTRACT MATTERS - HashSet DEMONSTRATION
        // HashSet uses hashCode() to decide WHICH internal "bucket" to check,
        // then equals() to confirm an actual match within that bucket.
        // If hashCode() is wrong/missing, HashSet can't find duplicates correctly.
        // ============================================

        HashSet<PersonUnoverridden> unsafeSet = new HashSet<>();
        unsafeSet.add(new PersonUnoverridden("Eve", 22));
        unsafeSet.add(new PersonUnoverridden("Eve", 22));  // "duplicate" content

        System.out.println("Unsafe HashSet size (should be 1 if truly deduplicated): " +
                unsafeSet.size());
        // Prints 2! Because without proper equals()/hashCode(), HashSet thinks
        // these are two DIFFERENT people, even though their data is identical


        HashSet<Person> safeSet = new HashSet<>();
        safeSet.add(new Person("Eve", 22));
        safeSet.add(new Person("Eve", 22));  // genuinely a duplicate now

        System.out.println("Safe HashSet size (properly deduplicated): " + safeSet.size());
        // Prints 1! Because our overridden equals()/hashCode() correctly
        // identifies these as the same logical person


        // ============================================
        // SECTION 7: HashMap ALSO DEPENDS ON THIS CONTRACT
        // Using a custom object as a HashMap KEY requires proper equals()/hashCode(),
        // or lookups will silently fail to find entries that "should" match
        // ============================================

        HashMap<Person, String> personRoles = new HashMap<>();
        personRoles.put(new Person("Frank", 35), "Manager");

        // Looking up with a DIFFERENT object instance, but EQUAL content
        String role = personRoles.get(new Person("Frank", 35));
        System.out.println("Role found via equal (but different) object: " + role);
        // Works correctly and returns "Manager" - only because equals()/hashCode()
        // are properly overridden; without them, this would return null


        // ============================================
        // SECTION 8: THE STANDARD PATTERN FOR OVERRIDING equals()
        // ============================================

        // See Person.equals() below - the standard defensive pattern:
        // 1. Check reference equality first (fast path, same object)
        // 2. Check null and class type
        // 3. Cast and compare the actual meaningful fields


        // ============================================
        // SECTION 9: Objects.equals() AND Objects.hash() - HELPER UTILITIES
        // java.util.Objects provides null-safe helpers that make writing
        // correct equals()/hashCode() much less error-prone by hand
        // ============================================

        // See Person's equals()/hashCode() implementation below - uses
        // java.util.Objects.equals() and java.util.Objects.hash() internally
    }
}


// ============================================
// CLASS WITHOUT ANY OVERRIDES - shows the default (unhelpful) behavior
// ============================================

class PersonUnoverridden {
    String name;
    int age;

    PersonUnoverridden(String name, int age) {
        this.name = name;
        this.age = age;
    }
    // No toString(), equals(), or hashCode() overrides - uses Object's defaults
}


// ============================================
// PROPERLY OVERRIDDEN CLASS
// ============================================

class Person {
    String name;
    int age;

    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // --- OVERRIDING toString() ---
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }

    // --- OVERRIDING equals() - THE STANDARD DEFENSIVE PATTERN ---
    @Override
    public boolean equals(Object obj) {
        // Step 1: fast path - if it's literally the same object, they're equal
        if (this == obj) {
            return true;
        }

        // Step 2: null check and class type check
        if (obj == null || getClass() != obj.getClass()) {
            return false;
        }

        // Step 3: cast and compare the actual meaningful fields
        Person other = (Person) obj;
        return this.age == other.age && java.util.Objects.equals(this.name, other.name);
        // Objects.equals() is null-safe - avoids a manual null check on 'name'
    }

    // --- OVERRIDING hashCode() - MUST BE CONSISTENT WITH equals() ---
    @Override
    public int hashCode() {
        // Objects.hash() combines multiple fields into one hashCode safely,
        // using the SAME fields that equals() compares - this is the key rule
        return java.util.Objects.hash(name, age);
    }
}