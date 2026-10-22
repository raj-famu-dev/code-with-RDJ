# ============================================
# TOPIC 4: TYPE CASTING
# Python calls this "type conversion" more often than "casting",
# since there's no (type) syntax like Java - you use FUNCTIONS instead.
# Python also has NO implicit/explicit distinction the way Java does -
# almost everything requires an EXPLICIT function call.
# ============================================


# ============================================
# SECTION 1: THE BIG DIFFERENCE FROM JAVA
# Java separates "widening" (automatic) from "narrowing" (manual cast).
# Python has NO automatic widening at all for most conversions -
# you almost always call a conversion function explicitly.
# The ONE exception: Python auto-promotes int to float during
# mixed-type arithmetic (similar to Java's automatic promotion).
# ============================================

whole_number = 10
decimal_number = 3.5

mixed_result = whole_number + decimal_number   # int automatically becomes float here
print("Mixed arithmetic result:", mixed_result)       # 13.5
print("Type of mixed_result:", type(mixed_result))    # <class 'float'>

# This IS automatic - Python doesn't require you to write int(whole_number)
# first. But this is the ONLY kind of "automatic" conversion Python does.


# ============================================
# SECTION 2: EXPLICIT CONVERSION FUNCTIONS
# int(), float(), str(), bool() - these REPLACE Java's (type) syntax
# ============================================

# --- Converting float to int: int() TRUNCATES, same as Java's (int) cast ---
price = 9.99
truncated_price = int(price)
print("9.99 converted to int:", truncated_price)   # 9, NOT 10 - truncates, doesn't round

# --- Converting int to float ---
whole = 100
as_float = float(whole)
print("100 converted to float:", as_float)   # 100.0

# --- Converting string to int/float (VERY COMMON - user input is ALWAYS a string) ---
numeric_text = "123"
parsed_int = int(numeric_text)
print("String '123' to int:", parsed_int)

numeric_decimal_text = "45.67"
parsed_float = float(numeric_decimal_text)
print("String '45.67' to float:", parsed_float)

# --- Converting int/float to string ---
number = 42
number_as_string = str(number)
print("int 42 to string:", number_as_string)
print("Type check:", type(number_as_string))   # <class 'str'>


# ============================================
# SECTION 3: THE CRASH YOU'LL HIT CONSTANTLY AS A BEGINNER
# Trying to convert a non-numeric string crashes with ValueError
# (similar to Java's NumberFormatException)
# ============================================

# bad_conversion = int("abc")   # <-- CRASHES: ValueError: invalid literal for int()
# Unlike some languages, Python gives NO silent fallback - it just crashes
# immediately unless you wrap it in a try/except (covered in 04-exceptions)


# ============================================
# SECTION 4: int() TRUNCATES TOWARD ZERO - DIFFERENT FROM // !
# This is a genuinely confusing Python-specific gotcha
# ============================================

print("int(9.99):", int(9.99))     # 9 - truncates toward zero
print("int(-9.99):", int(-9.99))   # -9 - ALSO truncates toward zero, not -10!

# Compare this to floor division from Topic 3:
print("-15 // 4:", -15 // 4)       # -4 - floors toward NEGATIVE INFINITY

# So int() and // round DIFFERENTLY for negative numbers.
# int() always truncates toward zero. // always floors downward.
# This inconsistency catches almost everyone off guard at least once.


# ============================================
# SECTION 5: bool() CONVERSION - PYTHON'S "TRUTHINESS" CONCEPT
# Java has NO equivalent to this at all - only true/false are boolean.
# Python lets you convert almost ANYTHING into a bool, based on rules
# ============================================

print("bool(0):", bool(0))            # False - zero is "falsy"
print("bool(1):", bool(1))            # True - any nonzero number is "truthy"
print("bool(-5):", bool(-5))          # True - even negative numbers are truthy!
print("bool(''):", bool(''))          # False - empty string is "falsy"
print("bool('hello'):", bool('hello'))# True - any non-empty string is "truthy"
print("bool(None):", bool(None))      # False - None is always falsy

# This "truthiness" concept will matter a LOT once we reach control flow -
# Python lets you write "if some_string:" directly, without needing
# "if (someString != null && !someString.isEmpty())" like Java would


# ============================================
# SECTION 6: NO BYTE/SHORT/LONG DISTINCTION AT ALL
# Python only has ONE integer type - no overflow, no wraparound,
# no range limits to worry about (unlike Java's byte/short/int/long)
# ============================================

huge_number = 99999999999999999999999999999999999999
print("Huge number works fine:", huge_number)
print("Type:", type(huge_number))   # still just <class 'int'>

# In Java, this would require careful type selection (long, or even
# BigInteger for something this large) and risk silent overflow.
# Python integers automatically grow to however large they need to be -
# there is NO overflow bug equivalent to Java's byte/int wraparound at all.


# ============================================
# SECTION 7: CASTING BETWEEN char AND int - DOESN'T REALLY APPLY
# Python has NO separate 'char' type - a single character IS just
# a string of length 1. Conversion uses ord() and chr() instead
# ============================================

letter = 'A'
unicode_value = ord(letter)      # ord() = "ordinal" - gets the Unicode code point
print("ord('A'):", unicode_value)   # 65

back_to_char = chr(65)           # chr() = reverse of ord() - number back to character
print("chr(65):", back_to_char)     # A

# Java equivalent: (int) 'A' and (char) 65
# Python just uses two separate functions instead of a cast


# ============================================
# SECTION 8: f-STRINGS AUTO-CONVERT FOR YOU (PREVIEW OF TOPIC 11)
# Inside an f-string, you can embed ANY type directly -
# Python converts it to a readable string automatically
# ============================================

age = 25
print(f"Age is {age}")          # no need for str(age) inside an f-string!
print(f"Pi is {3.14159}")       # works directly with floats too
print(f"Flag is {True}")        # even booleans convert automatically here

# This ONLY applies inside f-strings specifically - regular string
# concatenation with '+' still requires explicit str() (see Topic 2's gotcha)