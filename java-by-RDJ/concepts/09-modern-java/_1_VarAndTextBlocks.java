// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class _1_VarAndTextBlocks {

    public static void main(String[] args) {

        // ============================================
        // SECTION 1: var - LOCAL VARIABLE TYPE INFERENCE (Java 10)
        // The compiler works out the type from the right-hand side. The variable is
        // STILL statically typed: var is not "dynamic typing" and not JavaScript's var.
        // ============================================

        var count = 10;                                            // int
        var name = "Ada";                                          // String
        var prices = new ArrayList<Double>();                      // ArrayList<Double>
        prices.add(9.99);
        System.out.println("count is " + ((Object) count).getClass().getSimpleName()
                + ", name is " + name.getClass().getSimpleName()
                + ", prices is " + prices.getClass().getSimpleName());
        // count = "text";                                         // COMPILE ERROR: count is an int, forever


        // ============================================
        // SECTION 2: WHERE var HELPS
        // The type is already obvious or very long: less noise.
        // ============================================

        Map<String, List<Integer>> verbose = new HashMap<String, List<Integer>>();   // type written twice
        var concise = new HashMap<String, List<Integer>>();                           // same type, written once
        concise.computeIfAbsent("scores", k -> new ArrayList<>()).add(90);
        System.out.println("concise: " + concise);

        for (var entry : concise.entrySet()) {                     // entry is Map.Entry<String, List<Integer>>
            System.out.println("entry key = " + entry.getKey());
        }
        System.out.println("verbose map is empty: " + verbose.isEmpty());


        // ============================================
        // SECTION 3: WHERE var HURTS
        // When the reader cannot tell the type from the line, or you change the type by accident.
        // ============================================

        // var result = compute();                                 // what type is this? Click-through needed.
        // var x = 1;                                              // int... but you probably wanted long?
        var bigger = 1;                                            // int, NOT long
        long wanted = 1;                                           // say what you mean
        System.out.println("var bigger = 1 is " + ((Object) bigger).getClass().getSimpleName()
                + "; explicit long is " + ((Object) wanted).getClass().getSimpleName());

        // var list = new ArrayList<>();                           // ArrayList<Object>: the diamond has nothing to infer from
        var objectList = new ArrayList<>();
        objectList.add(1);
        objectList.add("mixed");                                   // compiles: the list holds Objects
        System.out.println("var with an empty diamond gives ArrayList<Object>: " + objectList);

        // Things var CANNOT do:
        // var a;                                                  // COMPILE ERROR: no initializer, nothing to infer
        // var b = null;                                           // COMPILE ERROR: null has no type
        // var f = () -> 1;                                        // COMPILE ERROR: a lambda needs a target type
        // var arr = {1, 2, 3};                                    // COMPILE ERROR: array initializer needs a type
        // Also: var works only for LOCAL variables, never for fields, parameters or return types.

        // Naming matters more with var:
        // var data = load();      // vague
        // var customers = load(); // the NAME carries the meaning the type no longer shows


        // ============================================
        // SECTION 4: TEXT BLOCKS (Java 15) - MULTI-LINE STRINGS
        // Start with three quotes and a NEWLINE; end with three quotes.
        // No more "\n" and "\"" noise for JSON, SQL, HTML.
        // ============================================

        String json = """
                {
                  "name": "Ada",
                  "role": "engineer"
                }
                """;
        System.out.print("text block:\n" + json);

        String oldWay = "{\n  \"name\": \"Ada\",\n  \"role\": \"engineer\"\n}\n";
        System.out.println("same content as the old escaped string: " + json.equals(oldWay));


        // ============================================
        // SECTION 5: HOW INDENTATION IS DECIDED
        // The compiler removes the COMMON leading whitespace of all lines, including
        // the closing """ line. Move the closing """ left and you keep more indentation.
        // ============================================

        String indented = """
                level 0
                  level 1
                    level 2
                """;
        System.out.print(indented);

        String keepsIndent = """
                kept four spaces
            """;                                                   // closing delimiter is 4 spaces further left
        System.out.print("[" + keepsIndent.replace("\n", "") + "]\n");


        // ============================================
        // SECTION 6: ESCAPES SPECIAL TO TEXT BLOCKS
        //   \   at the end of a line : join with the next line (no newline)
        //   \s                       : a space that is NOT stripped (trailing spaces are otherwise removed)
        //   \"""                     : a literal triple quote
        // ============================================

        String oneLine = """
                this long sentence is written over \
                two source lines but is one line.""";
        System.out.println(oneLine);

        String padded = """
                abc\s\s
                """;
        System.out.println("trailing spaces kept with \\s: [" + padded.stripTrailing().length() + " vs " + padded.length() + " chars incl. newline]");


        // ============================================
        // SECTION 7: formatted() - FILLING IN VALUES
        // ============================================

        String template = """
                Hello, %s!
                You have %d new messages.
                """.formatted("Ada", 3);
        System.out.print(template);

        // ============================================
        // SECTION 8: A HONEST RULE FOR BOTH
        // var: use when the type is obvious from the right-hand side. Spell it out when it is not.
        // Text blocks: use for anything multi-line (JSON, SQL, HTML). Never build SQL by gluing user
        // input into a text block: that is still SQL injection (see 10-jdbc-sql).
        // ============================================
    }
}
