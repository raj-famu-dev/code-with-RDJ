// Reference file generated with Claude (Sonnet 5.5). To be retyped, broken and explained by RDJ before this topic is marked complete.
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

public class _5_CsvAndJson {

    record Person(String name, int age, String city) { }

    static void deleteTree(Path root) throws IOException {
        try (Stream<Path> walk = Files.walk(root)) {
            for (Path p : walk.sorted(Comparator.reverseOrder()).toList()) {
                Files.delete(p);
            }
        }
    }

    // ============================================
    // PART 1: CSV
    // "Comma-separated values". It looks trivial, and line.split(",") is the classic
    // WRONG answer, because a field may CONTAIN a comma, a quote, or a newline.
    // The rules (RFC 4180): such a field is wrapped in double quotes, and a quote
    // inside it is written as two quotes.      "Smith, John"    "He said ""hi"""
    // ============================================

    static String escapeCsv(String field) {
        if (field.contains(",") || field.contains("\"") || field.contains("\n")) {
            return "\"" + field.replace("\"", "\"\"") + "\"";
        }
        return field;
    }

    static String toCsvLine(String... fields) {
        List<String> parts = new ArrayList<>();
        for (String f : fields) {
            parts.add(escapeCsv(f));
        }
        return String.join(",", parts);
    }

