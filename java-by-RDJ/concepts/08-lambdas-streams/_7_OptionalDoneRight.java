// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Optional;

public class _7_OptionalDoneRight {

    record User(String name, String email) { }

    static class UserRepository {
        private final List<User> users = List.of(
                new User("ada", "ada@example.com"),
                new User("linus", null));                          // a user with no email on purpose

        // GOOD USE: a method that might not find anything says so in its RETURN TYPE
        Optional<User> findByName(String name) {
            return users.stream().filter(u -> u.name().equals(name)).findFirst();
        }
    }

    // The old way: null is the signal. Nothing in the signature warns the caller.
    static String findEmailOld(UserRepository repo, String name) {
        Optional<User> user = repo.findByName(name);
        if (user.isPresent()) {
            String email = user.get().email();
            if (email != null) {
                return email;
            }
        }
        return "no-email@unknown";
    }

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: WHAT Optional<T> IS FOR
        // A container that holds either one value or nothing. Its purpose is to make
        // "this result may be absent" part of a method's SIGNATURE, so callers cannot forget.
        // ============================================

        UserRepository repo = new UserRepository();

        Optional<User> found = repo.findByName("ada");
        Optional<User> missing = repo.findByName("nobody");
        System.out.println("found:   " + found);
        System.out.println("missing: " + missing);
        System.out.println("found.isPresent(): " + found.isPresent() + ", missing.isEmpty(): " + missing.isEmpty());


        // ============================================
        // SECTION 2: CREATING ONE
        // ============================================

        Optional<String> a = Optional.of("value");                 // value must NOT be null
        Optional<String> b = Optional.ofNullable(null);            // null becomes an empty Optional
        Optional<String> c = Optional.empty();
        System.out.println("of / ofNullable(null) / empty: " + a + ", " + b + ", " + c);
        try {
            Optional.of(null);                                     // of() refuses null
        } catch (NullPointerException e) {
            System.out.println("Optional.of(null) -> NullPointerException (use ofNullable)");
        }


        // ============================================
        // SECTION 3: GETTING THE VALUE OUT - THE GOOD WAYS
        // ============================================

        System.out.println("orElse:        " + missing.map(User::name).orElse("default-name"));
        System.out.println("orElseGet:     " + missing.map(User::name).orElseGet(() -> "computed-" + 42));
        try {
            missing.orElseThrow(() -> new NoSuchElementException("user not found"));
        } catch (NoSuchElementException e) {
            System.out.println("orElseThrow:   " + e.getMessage());
        }
        // orElse(x) always BUILDS x, even when the Optional has a value.
        // orElseGet(supplier) only runs the supplier when it is needed: use it for anything costly.


        // ============================================
        // SECTION 4: THE BAD WAY - get() WITHOUT CHECKING
        // ============================================

        try {
            missing.get();                                         // throws if empty
        } catch (NoSuchElementException e) {
            System.out.println("get() on empty -> NoSuchElementException: " + e.getMessage());
        }
        // isPresent() + get() is just a null check in disguise. Prefer map/orElse/ifPresent.


        // ============================================
        // SECTION 5: TRANSFORMING WITHOUT UNWRAPPING
        // map: apply a function if present.   flatMap: the function itself returns an Optional.
        // filter: keep the value only if it passes a test.
        // ============================================

        System.out.println("map:        " + found.map(User::name).map(String::toUpperCase));
        System.out.println("map on empty: " + missing.map(User::name));

        // email() may be null. map treats a null result as empty, so no NullPointerException:
        Optional<String> linusEmail = repo.findByName("linus").map(User::email);
        System.out.println("linus has no email -> " + linusEmail);

        Optional<User> withEmail = repo.findByName("ada").filter(u -> u.email() != null);
        System.out.println("filter: " + withEmail.isPresent());

        System.out.println("whole chain with a default: "
                + repo.findByName("linus").map(User::email).orElse("no-email@unknown"));
        System.out.println("same result the old way:    " + findEmailOld(repo, "linus"));


        // ============================================
        // SECTION 6: DOING SOMETHING ONLY IF PRESENT
        // ============================================

        found.ifPresent(u -> System.out.println("ifPresent ran for " + u.name()));
        missing.ifPresentOrElse(
                u -> System.out.println("not printed"),
                () -> System.out.println("ifPresentOrElse: nothing found"));
        System.out.println("or(): " + missing.or(() -> Optional.of(new User("guest", "none"))).get().name());


        // ============================================
        // SECTION 7: WHERE NOT TO USE Optional
        // - NOT as a field in a class or entity (it is not Serializable and adds overhead).
        // - NOT as a method PARAMETER (callers must wrap values for no benefit).
        // - NOT inside collections: use an empty list instead of Optional<List<..>>,
        //   and never return null for a collection.
        // - NOT as a replacement for a simple null check on a local variable.
        // - NEVER set an Optional variable to null.
        // Rule of thumb: Optional is for RETURN TYPES where "no result" is a normal outcome.
        // ============================================


        // ============================================
        // SECTION 8: PRIMITIVE VERSIONS
        // OptionalInt, OptionalDouble: what stream terminals like max(), average() return.
        // ============================================

        System.out.println("average of an empty list: " + java.util.stream.IntStream.empty().average());
        System.out.println("max of 3,9,4: " + java.util.stream.IntStream.of(3, 9, 4).max().getAsInt());
    }
}
