public class _11_Enums {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS AN ENUM?
        // A special type representing a FIXED set of named constants.
        // Use it whenever a variable should only ever hold ONE of a small,
        // known list of values (e.g., days of the week, order status, directions)
        // ============================================

        Day today = Day.WEDNESDAY;
        System.out.println("Today is: " + today);


        // ============================================
        // SECTION 2: WHY NOT JUST USE STRINGS OR INTS INSTEAD?
        // Enums are much SAFER - the compiler guarantees only valid values
        // can ever be assigned, unlike a String which could be ANY typo
        // ============================================

        System.out.println("Enums prevent typos the compiler can catch at compile time.");


        // ============================================
        // SECTION 3: COMPARING ENUM VALUES
        // Use == for enum comparison (safe and preferred - unlike Strings!)
        // since each enum constant is a single, unique, shared instance
        // ============================================

        if (today == Day.WEDNESDAY) {
            System.out.println("It's midweek!");
        }

        System.out.println("today.equals(Day.WEDNESDAY): " + today.equals(Day.WEDNESDAY));


        // ============================================
        // SECTION 4: USING ENUMS IN A SWITCH STATEMENT
        // A very common, clean pairing - no need to prefix with the enum name
        // inside the switch cases
        // ============================================

        switch (today) {
            case MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY -> System.out.println("It's a weekday.");
            case SATURDAY, SUNDAY -> System.out.println("It's the weekend!");
        }


        // ============================================
        // SECTION 5: BUILT-IN ENUM METHODS
        // Every enum automatically gets these methods for free
        // ============================================

        System.out.println("Name: " + today.name());
        System.out.println("Ordinal (position): " + today.ordinal());

        System.out.println("All days:");
        for (Day d : Day.values()) {
            System.out.println("- " + d + " (position " + d.ordinal() + ")");
        }

        Day parsedDay = Day.valueOf("FRIDAY");
        System.out.println("Parsed from String: " + parsedDay);


        // ============================================
        // SECTION 6: ENUMS WITH FIELDS AND CONSTRUCTORS (MUCH MORE POWERFUL)
        // Enums aren't just labels - each constant can carry its OWN data
        // ============================================

        Planet earth = Planet.EARTH;
        System.out.println(earth + " has gravity: " + earth.getGravity());
        System.out.println(earth + " distance from sun: " + earth.getDistanceFromSun() + " million km");

        System.out.println("\nAll planets and their gravity:");
        for (Planet p : Planet.values()) {
            System.out.println(p + ": " + p.getGravity() + " m/s^2");
        }


        // ============================================
        // SECTION 7: ENUMS WITH THEIR OWN METHODS (BEHAVIOR, NOT JUST DATA)
        // ============================================

        System.out.println("\nWeight of 70kg person on each planet:");
        for (Planet p : Planet.values()) {
            System.out.printf("%s: %.2f kg-equivalent%n", p, p.calculateWeight(70));
        }


        // ============================================
        // SECTION 8: ENUMS WITH CONSTANT-SPECIFIC METHOD BODIES (ADVANCED)
        // Each constant can override a method with its OWN unique behavior
        // ============================================

        for (TrafficLight light : TrafficLight.values()) {
            System.out.println(light + " means: " + light.getAction());
        }


        // ============================================
        // SECTION 9: WHEN TO USE ENUMS
        // ============================================

        // Use an enum when:
        // - A variable should only ever be ONE of a small, fixed, known set of values
        // - You want compile-time safety against typos/invalid values
        // - Each "option" might need its OWN associated data or behavior
        //   (like Planet's gravity, or TrafficLight's action)
        // - You'd otherwise be tempted to use "magic strings" or "magic numbers"
        //   to represent a fixed category of things
    }
}


// ============================================
// SIMPLE ENUM - just a fixed list of named constants
// ============================================

enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}


// ============================================
// ENUM WITH FIELDS AND A CONSTRUCTOR
// Each constant calls the constructor with its OWN specific values
// ============================================

enum Planet {
    MERCURY(3.7, 57.9),
    VENUS(8.9, 108.2),
    EARTH(9.8, 149.6),
    MARS(3.7, 227.9);

    // --- Fields: every constant carries its own copy of these ---
    private final double gravity;
    private final double distanceFromSun;

    // --- Constructor: runs ONCE per constant, at class-loading time ---
    Planet(double gravity, double distanceFromSun) {
        this.gravity = gravity;
        this.distanceFromSun = distanceFromSun;
    }

    // --- Getters ---
    double getGravity() {
        return gravity;
    }

    double getDistanceFromSun() {
        return distanceFromSun;
    }

    // --- A regular method using the enum's own data ---
    double calculateWeight(double massOnEarthKg) {
        return massOnEarthKg * (gravity / 9.8);
    }
}


// ============================================
// ENUM WITH CONSTANT-SPECIFIC METHOD IMPLEMENTATIONS (ADVANCED)
// Each constant provides its OWN version of an abstract method -
// similar in spirit to abstract classes, but within an enum
// ============================================

enum TrafficLight {
    RED {
        @Override
        String getAction() {
            return "Stop";
        }
    },
    YELLOW {
        @Override
        String getAction() {
            return "Slow down";
        }
    },
    GREEN {
        @Override
        String getAction() {
            return "Go";
        }
    };

    // Abstract method - EVERY constant above must implement it
    abstract String getAction();
}