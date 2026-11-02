// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InvalidClassException;
import java.io.InvalidObjectException;
import java.io.NotSerializableException;
import java.io.ObjectInputFilter;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serial;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class _6_SerializationAndItsDangers {

    // ============================================
    // SECTION 1: WHAT SERIALIZATION IS
    // Turning an object (and everything it references) into bytes, and back.
    // A class opts in by implementing the marker interface Serializable (no methods).
    // ============================================

    static class Address implements Serializable {
        @Serial
        private static final long serialVersionUID = 1L;
        final String city;

        Address(String city) {
            this.city = city;
        }
    }

    static class User implements Serializable {
        // serialVersionUID is a VERSION STAMP for the class layout. If the stored bytes have a
        // different stamp than the current class, deserializing fails with InvalidClassException.
        @Serial
        private static final long serialVersionUID = 1L;

        final String name;
        final Address address;                                     // referenced objects must be Serializable too
        final transient String password;                           // transient = NEVER written to the bytes
        int age;

        User(String name, int age, Address address, String password) {
            this.name = name;
            this.age = age;
            this.address = address;
            this.password = password;
            System.out.println("    (constructor ran for " + name + ")");
        }

        // ============================================
        // SECTION 5: VALIDATE ON THE WAY IN
        // Deserialization does NOT call a constructor, so your constructor's checks
        // are skipped. Re-check invariants in readObject, or the object can be invalid.
        // ============================================
        @Serial
        private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException {
            in.defaultReadObject();
            if (age < 0) {
                throw new InvalidObjectException("age cannot be negative");
            }
        }
    }

    static class NotSerializableThing {
        int x = 1;
    }

    static class Holder implements Serializable {
        @Serial
        private static final long serialVersionUID = 1L;
        final NotSerializableThing inner = new NotSerializableThing();   // this will break serialization
    }

    static byte[] serialize(Object o) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        try (ObjectOutputStream out = new ObjectOutputStream(bytes)) {
            out.writeObject(o);
        }
        return bytes.toByteArray();
    }

    static Object deserialize(byte[] data) throws IOException, ClassNotFoundException {
        try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(data))) {
            return in.readObject();
        }
    }

    public static void main(String[] args) throws Exception {

        // ============================================
        // SECTION 2: A ROUND TRIP (done in memory with byte arrays; the same works with files)
        // ============================================

        User original = new User("ada", 36, new Address("London"), "s3cret");
        byte[] bytes = serialize(original);
        System.out.println("serialized to " + bytes.length + " bytes");

        System.out.println("deserializing:");
        User copy = (User) deserialize(bytes);                     // NO "(constructor ran...)" line appears
        System.out.println("name = " + copy.name + ", age = " + copy.age + ", city = " + copy.address.city);
        System.out.println("same object? " + (copy == original) + " (a different object with equal content)");
        System.out.println("transient password after reading: " + copy.password + "  (never saved)");


        // ============================================
        // SECTION 3: NOT EVERYTHING CAN BE SERIALIZED
        // ============================================

        try {
            serialize(new Holder());
        } catch (NotSerializableException e) {
            System.out.println("NotSerializableException: " + e.getMessage().replace("_6_SerializationAndItsDangers$", ""));
        }


        // ============================================
        // SECTION 4: VALIDATION IS SKIPPED, SO readObject MUST CHECK
        // We forge a negative age by changing the live object before saving it
        // (age is a normal field). Our readObject then rejects the bytes.
        // ============================================

        User bad = new User("eve", 20, new Address("Paris"), "x");
        bad.age = -5;
        byte[] badBytes = serialize(bad);
        try {
            deserialize(badBytes);
        } catch (InvalidObjectException e) {
            System.out.println("readObject rejected the data: " + e.getMessage());
        }


        // ============================================
        // SECTION 6: THE DANGER - NEVER DESERIALIZE UNTRUSTED BYTES
        // ObjectInputStream will load whatever class the bytes name and run its
        // deserialization code BEFORE your cast. So the cast in
        //        (User) in.readObject()
        // happens too late to protect you. Attackers have used this for years to
        // take over servers (it is a well-known vulnerability class: CWE-502).
        // This file does NOT show an attack. The rules:
        //   1) Never deserialize data from outside your own trust boundary
        //      (network, uploads, cookies, user-supplied files).
        //   2) Prefer data formats such as JSON/CSV (_5) for exchanging data.
        //   3) If you must use Java serialization, set an ALLOW-LIST filter.
        // ============================================


        // ============================================
        // SECTION 7: DEFENCE - AN ObjectInputFilter ALLOW-LIST (Java 9+)
        // The pattern lists classes that may be read; "!*" rejects everything else.
        // The filter runs BEFORE objects are created.
        // ============================================

        ObjectInputFilter allowOnlyOurs = ObjectInputFilter.Config.createFilter(
                "_6_SerializationAndItsDangers$User;_6_SerializationAndItsDangers$Address;java.lang.*;!*");

        try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(bytes))) {
            in.setObjectInputFilter(allowOnlyOurs);
            User ok = (User) in.readObject();
            System.out.println("filter allowed the expected classes: " + ok.name);
        }

        byte[] foreign = serialize(new ArrayList<>(List.of("a", "b")));   // an ArrayList is not on our allow-list
        try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(foreign))) {
            in.setObjectInputFilter(allowOnlyOurs);
            in.readObject();
        } catch (InvalidClassException e) {
            System.out.println("filter rejected an unexpected class: InvalidClassException");
        }


        // ============================================
        // SECTION 8: OTHER REASONS TO AVOID IT
        // - The byte format is tied to your class layout: change a field and old files may break.
        // - It exposes private fields; it is hard to evolve and hard to read from other languages.
        // - Modern Java teams use JSON, Protocol Buffers or a database instead.
        // ============================================
    }
}
