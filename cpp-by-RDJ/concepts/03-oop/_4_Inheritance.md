# `_4_Inheritance.cpp`

> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

## Concept
Inheritance lets a derived class reuse and extend a base class: `class Dog : public Animal`. The derived object contains the base object inside it, which is why the base constructor runs first and why copying a `Dog` into an `Animal` by value cuts the extra part off ("slicing").

In this file the methods are deliberately non-virtual to isolate the basics; the next file adds `virtual`, which changes how calls are chosen.

## Full Line-by-Line Breakdown

### SECTION 1: public inheritance + constructor chaining
`Dog(std::string name, std::string breed) : Animal(std::move(name)), breed_(...)` calls the base constructor in the initializer list. The output shows `Animal(Rex)` printed before `Dog(Beagle)`: base first, always. `Dog::describe` has the same name as `Animal::describe`, so it HIDES it. `d.Animal::describe()` reaches the hidden one. Through a base reference (`Animal& asBase = d`) the NON-virtual function is chosen by the declared type, so it prints the Animal text even though the object is a Dog. In Java this would call the Dog version; that is the single biggest surprise for Java programmers.

Output from a real run:

```text
===== SECTION 1: public inheritance + constructor chaining =====
  Animal(Rex)
  Dog(Beagle)
d.describe()  = Dog Rex (Beagle) (Dog's version hides Animal's)
d.Animal::describe() = Animal named Rex (explicit qualification reaches the hidden one)
asBase.describe() = Animal named Rex (non-virtual: chosen by the STATIC type)
```

### SECTION 2: protected vs private
`energy_` is `protected` in `Animal`: `Dog::run()` may change it, `main` may not. The base's `private` members (such as `name_`) are not accessible in `Dog` at all, which is why `Dog` uses the public `name()` accessor. `public` inheritance means "a Dog IS an Animal" (the interface carries through); private/protected inheritance exist but are rare.

Output from a real run:

```text
===== SECTION 2: protected vs private =====
after run(): energy = 7 (Dog changed the protected base member)
d.energy_ from main would not compile (protected).
```

### SECTION 3: slicing
`Animal sliced = d;` is legal and compiles without warning: it copy-constructs an `Animal` from the Animal part of `d`. The breed is gone, because an `Animal` has no space for it (sizeof shows 40 vs 72 bytes on this machine; those numbers are platform-specific). The same happens when passing by value and when storing objects in a `vector<Animal>`. The fix: pass by reference or pointer, store pointers/smart pointers, and (next file) use virtual functions. The demo uses a vector of non-owning `const Animal*`, which keeps the real Dog intact. The last note warns that OWNING Dogs through `unique_ptr<Animal>` needs a virtual destructor; the first draft of this file did exactly that, and AddressSanitizer reported a new-delete-type-mismatch, which is a nice proof that the rule is real.

Output from a real run:

```text
===== SECTION 3: slicing =====
sizeof(Animal) = 40, sizeof(Dog) = 72 (Dog is larger: extra breed_)
Animal sliced = d;  sliced.describe() = Animal named Rex
the breed is gone: there is nowhere in an Animal to store it.
takeByValue(d) = Animal named Rex (sliced copy)
takeByRef(d)   = Animal named Rex (no slicing, but still the base function)
vector<Animal> holding a Dog: size of stored element = 40 bytes (Animal-sized)
vector<const Animal*> view: the Dog is still whole, breed = Beagle (static_cast is safe here; virtual functions, next file, remove the need for it)
NOTE: owning a Dog through unique_ptr<Animal> would need a virtual destructor in Animal (see next file).
```

## Key Differences From Java
| Java | C++ |
|---|---|
| `class Dog extends Animal` | `class Dog : public Animal` (without `public` you get private inheritance) |
| All instance methods are virtual by default | Methods are NON-virtual by default; must write `virtual` |
| `super(name)` first line of constructor | Base constructor named in the initializer list |
| Variables are references; no slicing | Object variables hold the value; copying to a base type slices |
| Single inheritance (+ interfaces) | Multiple inheritance allowed |
| `protected` also grants package access | `protected` = derived classes only |

## Key Rules / Gotchas Recap
- Base constructor first, derived second; destruction in reverse.
- Non-virtual functions are bound by the static type; a same-named function in the derived class hides, it does not override.
- Slicing: never pass or store polymorphic objects by value in a base-typed container.
- Use `public` inheritance only for true "is-a" relationships.
- Polymorphic base classes need a virtual destructor (next file).

## Why This Structure Exists
Understanding that an object contains its base explains object layout, copy behavior and ABI issues in real libraries. Slicing bugs show up in plugin systems and message handlers in security and ML-serving code, where a derived message silently loses fields.
