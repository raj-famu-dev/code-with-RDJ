// Tags: #Cpp #OOP #Inheritance | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: public inheritance, constructor chaining (base first), `protected`,
 * name hiding, and the SLICING trap: copying a Derived into a Base by value
 * silently discards the derived part. Fixed by using references/pointers.
 * (Runtime dispatch via virtual comes in the next file; here methods are non-virtual on purpose.)
 */
#include <iostream>
#include <string>
#include <vector>

// ===== SECTION 1: public inheritance + constructor chaining =====
class Animal {
public:
    explicit Animal(std::string name) : name_(std::move(name)) { std::cout << "  Animal(" << name_ << ")\n"; }
    std::string describe() const { return "Animal named " + name_; }
    const std::string& name() const { return name_; }
protected:
    int energy_ = 10;                                         // visible to derived classes
private:
    std::string name_;
};

class Dog : public Animal {
public:
    Dog(std::string name, std::string breed) : Animal(std::move(name)), breed_(std::move(breed)) {   // chain to base ctor
        std::cout << "  Dog(" << breed_ << ")\n";
    }
    void run() { energy_ -= 3; }                              // protected member usable here
    int energy() const { return energy_; }
    const std::string& breed() const { return breed_; }
    std::string describe() const { return "Dog " + name() + " (" + breed_ + ")"; }   // HIDES Animal::describe
private:
    std::string breed_;
};

// ===== SECTION 2: protected vs private =====
// energy_ is protected in Animal: Dog can touch it, outside code cannot (compile error).

// ===== SECTION 3: slicing =====
std::string takeByValue(Animal a) { return a.describe(); }          // copies ONLY the Animal part
std::string takeByRef(const Animal& a) { return a.describe(); }     // no copy, but still calls Animal::describe (non-virtual)

int main() {
    std::cout << "===== SECTION 1: public inheritance + constructor chaining =====\n";
    Dog d("Rex", "Beagle");
    std::cout << "d.describe()  = " << d.describe() << " (Dog's version hides Animal's)\n";
    std::cout << "d.Animal::describe() = " << d.Animal::describe() << " (explicit qualification reaches the hidden one)\n";
    Animal& asBase = d;
    std::cout << "asBase.describe() = " << asBase.describe() << " (non-virtual: chosen by the STATIC type)\n";

    std::cout << "\n===== SECTION 2: protected vs private =====\n";
    d.run();
    std::cout << "after run(): energy = " << d.energy() << " (Dog changed the protected base member)\n";
    std::cout << "d.energy_ from main would not compile (protected).\n";

    std::cout << "\n===== SECTION 3: slicing =====\n";
    std::cout << "sizeof(Animal) = " << sizeof(Animal) << ", sizeof(Dog) = " << sizeof(Dog) << " (Dog is larger: extra breed_)\n";
    Animal sliced = d;                                         // TRAP: copy-initializes an Animal from a Dog
    std::cout << "Animal sliced = d;  sliced.describe() = " << sliced.describe() << "\n";
    std::cout << "the breed is gone: there is nowhere in an Animal to store it.\n";
    std::cout << "takeByValue(d) = " << takeByValue(d) << " (sliced copy)\n";
    std::cout << "takeByRef(d)   = " << takeByRef(d) << " (no slicing, but still the base function)\n";

    std::vector<Animal> bad;                                   // a vector of values slices every element
    bad.push_back(d);
    std::cout << "vector<Animal> holding a Dog: size of stored element = " << sizeof(bad[0]) << " bytes (Animal-sized)\n";
    std::vector<const Animal*> view;                           // fix: non-owning pointers keep the full object intact
    view.push_back(&d);
    std::cout << "vector<const Animal*> view: the Dog is still whole, breed = "
              << static_cast<const Dog*>(view[0])->breed() << " (static_cast is safe here; virtual functions, next file, remove the need for it)\n";
    std::cout << "NOTE: owning a Dog through unique_ptr<Animal> would need a virtual destructor in Animal (see next file).\n";
    return 0;
}
