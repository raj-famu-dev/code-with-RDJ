// Tags: #Cpp #Pointers #MemoryManagement #SmartPointers | @rdj_369 | C++20 (g++ 13)
// Completed and verified (g++ 13, -std=c++20). Written with Claude (Sonnet 5.5); authorship disclosed.
/*
 * _6_SmartPointers
 * Teaches: unique_ptr (sole owner), shared_ptr (shared ownership with a
 * reference count shown by use_count), weak_ptr (non-owning observer that
 * breaks cycles), and make_unique / make_shared.
 */
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

struct Widget {
    std::string name;
    explicit Widget(std::string n) : name(std::move(n)) { std::cout << "  [Widget " << name << " created]\n"; }
    ~Widget() { std::cout << "  [Widget " << name << " destroyed]\n"; }
};

// Cycle demo types: each holds the other by shared_ptr => neither can ever reach count 0.
struct BadNode {
    std::string name;
    std::shared_ptr<BadNode> other;
    explicit BadNode(std::string n) : name(std::move(n)) {}
    ~BadNode() { std::cout << "  [BadNode " << name << " destroyed]\n"; }
};
// Fixed: the back-link is a weak_ptr (observes, does not own).
struct GoodNode {
    std::string name;
    std::shared_ptr<GoodNode> next;
    std::weak_ptr<GoodNode> prev;
    explicit GoodNode(std::string n) : name(std::move(n)) {}
    ~GoodNode() { std::cout << "  [GoodNode " << name << " destroyed]\n"; }
};

void take_ownership(std::unique_ptr<Widget> w) { std::cout << "  callee owns " << w->name << " and will destroy it\n"; }
void just_use(const Widget& w) { std::cout << "  callee only borrows " << w.name << '\n'; }

int main() {
    std::cout << "===== SECTION 1: unique_ptr (SOLE OWNER) =====\n";
    {
        auto w = std::make_unique<Widget>("U1");      // prefer make_unique over new
        std::cout << "  using it: " << w->name << '\n';
        just_use(*w);                                 // lend with a reference, keep ownership
        auto moved = std::move(w);                    // copying is deleted; moving transfers ownership
        std::cout << "  after move, original is " << (w ? "valid" : "null") << '\n';
        // auto copy = moved;                         // ERROR: unique_ptr is not copyable
        take_ownership(std::move(moved));             // destroyed when callee returns
        std::cout << "  back in caller\n";
    }
    auto arr = std::make_unique<int[]>(3);            // array form, delete[] handled for you
    arr[0] = 5;
    std::cout << "  unique_ptr<int[]> arr[0] = " << arr[0] << ", arr[1] = " << arr[1] << " (make_unique value-initialises)\n";

    std::cout << "\n===== SECTION 2: shared_ptr AND use_count =====\n";
    {
        auto a = std::make_shared<Widget>("S1");
        std::cout << "  use_count after creation: " << a.use_count() << '\n';
        {
            auto b = a;                               // copy: count goes up
            std::vector<std::shared_ptr<Widget>> list{a, b};
            std::cout << "  use_count with b and a 2-element vector: " << a.use_count() << '\n';
        }
        std::cout << "  use_count after the inner scope: " << a.use_count() << '\n';
        std::cout << "  leaving scope: last owner releases it\n";
    }
    // Trap: do not make two shared_ptrs from the same raw pointer; each would think it is the sole owner.
    //   Widget* raw = new Widget("X"); std::shared_ptr<Widget> p1(raw), p2(raw);  // double delete
    // Always copy a shared_ptr, never rebuild one from a raw pointer.

    std::cout << "\n===== SECTION 3: weak_ptr =====\n";
    std::weak_ptr<Widget> observer;
    {
        auto strong = std::make_shared<Widget>("W1");
        observer = strong;
        std::cout << "  use_count (weak does not count): " << strong.use_count() << '\n';
        if (auto locked = observer.lock()) std::cout << "  lock() succeeded, name = " << locked->name << '\n';
    }
    std::cout << "  expired after owner died: " << std::boolalpha << observer.expired() << '\n';
    if (!observer.lock()) std::cout << "  lock() now returns null, so the check is mandatory\n";

    std::cout << "\n===== SECTION 4: A REFERENCE CYCLE LEAKS (TRAP) =====\n";
    {
        // To keep the whole program leak-free, we break the bad cycle by hand at the end of the scope.
        auto x = std::make_shared<BadNode>("x");
        auto y = std::make_shared<BadNode>("y");
        x->other = y;
        y->other = x;
        std::cout << "  x use_count = " << x.use_count() << ", y use_count = " << y.use_count() << " (each held by the other)\n";
        std::cout << "  if we just left the scope, neither destructor would run: a leak\n";
        x->other.reset();                             // manual cycle break so this demo stays clean
        std::cout << "  broke the cycle manually; now leaving scope\n";
    }

    std::cout << "\n===== SECTION 5: FIX WITH weak_ptr =====\n";
    {
        auto head = std::make_shared<GoodNode>("head");
        auto tail = std::make_shared<GoodNode>("tail");
        head->next = tail;                            // owning forward link
        tail->prev = head;                            // non-owning back link
        std::cout << "  head use_count = " << head.use_count() << ", tail use_count = " << tail.use_count() << '\n';
        std::cout << "  leaving scope: both destructors run (no leak)\n";
    }
    std::cout << "\nRule: default to unique_ptr; use shared_ptr only for true shared ownership; use weak_ptr for back-references.\n";
    return 0;
}
