# ============================================
# TOPIC 9: FUNCTIONS
# Java calls these "methods" and requires a class to contain them.
# Python calls them "functions" and they can exist completely
# standalone, with no class needed at all. No return type is
# ever declared - Python figures out what's being returned at runtime.
# ============================================


# ============================================
# SECTION 1: BASIC FUNCTION DEFINITION
# 'def' keyword, colon, indented body - same block rules as
# if/for/while from earlier topics
# ============================================

def greet_user():
    print("Welcome to Python Functions!")

greet_user()   # calling it - no 'static' needed, no class wrapper required at all


# ============================================
# SECTION 2: FUNCTIONS WITH PARAMETERS
# NO type declared on parameters at all - Python accepts
# whatever type you pass in, checked only at runtime
# ============================================

def greet_by_name(user_name):
    print(f"Hello, {user_name}!")

greet_by_name("RDJ")
greet_by_name("Anthropic")


# ============================================
# SECTION 3: FUNCTIONS WITH RETURN VALUES
# 'return' works the same conceptually, but there's NO return
# type declared anywhere in the function signature
# ============================================

def add_numbers(a, b):
    return a + b

total = add_numbers(5, 10)
print("Sum from function:", total)

def calculate_average(a, b, c):
    return (a + b + c) / 3   # recap Topic 3: / always returns float - no cast needed!

average = calculate_average(85, 92, 78)
print("Average from function:", average)


# ============================================
# SECTION 4: DEFAULT PARAMETER VALUES - BUILT INTO PYTHON ITSELF
# Java needs METHOD OVERLOADING to simulate this. Python has
# default values as a NATIVE language feature - no overloading needed
# ============================================

def greet_with_default(user_name, greeting="Hello"):
    print(f"{greeting}, {user_name}!")

greet_with_default("RDJ")                  # uses the default: "Hello, RDJ!"
greet_with_default("RDJ", "Welcome back")  # overrides the default: "Welcome back, RDJ!"

# This ONE function replaces what Java would need TWO overloaded
# methods to accomplish


# ============================================
# SECTION 5: PYTHON HAS NO METHOD OVERLOADING AT ALL
# You CANNOT define two functions with the same name and
# different parameters - the SECOND definition just REPLACES the first
# ============================================

def add(a, b):
    return a + b

def add(a, b, c):   # this doesn't "overload" add - it REPLACES it entirely!
    return a + b + c

# print(add(2, 3))   # <-- CRASHES: missing required argument 'c'!
# The original 2-parameter add() no longer exists at all once
# the 3-parameter version was defined with the same name

print("Only the 3-param version exists now:", add(1, 2, 3))

# The Pythonic replacement for overloading is usually DEFAULT
# PARAMETERS (Section 4) or *args (Section 8) - not multiple
# same-named functions


# ============================================
# SECTION 6: MULTIPLE PARAMETERS, MIXED TYPES
# ============================================

def print_profile(name, age, is_active):
    print(f"Name: {name}, Age: {age}, Active: {is_active}")

print_profile("RDJ", 25, True)


# ============================================
# SECTION 7: KEYWORD ARGUMENTS - CALL BY PARAMETER NAME, NOT JUST POSITION
# This has NO direct Java equivalent at all
# ============================================

print_profile(age=30, name="Dana", is_active=False)
# Notice the ORDER is completely different from the function's
# definition - this still works perfectly because each argument
# is matched by NAME, not by position

print_profile("Charlie", is_active=True, age=19)   # mixing positional + keyword also works


# ============================================
# SECTION 8: *args - VARIABLE NUMBER OF ARGUMENTS
# Conceptually similar to Java's varargs (int... nums), but Python's
# version works with ANY type, not just one declared type
# ============================================

def sum_all(*nums):   # the * collects ALL extra positional arguments into a tuple
    total = 0
    for n in nums:
        total += n
    return total

print("Varargs sum (2 args):", sum_all(1, 2))
print("Varargs sum (5 args):", sum_all(1, 2, 3, 4, 5))
print("Varargs sum (0 args):", sum_all())


# ============================================
# SECTION 9: **kwargs - VARIABLE NUMBER OF KEYWORD ARGUMENTS
# NO Java equivalent at all - collects named arguments into a dictionary
# ============================================

def print_details(**kwargs):   # ** collects extra keyword arguments into a dict
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_details(name="RDJ", age=25, city="Austin")
# You can pass ANY number of named arguments, with ANY names -
# the function doesn't need to predefine them at all


# ============================================
# SECTION 10: void vs RETURN - NO 'void' KEYWORD EXISTS AT ALL
# A function with no explicit return statement automatically
# returns a special value called None (Python's version of null)
# ============================================

def print_message(msg):
    print(msg)
    # no return statement at all - implicitly returns None

result = print_message("This prints something")
print("What print_message() actually returned:", result)   # None

def build_message(msg):
    return f"Built message: {msg}"

built = build_message("This returns a value")
print(built)


# ============================================
# SECTION 11: "PASS BY VALUE" GETS MORE CONFUSING IN PYTHON
# Python's actual behavior is called "pass by object reference" -
# immutable types (int, str, float, tuple) BEHAVE like pass-by-value,
# but mutable types (list, dict) behave like Java's arrays
# ============================================

def modify_value(value):
    value = value + 100   # reassigns the LOCAL name only
    print("Inside function, value is now:", value)

original_number = 10
print("Before function call:", original_number)
modify_value(original_number)
print("After function call:", original_number)
# Still 10! Reassigning a parameter inside a function never
# affects the caller's variable - same OUTCOME as Java's primitives


def modify_list(lst):
    lst[0] = 999   # modifies the ACTUAL list's CONTENTS, not just the local name

numbers = [1, 2, 3]
print("Before list function call:", numbers[0])
modify_list(numbers)
print("After list function call:", numbers[0])
# This DOES change! Same underlying reason as Java arrays:
# both 'numbers' and the parameter 'lst' point to the SAME list object


# ============================================
# SECTION 12: RECURSION - SAME CONCEPT, NO return TYPE NEEDED
# ============================================

def factorial(n):
    if n <= 1:
        return 1        # base case
    return n * factorial(n - 1)   # recursive case

print("Factorial of 5:", factorial(5))


# ============================================
# SECTION 13: TYPE HINTS - OPTIONAL, NOT ENFORCED AT ALL
# Python 3.5+ lets you ANNOTATE expected types, purely for
# readability and IDE assistance - the interpreter does NOT
# enforce these at runtime the way Java's compiler enforces types
# ============================================

def add_with_hints(a: int, b: int) -> int:
    return a + b

print("With type hints:", add_with_hints(3, 4))
print("Hints are NOT enforced:", add_with_hints("3", "4"))   # works anyway! Just concatenates strings
# Python happily ran this even though "3" and "4" are strings, not ints -
# the -> int and (a: int, b: int) are purely DOCUMENTATION, never checked