    // A small parser for ONE line (no newlines inside quoted fields, to stay short)
    static List<String> parseCsvLine(String line) {
        List<String> fields = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        boolean inQuotes = false;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (inQuotes) {
                if (c == '"') {
                    if (i + 1 < line.length() && line.charAt(i + 1) == '"') {
                        current.append('"');                       // "" inside quotes = one literal quote
                        i++;
                    } else {
                        inQuotes = false;                          // closing quote
                    }
                } else {
                    current.append(c);
                }
            } else if (c == '"') {
                inQuotes = true;
            } else if (c == ',') {
                fields.add(current.toString());
                current.setLength(0);
            } else {
                current.append(c);
            }
        }
        fields.add(current.toString());
        return fields;
    }

    // ============================================
    // PART 2: JSON (WRITING)
    // JSON values: object {}, array [], string "", number, true/false, null.
    // Writing it by hand means getting the ESCAPING right: " \ and control characters.
    // ============================================

    static String jsonString(String s) {
        StringBuilder sb = new StringBuilder("\"");
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\n' -> sb.append("\\n");
                case '\t' -> sb.append("\\t");
                default -> {
                    if (c < 0x20) {
                        sb.append(String.format("\\u%04x", (int) c));
                    } else {
                        sb.append(c);
                    }
                }
            }
        }
        return sb.append('"').toString();
    }

    static String toJson(List<Person> people) {
        StringBuilder sb = new StringBuilder("[\n");
        for (int i = 0; i < people.size(); i++) {
            Person p = people.get(i);
            sb.append("  {\"name\": ").append(jsonString(p.name()))
                    .append(", \"age\": ").append(p.age())
                    .append(", \"city\": ").append(jsonString(p.city())).append('}');
            sb.append(i < people.size() - 1 ? ",\n" : "\n");
        }
        return sb.append("]").toString();
    }

    // ============================================
    // PART 3: JSON (READING) - A TINY PARSER FOR FLAT OBJECTS
    // Handles: an array of flat objects whose values are strings or integers.
    // That is ALL it does, on purpose. Real JSON needs a library (see the end).
    // ============================================

    static class MiniJsonParser {
        private final String text;
        private int pos;

        MiniJsonParser(String text) {
            this.text = text;
        }

        List<Map<String, Object>> parseArrayOfObjects() {
            List<Map<String, Object>> result = new ArrayList<>();
            skipSpaces();
            expect('[');
            skipSpaces();
            if (peek() == ']') {
                pos++;
                return result;
            }
            while (true) {
                result.add(parseObject());
                skipSpaces();
                if (peek() == ',') {
                    pos++;
                    continue;
                }
                expect(']');
                return result;
            }
        }

        private Map<String, Object> parseObject() {
            Map<String, Object> map = new LinkedHashMap<>();
            skipSpaces();
            expect('{');
            skipSpaces();
            while (peek() != '}') {
                skipSpaces();
                String key = parseString();
                skipSpaces();
                expect(':');
                skipSpaces();
                Object value = peek() == '"' ? parseString() : parseInt();
                map.put(key, value);
                skipSpaces();
                if (peek() == ',') {
                    pos++;
                }
                skipSpaces();
            }
            expect('}');
            return map;
        }

        private String parseString() {
            expect('"');
            StringBuilder sb = new StringBuilder();
            while (peek() != '"') {
                char c = text.charAt(pos++);
                if (c == '\\') {
                    char next = text.charAt(pos++);
                    switch (next) {
                        case 'n' -> sb.append('\n');
                        case 't' -> sb.append('\t');
                        case '"' -> sb.append('"');
                        case '\\' -> sb.append('\\');
                        default -> throw error("unsupported escape \\" + next);
                    }
                } else {
                    sb.append(c);
                }
            }
            pos++;                                                 // closing quote
            return sb.toString();
        }

        private Integer parseInt() {
            int start = pos;
            if (peek() == '-') pos++;
            while (pos < text.length() && Character.isDigit(text.charAt(pos))) pos++;
            if (start == pos) throw error("expected a number");
            return Integer.parseInt(text.substring(start, pos));
        }

        private char peek() {
            if (pos >= text.length()) throw error("unexpected end of input");
            return text.charAt(pos);
        }

        private void expect(char c) {
            if (peek() != c) throw error("expected '" + c + "' but found '" + peek() + "'");
            pos++;
        }

        private void skipSpaces() {
            while (pos < text.length() && Character.isWhitespace(text.charAt(pos))) pos++;
        }

        private IllegalArgumentException error(String message) {
            return new IllegalArgumentException(message + " at position " + pos);
        }
    }

    public static void main(String[] args) throws IOException {

        List<Person> people = List.of(
                new Person("Ada Lovelace", 36, "London"),
                new Person("Smith, John", 41, "New York, NY"),       // commas inside fields
                new Person("Grace \"Amazing\" Hopper", 85, "Arlington"));   // quotes inside a field

        Path dir = Files.createTempDirectory("rdj-csvjson-");
        try {

            // ---------- CSV: write ----------
            Path csv = dir.resolve("people.csv");
            List<String> csvLines = new ArrayList<>();
            csvLines.add(toCsvLine("name", "age", "city"));
            for (Person p : people) {
                csvLines.add(toCsvLine(p.name(), String.valueOf(p.age()), p.city()));
            }
            Files.write(csv, csvLines);
            System.out.println("--- people.csv ---");
            Files.readAllLines(csv).forEach(System.out::println);

            // ---------- CSV: the naive way breaks ----------
            String tricky = Files.readAllLines(csv).get(2);        // the "Smith, John" row
            System.out.println("naive split(\",\") gives " + tricky.split(",").length + " fields (should be 3)");
            System.out.println("parseCsvLine gives  " + parseCsvLine(tricky).size() + " fields: " + String.join(" | ", parseCsvLine(tricky)));

            // ---------- CSV: read back into objects ----------
            List<Person> readBack = new ArrayList<>();
            List<String> lines = Files.readAllLines(csv);
            for (String line : lines.subList(1, lines.size())) {   // skip the header row
                List<String> f = parseCsvLine(line);
                readBack.add(new Person(f.get(0), Integer.parseInt(f.get(1)), f.get(2)));
            }
            System.out.println("CSV round trip equal: " + readBack.equals(people));

            // ---------- JSON: write ----------
            Path json = dir.resolve("people.json");
            Files.writeString(json, toJson(people));
            System.out.println("--- people.json ---");
            System.out.println(Files.readString(json));

            // ---------- JSON: read ----------
            List<Map<String, Object>> parsed = new MiniJsonParser(Files.readString(json)).parseArrayOfObjects();
            List<Person> fromJson = new ArrayList<>();
            for (Map<String, Object> m : parsed) {
                fromJson.add(new Person((String) m.get("name"), (Integer) m.get("age"), (String) m.get("city")));
            }
            System.out.println("JSON round trip equal: " + fromJson.equals(people));

            // ---------- JSON: bad input fails loudly ----------
            try {
                new MiniJsonParser("[{\"name\": }]").parseArrayOfObjects();
            } catch (IllegalArgumentException e) {
                System.out.println("malformed JSON rejected: " + e.getMessage());
            }

        } finally {
            deleteTree(dir);
        }

        // ============================================
        // WHEN TO USE A LIBRARY
        // This hand-written code is for LEARNING. It cannot do nested objects, arrays inside
        // objects, decimals, booleans, null, or unicode escapes in input. In real projects:
        //   JSON -> Jackson (or Gson)       CSV -> Apache Commons CSV (or OpenCSV)
        // Both are normal dependencies in Maven/Gradle (see 12-build-tools).
        // The rules you learned here (escaping, quoting, round-trip tests) still apply.
        // ============================================
    }
}
