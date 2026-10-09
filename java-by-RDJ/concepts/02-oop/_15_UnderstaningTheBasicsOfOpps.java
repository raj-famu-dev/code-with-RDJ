// ============================================
// MAIN: everything comes together here
// ============================================
public class _15_UnderstaningTheBasicsOfOpps {
    static void main() {
        // Animals animal = new Animals("Generic", 1, "Unknown");
        // COMPILE ERROR - Animal is abstract, cannot be instantiated directly

        // ENCAPSULATION in action: age validation triggered here
        Dogs dog=new Dogs("Rex",-5);//invalid age gets corrected to 0
        Cats cat=new Cats("Wiskers",3);

        System.out.println("Rex's age after invalid input: " + dog.getAge());
        System.out.println();

        // INHERITANCE in action: both objects use the SAME breathe() method,
        // never rewritten in Dog or Cat
        dog.breathe();
        cat.breathe();
        System.out.println();

        // POLYMORPHISM in action: one array, typed as the abstract PARENT,
        // holding different CONCRETE child objects

        Animals[] animals={dog,cat};

        System.out.println("Displaying info for all animals:");
        for (Animals a : animals) {
            a.displayInfo();  // each one correctly plays ITS OWN sound
        }

    }
}

// ============================================
// ABSTRACTION + ENCAPSULATION: the abstract parent class
// ============================================
abstract class Animals {

    // ENCAPSULATION: private fields, no direct outside access
    private String name;
    private int age;
    private String category;

Animals(String name, int age, String category) {
    this.name = name;
    this.category=category;
    // Using the setter here too, so even the constructor
    // benefits from validation logic (see setAge below)
    setAge(age);
}

// --- GETTERS: controlled read access ---
    String getName() {
    return name;
    }
    int getAge() {
    return age;
    }
    String getCategory() {
    return category;
    }

    // --- SETTER WITH VALIDATION: controlled write access ---
    void setAge(int age) {
        if (age > 0) {
            this.age = age;
        } else {
            System.out.println("Invalid age for " + name + " - defaulting to 0.");
            this.age = 0;
        }
    }
        // ABSTRACTION: every subclass MUST define its own sound -
        // Animal itself doesn't know HOW each type of animal sounds
        abstract void makeSound();

        // ABSTRACTION: a concrete method shared by every subclass automatically -
        // no need to repeat this logic in Dog, Cat, or any future subclass
        void breathe() {
            System.out.println(name + " is breathing...");
        }

    // A concrete method that USES the abstract method internally -
    // this is what makes abstraction and polymorphism interrelated:
    // displayInfo() doesn't know WHICH sound will play, it just trusts
    // whichever actual subclass is calling it to know its own sound
    void displayInfo(){
        System.out.print(name + " (" + category + ", age " + age + "): ");
        makeSound();  // POLYMORPHISM happens right here
    }
}

// ============================================
// INHERITANCE: Dog reuses everything Animal already built
// ============================================

class Dogs extends Animals {
    Dogs(String name,int age) {
        super(name,age,"Canine");//calls Animal constructor
    }
    // POLYMORPHISM (method overriding): Dog's own version of the
    // method Animal declared but never implemented
    @Override
    void makeSound() {
        System.out.println(getName()+" says: Woof Woof!");
    }
}

// ============================================
// INHERITANCE: Cat, a SECOND subclass, proving the abstraction
// actually forces EVERY subclass to supply its own sound
// ============================================

class Cats extends Animals {
    Cats(String name,int age) {
        super(name,age,"Feline");
    }
    @Override
    void makeSound() {
        System.out.println(getName()+" says: Meow!");
    }
}




