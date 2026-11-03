// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * Modern class features: = default and = delete, defaulted comparisons
 * (<=> and ==), designated initializers, enum class, using aliases, and
 * attributes such as [[nodiscard]], [[maybe_unused]] and [[deprecated]].
 */
#include <compare>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>

// ---------- = default and = delete ----------
class Account {
public:
    Account() = default;                          // ask the compiler to generate it
    explicit Account(std::string owner) : owner_(std::move(owner)) {}
    Account(const Account&) = delete;             // accounts must not be duplicated
    Account& operator=(const Account&) = delete;
    Account(Account&&) = default;                 // but they can be moved
    Account& operator=(Account&&) = default;
    ~Account() = default;
    const std::string& owner() const { return owner_; }

private:
    std::string owner_ = "nobody";                // default member initializer
};

// delete can also forbid unwanted overloads / conversions.
void take_int(int x) { std::cout << "take_int(" << x << ")\n"; }
void take_int(double) = delete;                   // no silent double -> int narrowing

// ---------- defaulted comparisons ----------
struct Version {
    int major = 0;
    int minor = 0;
    int patch = 0;
    auto operator<=>(const Version&) const = default;  // lexicographic over members, in order
    bool operator==(const Version&) const = default;
};

// ---------- designated initializers ----------
struct Config {
    std::string host = "localhost";
    int port = 80;
    bool verbose = false;
};

// ---------- enum class ----------
enum class Color { Red, Green, Blue };
enum class Level : unsigned char { Low = 1, High = 10 };  // explicit underlying type
enum OldColor { OLD_RED, OLD_GREEN };                     // classic enum for contrast

std::string name(Color c) {
    switch (c) {
        case Color::Red: return "Red";
        case Color::Green: return "Green";
        case Color::Blue: return "Blue";
    }
    return "?";
}

// ---------- using aliases ----------
using ScoreTable = std::map<std::string, std::vector<int>>;
template <class T> using Grid = std::vector<std::vector<T>>;

// ---------- attributes ----------
[[nodiscard]] int checked_divide(int a, int b) { return b == 0 ? 0 : a / b; }
[[deprecated("use checked_divide instead")]] int old_divide(int a, int b) { return a / b; }

int main() {
    std::cout << std::boolalpha;
    // ===== SECTION 1: = default AND = delete =====
    std::cout << "===== SECTION 1: = default AND = delete =====\n";
    Account a;
    Account b("raj");
    std::cout << "default-constructed owner: " << a.owner() << ", named owner: " << b.owner() << "\n";
    Account c = std::move(b);
    std::cout << "moved account owner: " << c.owner() << "\n";
    std::cout << "Account copy = delete: 'Account d = c;' is a COMPILE ERROR (try it).\n";
    take_int(5);
    std::cout << "take_int(2.5) is a COMPILE ERROR because the double overload is deleted.\n";

    // ===== SECTION 2: DEFAULTED COMPARISONS =====
    std::cout << "===== SECTION 2: DEFAULTED COMPARISONS =====\n";
    Version v1{1, 2, 3}, v2{1, 10, 0}, v3{1, 2, 3};
    std::cout << "v1 == v3: " << (v1 == v3) << "\n";
    std::cout << "v1 < v2:  " << (v1 < v2) << "  (minor 2 < 10; member order decides)\n";
    std::cout << "v2 >= v1: " << (v2 >= v1) << "\n";
    auto cmp = v1 <=> v2;
    std::cout << "(v1 <=> v2) < 0: " << (cmp < 0) << "\n";
    std::set<Version> versions = {v2, v1, v3};
    std::cout << "std::set<Version> size (v1 and v3 equal): " << versions.size() << ", smallest is "
              << versions.begin()->major << "." << versions.begin()->minor << "." << versions.begin()->patch << "\n";
    std::cout << "TRAP: the order of the data members IS the comparison order. Reordering fields changes behaviour.\n";

    // ===== SECTION 3: DESIGNATED INITIALIZERS =====
    std::cout << "===== SECTION 3: DESIGNATED INITIALIZERS =====\n";
    Config c1{.host = "example.test", .port = 8080};
    Config c2{.verbose = true};
    std::cout << "c1: " << c1.host << ":" << c1.port << " verbose=" << c1.verbose << "\n";
    std::cout << "c2: " << c2.host << ":" << c2.port << " verbose=" << c2.verbose << " (unnamed fields use defaults)\n";
    std::cout << "TRAP: designators must appear in declaration order; {.port = 1, .host = \"x\"} does not compile in C++.\n";

    // ===== SECTION 4: enum class =====
    std::cout << "===== SECTION 4: enum class =====\n";
    Color col = Color::Green;
    std::cout << "name(Color::Green) = " << name(col) << "\n";
    std::cout << "underlying value: " << static_cast<int>(col) << " (conversion must be explicit)\n";
    Level lv = Level::High;
    std::cout << "Level::High underlying: " << static_cast<int>(lv) << ", sizeof(Level)=" << sizeof(Level) << "\n";
    int old_val = OLD_GREEN;  // classic enums convert silently and leak names into the enclosing scope
    std::cout << "classic enum OLD_GREEN converts silently to int: " << old_val << "\n";
    std::cout << "TRAP: 'int x = Color::Red;' and 'Color::Red == 0' do not compile; that is the point.\n";

    // ===== SECTION 5: using ALIASES =====
    std::cout << "===== SECTION 5: using ALIASES =====\n";
    ScoreTable table;
    table["ana"] = {90, 85};
    table["ben"] = {70};
    Grid<int> grid(2, std::vector<int>(3, 7));
    std::cout << "ScoreTable entries: " << table.size() << ", ana's scores: " << table["ana"].size() << "\n";
    std::cout << "Grid<int> is " << grid.size() << "x" << grid[0].size() << ", grid[1][2]=" << grid[1][2] << "\n";
    std::cout << "'using' replaces typedef and, unlike typedef, supports templates.\n";

    // ===== SECTION 6: ATTRIBUTES =====
    std::cout << "===== SECTION 6: ATTRIBUTES =====\n";
    int q = checked_divide(10, 2);  // result used: no warning
    std::cout << "checked_divide(10, 2) = " << q << "\n";
    std::cout << "TRAP: a bare 'checked_divide(1, 0);' triggers a [[nodiscard]] warning; deprecated old_divide warns when called.\n";
    [[maybe_unused]] int debug_only = 123;  // silences 'unused variable' where it is intentional
    int level = 2;
    switch (level) {
        case 1:
            std::cout << "level one\n";
            break;
        case 2:
            std::cout << "level two, falling through on purpose\n";
            [[fallthrough]];
        case 3:
            std::cout << "level three code also ran\n";
            break;
        default:
            break;
    }
    return 0;
}
