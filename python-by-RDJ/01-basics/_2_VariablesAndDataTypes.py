# ============================================
# TOPIC 2: VARIABLES & DATA TYPES
# Python is DYNAMICALLY typed - you never declare a type.
# The interpreter figures out the type at runtime, based on
# whatever value you assign. The SAME variable can even be
# reassigned to a DIFFERENT type later (Java would never allow this).
# ============================================

# --- Integers (no size limit like Java's byte/short/int/long!) ---
my_int = 2_000_000          # underscores work for readability, same as Java
my_big_int = 15000000000    # NO 'L' suffix needed - Python ints have no fixed size at all

print("int:", my_int)
print("big int:", my_big_int)

# --- Floats (Python has ONLY ONE floating-point type - no float vs double) ---
my_float = 5.75             # no 'f' suffix needed - this IS the only decimal type
print("float:", my_float)

# --- Strings (single OR double quotes both work identically) ---
my_name = "RDJ"
greeting_quote = 'Hello'    # single quotes are just as valid as double quotes
print(my_name, greeting_quote)

# --- Booleans (capitalized! True/False, not true/false) ---
is_python_fun = True
is_learning_done = False
print("boolean 1:", is_python_fun)
print("boolean 2:", is_learning_done)


# ============================================
# CHECKING A VARIABLE'S TYPE AT RUNTIME
# Since Python doesn't declare types upfront, you use type()
# to check what type something currently is
# ============================================

print(type(my_int))        # <class 'int'>
print(type(my_float))      # <class 'float'>
print(type(my_name))       # <class 'str'>
print(type(is_python_fun)) # <class 'bool'>


# ============================================
# DYNAMIC TYPING IN ACTION - THE BIG DIFFERENCE FROM JAVA
# The same variable name can be reassigned to a COMPLETELY
# different type - Python doesn't stop you
# ============================================

flexible_variable = 42
print(flexible_variable, type(flexible_variable))   # 42 <class 'int'>

flexible_variable = "Now I'm a string!"
print(flexible_variable, type(flexible_variable))   # Now I'm a string! <class 'str'>

flexible_variable = 3.14
print(flexible_variable, type(flexible_variable))   # 3.14 <class 'float'>

# In Java, this would be a COMPILE ERROR - once a variable is
# declared 'int x', it can NEVER hold a String or double later.
# Python allows this because types are checked at RUNTIME, not compile time.


# ============================================
# STRING CONCATENATION - A GENUINE GOTCHA VS JAVA
# Java auto-converts numbers to String when using '+' with a String.
# Python does NOT - mixing str and int with '+' crashes!
# ============================================

age = 25
# greeting = "Age: " + age     # <-- this would CRASH: TypeError!
# Python requires EXPLICIT conversion - no automatic mixing allowed
greeting = "Age: " + str(age)   # str() explicitly converts int to string
print(greeting)


# ============================================
# CONSTANTS - PYTHON HAS NO 'final' KEYWORD AT ALL
# There's no enforced way to make a variable unchangeable.
# Constants are PURELY a naming convention: ALL_CAPS signals
# "please don't change this" - but Python won't stop you if you do
# ============================================

PI = 3.14159
MAX_USERS = 100

print("Constant PI:", PI)
PI = 3.14   # Python allows this! No compile error, no warning.
print("PI after 'illegal' reassignment:", PI)
# In Java, 'final double PI' reassignment would be a COMPILE ERROR.
# In Python, this is just... allowed. The ALL_CAPS naming is a
# promise between developers, not a rule enforced by the language.


# ============================================
# VARIABLE NAMING RULES & CONVENTIONS
# ============================================

# Rules (must follow, enforced by Python):
# - Can contain letters, digits, underscore
# - Cannot start with a digit
# - Cannot be a reserved keyword (like 'class', 'def', 'import')
# - Case-sensitive (age and Age are different variables)

# Conventions (community standard, not enforced):
# - snake_case for variables and functions: first_name, total_amount
#   (THIS IS THE BIG DIFFERENCE FROM JAVA - Java uses camelCase,
#   Python uses snake_case as the dominant style)
# - PascalCase for class names: VariablesAndDataTypes (same as Java)
# - ALL_CAPS for constants: MAX_USERS, PI (same convention as Java)

student_age = 21   # good: snake_case, descriptive name
print("Student age:", student_age)


# ============================================
# MULTIPLE ASSIGNMENT - A PYTHON-ONLY CONVENIENCE
# Assign several variables in a single line - no Java equivalent
# ============================================

x, y, z = 1, 2, 3
print(x, y, z)

# Also works for assigning the SAME value to multiple variables:
a = b = c = 0
print(a, b, c)