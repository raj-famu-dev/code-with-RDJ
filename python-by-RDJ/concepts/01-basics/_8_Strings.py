# ============================================
# TOPIC 8: STRINGS
# Strings are immutable in Python too - same core concept as Java.
# But Python strings have FAR more built-in methods, unique slicing
# syntax (recap from Topic 7), and some genuinely different rules
# around comparison and formatting.
# ============================================


# ============================================
# SECTION 1: CREATING STRINGS
# Single quotes and double quotes are 100% INTERCHANGEABLE -
# unlike Java, where double quotes are mandatory for Strings
# ============================================

greeting = "Hello"
name = 'RDJ'            # single quotes work exactly the same as double

print(greeting, name)

# Triple quotes for MULTI-LINE strings - no \n needed at all
multiline = """This spans
multiple lines
without any escape characters."""
print(multiline)

# Java needs text blocks (""") only since Java 15+, and even then
# the syntax rules are stricter. Python has supported this forever.


# ============================================
# SECTION 2: == COMPARES CONTENT DIRECTLY - NO STRING POOL CONFUSION
# This is a GENUINE relief coming from Java
# ============================================

str1 = "Java"
str2 = "Java"
str3 = "Jav" + "a"        # built at runtime, not a literal

print("str1 == str2:", str1 == str2)   # True - content comparison, as expected
print("str1 == str3:", str1 == str3)   # True - ALSO content comparison!

# Unlike Java, Python's == ALWAYS compares content for strings.
# There is NO equivalent to Java's "== compares references" trap at all.
# (Python DOES have 'is' for actual reference comparison - recap Topic 3 -
# but you almost never need it for strings specifically)


# ============================================
# SECTION 3: STRING CONCATENATION
# ============================================

full_greeting = greeting + ", " + name + "!"
print(full_greeting)

message = "Python"
message += " is"
message += " powerful"
print(message)

# Recap from Topic 2's gotcha: concatenating a STRING with a NUMBER
# using + still CRASHES - must convert explicitly
age = 25
# combined = "Age: " + age    # <-- CRASHES: TypeError
combined = "Age: " + str(age)   # str() required, same rule as before
print(combined)

# f-strings sidestep this entirely (recap from Topic 4) - no str() needed:
print(f"Age: {age}")


# ============================================
# SECTION 4: STRING IMMUTABILITY (SAME CONCEPT AS JAVA)
# ============================================

original = "Hello"
modified = original + " World"   # creates a NEW string - original is untouched

print("Original (unchanged):", original)
print("Modified (new string):", modified)

# original[0] = 'J'   # <-- CRASHES: TypeError: 'str' object does not support item assignment
# Strings cannot be modified in place AT ALL - not even a single character


# ============================================
# SECTION 5: COMMON STRING METHODS
# Many names are DIFFERENT from Java's equivalents - watch the
# naming carefully since they don't always map 1:1
# ============================================

sample = "  Python Programming  "

print("Length:", len(sample))              # len(), NOT sample.length()!
print("Stripped:", f"'{sample.strip()}'")  # .strip(), NOT .trim()!
print("Uppercase:", sample.strip().upper())    # .upper(), NOT .toUpperCase()
print("Lowercase:", sample.strip().lower())    # .lower(), NOT .toLowerCase()

word = "Python"
print("Character at index 0:", word[0])   # indexing directly - NO .charAt() method at all!
print("Character at index 3:", word[3])

sentence = "I love Python programming"
print("Index of 'Python':", sentence.find("Python"))      # .find(), NOT .indexOf()
print("Index of 'Java':", sentence.find("Java"))            # -1 if not found, same as Java

# .index() is similar to .find(), but CRASHES instead of returning -1:
# sentence.index("Java")   # <-- would raise ValueError if uncommented

print("Substring from index 7:", sentence[7:])             # SLICING replaces substring()!
print("Substring from 7 to 13:", sentence[7:13])            # end EXCLUSIVE, same rule as Java

replaced = sentence.replace("Python", "Java")
print("Replaced:", replaced)

print("Contains 'love':", "love" in sentence)    # 'in' keyword, NOT .contains()!

print("'PYTHON' == 'python':", "PYTHON" == "python")              # False - case-sensitive
print("Case-insensitive check:", "PYTHON".lower() == "python".lower())
# Python has NO .equalsIgnoreCase() - you lowercase both sides manually instead

print("Starts with 'I':", sentence.startswith("I"))
print("Ends with 'programming':", sentence.endswith("programming"))

empty_str = ""
blank_str = "   "
print("Is empty check:", empty_str == "")          # no .isEmpty() method - just compare to ""
print("Is blank check:", blank_str.strip() == "")   # no .isBlank() either - strip() then compare
print("Or simply:", not empty_str)                  # recap Topic 4's "truthiness" - empty string is falsy!


# ============================================
# SECTION 6: SPLITTING AND JOINING STRINGS
# ============================================

csv_data = "Alice,Bob,Charlie,Dave"
names_list = csv_data.split(",")     # same concept and name as Java's split()

print("Split result:")
for n in names_list:
    print("-", n)

# join() works BACKWARDS compared to how you might expect from Java!
# It's called ON the separator, with the list passed as the argument
words = ["Python", "is", "fun"]
joined = " ".join(words)             # NOTE: " ".join(words), not words.join(" ")
print("Joined:", joined)


# ============================================
# SECTION 7: STRINGS ARE DIRECTLY ITERABLE (RECAP FROM TOPIC 6)
# No need for a special method - just loop over the string itself
# ============================================

for letter in "Python":
    print("Letter:", letter)

# Java requires converting to a char array first (.toCharArray())
# before you can loop over individual characters at all


# ============================================
# SECTION 8: STRING SLICING FOR SUBSTRINGS (RECAP FROM TOPIC 7)
# This fully REPLACES Java's substring() method with more power
# ============================================

text = "Hello World"
print("text[0:5]:", text[0:5])      # "Hello"
print("text[6:]:", text[6:])        # "World"
print("text[::-1]:", text[::-1])    # "dlroW olleH" - reverses the ENTIRE string instantly!

# Java needs new StringBuilder(text).reverse().toString() for this -
# Python does it with one slicing trick


# ============================================
# SECTION 9: STRINGS ARE ALREADY EFFICIENT FOR BUILDING - MOSTLY
# Python has NO direct StringBuilder equivalent in common use.
# Modern Python strings handle repeated concatenation reasonably well,
# but the IDIOMATIC approach for building strings in a loop is
# actually to collect pieces in a LIST, then join() at the end
# ============================================

pieces = []
for i in range(1, 6):
    pieces.append(f"Number{i}")

result = " ".join(pieces)
print("Built efficiently:", result)

# This list-then-join() pattern is the Python equivalent of Java's
# StringBuilder - NOT because += is forbidden, but because
# accumulating in a list and joining once is considered more efficient
# and more idiomatic for larger-scale string building


# ============================================
# SECTION 10: f-STRINGS - PYTHON'S MODERN FORMATTING (PREVIEW OF TOPIC 11)
# ============================================

num = 100
numeric_text = "250"
parsed_num = int(numeric_text)

print(f"Number to string (automatic): {num}")
print(f"String to number: {parsed_num}")

# f-strings also support inline expressions directly:
print(f"Sum check: {5 + 3}")
print(f"Uppercase inline: {name.upper()}")