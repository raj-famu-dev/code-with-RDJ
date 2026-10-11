# ============================================
# TOPIC 10: USER INPUT
# Python's input() is DRAMATICALLY simpler than Java's Scanner.
# No import needed, no object to create, no buffer bugs,
# and EVERYTHING it returns is a string - always, no exceptions.
# ============================================


# ============================================
# SECTION 1: input() - THE ONLY FUNCTION YOU NEED
# No import java.util.Scanner, no Scanner scanner = new Scanner(System.in)
# It's just... a built-in function, ready to use immediately
# ============================================

user_name = input("Enter your name: ")
print(f"Hello, {user_name}!")

# input() does TWO things in one call:
# 1. Prints the prompt text you pass to it (no separate print() needed!)
# 2. Waits for the user to type something and press Enter
# 3. Returns WHATEVER was typed, as a STRING - always


# ============================================
# SECTION 2: EVERYTHING FROM input() IS A STRING - NO EXCEPTIONS
# This is THE single biggest difference from Java's Scanner.
# Java has separate methods: nextInt(), nextDouble(), nextBoolean().
# Python has ONLY input() - it never knows or cares what "type"
# the input "should" be. You must convert it yourself, every time.
# ============================================

age_input = input("Enter your age: ")
print("Type of age_input:", type(age_input))   # <class 'str'> - EVEN THOUGH you typed a number!

# To actually use it as a number, YOU must convert it (recap Topic 4):
age = int(age_input)
print(f"You are {age} years old. Type is now: {type(age)}")

# Or do it in one line, which is extremely common in practice:
height = float(input("Enter your height in meters: "))
print(f"Your height is {height}m.")


# ============================================
# SECTION 3: NO EQUIVALENT TO nextLine() vs next() AT ALL
# input() ALWAYS reads the full line, including spaces -
# there is NO separate "single word" input method, because
# there's no concept of a leftover buffer to worry about
# ============================================

favorite_language = input("Enter your favorite programming language: ")
print("You chose:", favorite_language)

full_sentence = input("Enter a full sentence with spaces: ")
print("You typed:", full_sentence)

# BOTH of these work identically, reading everything typed until
# Enter is pressed - Python makes no distinction at all here


# ============================================
# SECTION 4: READING A BOOLEAN - NO nextBoolean() EXISTS
# You must manually convert the string yourself, however you choose
# ============================================

is_student_input = input("Are you a student? (true/false): ")
is_student = is_student_input.lower() == "true"   # manual comparison, YOU decide the logic
print("Student status:", is_student)

# This is actually MORE flexible than Java's rigid nextBoolean(),
# since you can accept "yes"/"no", "y"/"n", or anything else you want:
is_student_flexible = input("Are you a student? (yes/no): ").lower() in ("yes", "y")
print("Student status (flexible):", is_student_flexible)


# ============================================
# SECTION 5: THE ENTIRE nextInt()+nextLine() BUG CATEGORY
# SIMPLY DOES NOT EXIST IN PYTHON
# This was THE most common beginner bug in Java (Topic 10 there) -
# in Python, there's no leftover buffer, no newline character issue,
# nothing to "consume" between calls at all
# ============================================

number = int(input("Enter a number: "))
sentence = input("Now enter a sentence: ")   # works IMMEDIATELY, no extra fix line needed!

print("Number:", number)
print("Sentence:", sentence)

# Compare this to Java, which REQUIRED an extra scanner.nextLine()
# call specifically to clear a leftover newline character before
# this second input would work correctly at all


# ============================================
# SECTION 6: READING MULTIPLE VALUES ON ONE LINE
# Python has NO automatic "chain reads across one line" behavior
# like Java's Scanner - you must manually SPLIT the input yourself
# ============================================

numbers_input = input("Enter three numbers separated by spaces: ")
parts = numbers_input.split()   # .split() with no argument splits on ANY whitespace
num1, num2, num3 = int(parts[0]), int(parts[1]), int(parts[2])
print("Sum:", num1 + num2 + num3)

# A more compact, very "Pythonic" way to do the exact same thing:
num_list = [int(x) for x in input("Enter three more numbers: ").split()]
print("Sum (compact version):", sum(num_list))


# ============================================
# SECTION 7: VALIDATING INPUT - NO hasNextInt() EXISTS
# Java could CHECK before converting. Python has no equivalent
# check function - you must TRY the conversion and catch the
# failure if it happens (a full preview of 04-exceptions)
# ============================================

favorite_number_input = input("Enter your favorite number: ")

try:
    favorite_number = int(favorite_number_input)
    print("Great choice:", favorite_number)
except ValueError:
    print("That wasn't a valid number!")

# try/except is Python's equivalent of try/catch - same core idea,
# different keyword (except instead of catch). Full coverage
# of this comes in Topic 04-exceptions, but input validation is
# SUCH a common real-world need that it genuinely can't wait that long


# ============================================
# SECTION 8: NO .close() NEEDED AT ALL
# Java's Scanner required scanner.close() when finished, to free
# system resources. Python's input() has NO object to create or
# close in the first place - it's just a function call, start to finish
# ============================================

print("Program finished - no cleanup needed, no .close() call exists.")