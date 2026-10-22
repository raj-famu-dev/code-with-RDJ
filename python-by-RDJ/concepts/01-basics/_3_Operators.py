# ============================================
# TOPIC 3: OPERATORS
# Mostly similar to Java, but with some genuinely different
# syntax and behavior - especially division and the complete
# absence of ++ / -- increment operators
# ============================================


# ============================================
# SECTION 1: ARITHMETIC OPERATORS
# ============================================

a = 15
b = 4

print("a + b =", a + b)    # addition
print("a - b =", a - b)    # subtraction
print("a * b =", a * b)    # multiplication
print("a / b =", a / b)    # TRUE division -> ALWAYS returns a float, even for whole results!
print("a % b =", a % b)    # modulus -> remainder, same as Java

# THE BIG DIFFERENCE: in Java, int/int = int (truncated).
# In Python, / ALWAYS produces a float result, no exceptions.
print("15 / 4 =", 15 / 4)   # 3.75, not 3!
print("8 / 2 =", 8 / 2)     # 4.0 - still a float, even though it divides evenly!

# If you WANT integer division (Java-style truncation), use // instead
print("a // b =", a // b)   # 3 - floor division, drops the decimal
print("15 // 4 =", 15 // 4) # 3
print("-15 // 4 =", -15 // 4)  # -4, NOT -3! Floors toward negative infinity,
# unlike Java's truncation toward zero - a real gotcha

# POWER operator - Python has this built in, Java does NOT
print("a ** 2 =", a ** 2)   # 225 (15 squared) - no Math.pow() needed


# ============================================
# SECTION 2: NO ++ OR -- IN PYTHON AT ALL
# This operator simply doesn't exist - trying to write x++ is
# a SYNTAX ERROR in Python, not just discouraged
# ============================================

x = 10
print("Original x:", x)

x += 1   # Python's equivalent - shorthand assignment, same as Java
print("After x += 1:", x)

x -= 1
print("After x -= 1:", x)

# x++  # <-- this would be a SyntaxError if uncommented!
# There is no pre/post increment distinction to worry about at all


# ============================================
# SECTION 3: ASSIGNMENT OPERATORS (SAME AS JAVA)
# ============================================

num = 10

num += 5    # same as: num = num + 5
print("num += 5:", num)

num -= 3
print("num -= 3:", num)

num *= 2
print("num *= 2:", num)

num /= 4    # NOTE: this always produces a float now!
print("num /= 4:", num)   # 6.0, not 6

num //= 2   # floor-divide assignment - Python-only shorthand
print("num //= 2:", num)

num **= 2   # power assignment - also Python-only
print("num **= 2:", num)


# ============================================
# SECTION 4: RELATIONAL (COMPARISON) OPERATORS
# Identical symbols to Java, same behavior
# ============================================

p = 10
q = 20

print("p == q:", p == q)
print("p != q:", p != q)
print("p > q:", p > q)
print("p < q:", p < q)
print("p >= q:", p >= q)
print("p <= q:", p <= q)

# Python ALSO allows CHAINED comparisons - no Java equivalent at all!
print("1 < p < 15:", 1 < p < 15)   # True - checks BOTH conditions in one expression
# This is NOT the same as (1 < p) < 15 the way Java would (mis)interpret it -
# Python specifically understands chained comparisons as a single readable check


# ============================================
# SECTION 5: LOGICAL OPERATORS
# DIFFERENT KEYWORDS from Java - words instead of symbols!
# ============================================

is_adult = True
has_id = False

print("is_adult and has_id:", is_adult and has_id)   # 'and', NOT &&
print("is_adult or has_id:", is_adult or has_id)     # 'or', NOT ||
print("not is_adult:", not is_adult)                 # 'not', NOT !

# Short-circuit behavior works identically to Java:
# in (A and B), if A is False, B is never evaluated
# in (A or B), if A is True, B is never evaluated


# ============================================
# SECTION 6: BITWISE OPERATORS (SAME SYMBOLS AS JAVA)
# ============================================

bit1 = 5   # binary: 0101
bit2 = 3   # binary: 0011

print("bit1 & bit2:", bit1 & bit2)    # AND -> 1
print("bit1 | bit2:", bit1 | bit2)    # OR -> 7
print("bit1 ^ bit2:", bit1 ^ bit2)    # XOR -> 6
print("~bit1:", ~bit1)                # NOT -> -6
print("bit1 << 1:", bit1 << 1)        # left shift -> 10
print("bit1 >> 1:", bit1 >> 1)        # right shift -> 2


# ============================================
# SECTION 7: TERNARY-STYLE EXPRESSION
# Python has NO ?: symbol - instead uses a readable inline if-else
# ============================================

age = 20
result = "Adult" if age >= 18 else "Minor"
print("Ternary result:", result)

# Java equivalent:  String result = (age >= 18) ? "Adult" : "Minor";
# Python reads almost like English: value_if_true if condition else value_if_false


# ============================================
# SECTION 8: MEMBERSHIP OPERATORS - NO JAVA EQUIVALENT AT ALL
# Check if a value exists inside a sequence (string, list, etc.)
# ============================================

name = "RDJ"
print("'D' in name:", 'D' in name)           # True - checks if character exists in string
print("'Z' not in name:", 'Z' not in name)   # True - confirms absence

# This single keyword replaces what Java would need .contains() or
# .indexOf() != -1 for


# ============================================
# SECTION 9: IDENTITY OPERATORS - is / is not
# Compares whether two variables point to the EXACT SAME object
# in memory - conceptually similar to Java's == for objects
# ============================================

list1 = [1, 2, 3]
list2 = [1, 2, 3]
list3 = list1

print("list1 == list2:", list1 == list2)   # True - same CONTENT
print("list1 is list2:", list1 is list2)   # False - different OBJECTS in memory
print("list1 is list3:", list1 is list3)   # True - same OBJECT (list3 points to list1)

# This mirrors Java's == vs .equals() distinction for objects,
# just using different keywords: 'is' (reference) vs '==' (content)


# ============================================
# SECTION 10: OPERATOR PRECEDENCE
# Mostly the same order as Java, with ** and // added in
# ============================================

precedence_test = 10 + 5 * 2
print("10 + 5 * 2 =", precedence_test)   # 20 - multiplication first, same as Java

precedence_with_parens = (10 + 5) * 2
print("(10 + 5) * 2 =", precedence_with_parens)   # 30 - parentheses override, same as Java