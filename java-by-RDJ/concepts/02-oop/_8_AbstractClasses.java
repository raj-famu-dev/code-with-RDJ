public class _8_AbstractClasses {
    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT IS AN ABSTRACT CLASS?
        // A class that CANNOT be instantiated directly - it exists only to
        // be extended. It can mix fully-implemented methods with "abstract"
        // methods that have NO body, forcing child classes to provide one.
        // ============================================

        // Shape shape = new Shape();  // COMPILE ERROR - cannot instantiate an abstract class!


        // ============================================
        // SECTION 2: CREATING CONCRETE (NON-ABSTRACT) SUBCLASSES
        // A subclass of an abstract class MUST implement all abstract methods,
        // or it too must be declared abstract
        // ============================================

        Circle circle = new Circle(5);
        Rectangle rectangle = new Rectangle(4, 6);

        System.out.println("Circle area: " + circle.calculateArea());
        System.out.println("Rectangle area: " + rectangle.calculateArea());


        // ============================================
        // SECTION 3: ABSTRACT METHODS - DECLARED BUT NOT IMPLEMENTED
        // The abstract class defines WHAT must exist (the method signature),
        // but each subclass decides HOW it actually works
        // ============================================

        // See Shape.calculateArea() below - it has NO body, just a signature
        // ending in a semicolon. Circle and Rectangle each provide their OWN
        // completely different implementation.


        // ============================================
        // SECTION 4: CONCRETE (REGULAR) METHODS INSIDE AN ABSTRACT CLASS
        // Abstract classes CAN also have fully-implemented methods that are
        // shared by ALL subclasses automatically - no need to repeat this
        // logic in every child class
        // ============================================

        circle.displayInfo();       // inherited, fully-implemented method from Shape
        rectangle.displayInfo();    // same shared method, different object


        // ============================================
        // SECTION 5: POLYMORPHISM WITH ABSTRACT CLASSES
        // Just like _7_Polymorphism - an abstract PARENT type reference can
        // point to any CONCRETE child object
        // ============================================

        Shape[] shapes = { new Circle(3), new Rectangle(2, 5), new Triangle(4, 6) };

        System.out.println("Calculating area for all shapes:");
        for (Shape s : shapes) {
            System.out.println(s.getName() + " area: " + s.calculateArea());
        }
        // Each shape correctly calculates its OWN area - polymorphism in action,
        // but now built on an abstract foundation that GUARANTEES every
        // shape subtype has a calculateArea() method to call


        // ============================================
        // SECTION 6: ABSTRACT CLASSES CAN HAVE CONSTRUCTORS
        // Even though you can't create a Shape directly, its constructor
        // still runs whenever a SUBCLASS object is created (via super())
        // ============================================

        // See Circle/Rectangle/Triangle constructors below - each calls
        // super(name) to initialize the shared 'name' field in Shape


        // ============================================
        // SECTION 7: ABSTRACT CLASSES CAN HAVE FIELDS TOO
        // Just like a regular class - shared state that every subclass inherits
        // ============================================

        System.out.println("Circle's inherited name field: " + circle.name);


        // ============================================
        // SECTION 8: A SUBCLASS THAT DOESN'T IMPLEMENT AN ABSTRACT METHOD
        // MUST ALSO BE DECLARED ABSTRACT
        // ============================================

        // class IncompleteShape extends Shape {
        //     // forgot to implement calculateArea()
        // }
        // COMPILE ERROR unless IncompleteShape is ALSO declared abstract:
        // abstract class IncompleteShape extends Shape { }  // this would be fine,
        // but then IncompleteShape ALSO can't be instantiated directly


        // ============================================
        // SECTION 9: WHEN TO USE AN ABSTRACT CLASS
        // ============================================

        // Use an abstract class when:
        // - Multiple related classes share SOME common implementation (like displayInfo())
        // - You want to FORCE subclasses to implement certain methods (like calculateArea())
        // - The classes share a genuine "is-a" relationship (a Circle IS-A Shape)
        // - You need shared FIELDS and CONSTRUCTORS across the family of classes

        // (Compare this to interfaces in the next topic, which take a
        // slightly different, more flexible approach to the same general idea)
    }
}


// ============================================
// THE ABSTRACT CLASS
// ============================================

abstract class Shape {

    String name;  // shared field - every shape has a name

    // Constructor - runs via super() whenever a subclass object is created
    Shape(String name) {
        this.name = name;
    }

    // --- ABSTRACT METHOD ---
    // NO body at all - just a signature. Every concrete subclass MUST provide
    // its own implementation, or the subclass itself must also be abstract.
    abstract double calculateArea();

    // --- CONCRETE (REGULAR) METHOD ---
    // Fully implemented here, shared automatically by EVERY subclass -
    // no need to rewrite this in Circle, Rectangle, or Triangle
    void displayInfo() {
        System.out.println(name + " has an area of " + calculateArea());
    }

    String getName() {
        return name;
    }
}


// ============================================
// CONCRETE SUBCLASSES - each MUST implement calculateArea()
// ============================================

class Circle extends Shape {
    double radius;

    Circle(double radius) {
        super("Circle");
        this.radius = radius;
    }

    @Override
    double calculateArea() {
        return Math.PI * radius * radius;
    }
}

class Rectangle extends Shape {
    double width;
    double height;

    Rectangle(double width, double height) {
        super("Rectangle");
        this.width = width;
        this.height = height;
    }

    @Override
    double calculateArea() {
        return width * height;
    }
}

class Triangle extends Shape {
    double base;
    double height;

    Triangle(double base, double height) {
        super("Triangle");
        this.base = base;
        this.height = height;
    }

    @Override
    double calculateArea() {
        return 0.5 * base * height;
    }
}