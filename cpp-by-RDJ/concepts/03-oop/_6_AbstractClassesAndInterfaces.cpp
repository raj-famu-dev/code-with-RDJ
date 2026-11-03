// Tags: #Cpp #OOP #AbstractClassesInterfaces | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Teaches: pure virtual functions (`= 0`), abstract classes that cannot be
 * instantiated, interface-style classes (only pure virtuals + virtual
 * destructor), a pure virtual WITH a body, and multiple interface
 * implementation (the C++ way to do what Java interfaces do).
 */
#include <iostream>
#include <memory>
#include <string>
#include <type_traits>
#include <vector>

// ===== SECTION 1: interface-style class =====
class IPrintable {                                   // "I" prefix is a convention, not a keyword
public:
    virtual ~IPrintable() = default;
    virtual std::string print() const = 0;
};
class IComparableById {
public:
    virtual ~IComparableById() = default;
    virtual int id() const = 0;
    bool sameIdAs(const IComparableById& o) const { return id() == o.id(); }   // non-virtual helper: allowed (unlike classic Java 7 interfaces)
};

// ===== SECTION 2: abstract class with state =====
class Employee : public IPrintable, public IComparableById {   // implements TWO interfaces
public:
    Employee(int id, std::string name) : name_(std::move(name)), id_(id) {}
    int id() const override { return id_; }
    std::string print() const override { return "Employee#" + std::to_string(id_) + " " + name_ + " pays " + std::to_string(pay()); }
    virtual int pay() const = 0;                     // pure virtual: subclasses MUST supply
protected:
    std::string name_;
private:
    int id_;
};
class Salaried : public Employee {
public:
    Salaried(int id, std::string n, int annual) : Employee(id, std::move(n)), annual_(annual) {}
    int pay() const override { return annual_ / 12; }
private:
    int annual_;
};
class Hourly : public Employee {
public:
    Hourly(int id, std::string n, int rate, int hours) : Employee(id, std::move(n)), rate_(rate), hours_(hours) {}
    int pay() const override { return rate_ * hours_; }
private:
    int rate_, hours_;
};
class Incomplete : public Employee {                 // forgot pay(): still abstract
public:
    Incomplete() : Employee(0, "none") {}
};

// ===== SECTION 3: pure virtual with a body =====
class Logger {
public:
    virtual ~Logger() = default;
    virtual void log(const std::string& m) const = 0;
};
void Logger::log(const std::string& m) const { std::cout << "  [default log] " << m << "\n"; }   // pure, yet defined
class ConsoleLogger : public Logger {
public:
    void log(const std::string& m) const override { Logger::log("console says: " + m); }          // reuse the default body
};

// ===== SECTION 4: programming against the interface =====
void printAll(const std::vector<std::unique_ptr<Employee>>& staff) {
    for (const auto& e : staff) std::cout << "  " << e->print() << "\n";
}

int main() {
    std::cout << "===== SECTION 1: interface-style class =====\n";
    std::cout << "is_abstract<IPrintable>: " << std::boolalpha << std::is_abstract_v<IPrintable> << "\n";
    std::cout << "`IPrintable p;` would not compile: cannot instantiate an abstract class.\n";
    std::cout << "is_polymorphic<IPrintable>: " << std::is_polymorphic_v<IPrintable> << "\n";

    std::cout << "\n===== SECTION 2: abstract class with state =====\n";
    std::cout << "is_abstract<Employee>: " << std::is_abstract_v<Employee> << "\n";
    std::cout << "is_abstract<Salaried>: " << std::is_abstract_v<Salaried> << "\n";
    std::cout << "is_abstract<Incomplete>: " << std::is_abstract_v<Incomplete> << " (forgot to override pay(), so still abstract; `Incomplete x;` would not compile)\n";
    std::vector<std::unique_ptr<Employee>> staff;
    staff.push_back(std::make_unique<Salaried>(1, "Ana", 120000));
    staff.push_back(std::make_unique<Hourly>(2, "Ben", 20, 80));
    printAll(staff);
    std::cout << "sameIdAs: " << staff[0]->sameIdAs(*staff[1]) << " (ids 1 vs 2)\n";
    const IPrintable& asPrintable = *staff[1];
    std::cout << "via IPrintable& only: " << asPrintable.print() << "\n";

    std::cout << "\n===== SECTION 3: pure virtual with a body =====\n";
    ConsoleLogger cl;
    cl.log("hello");
    std::cout << "A pure virtual may still have a definition; derived classes must override it but may call it explicitly.\n";

    std::cout << "\n===== SECTION 4: the memory cost of interfaces =====\n";
    std::cout << "sizeof(IPrintable) = " << sizeof(IPrintable) << " (only the hidden vptr; no data)\n";
    std::cout << "sizeof(Employee) = " << sizeof(Employee) << " (two vptrs for two bases + data)\n";
    std::cout << "Employee has two vptrs because it inherits from two polymorphic bases (multiple inheritance).\n";
    return 0;
}
