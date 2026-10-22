# ============================================
# TOPIC 11: OUTPUT FORMATTING
# Python has gone through THREE different formatting styles over
# its history (%-formatting, .format(), and f-strings). f-strings
# (Python 3.6+) are the modern standard and what you should use
# by default - but you'll see the older styles in existing code,
# so it's worth recognizing all three.
# ============================================


# ============================================
# SECTION 1: THE BASIC print() FUNCTION (RECAP)
# ============================================

print("This prints text AND moves to a new line after")    # same as println
print("This stays on the same line...", end="")             # end="" replaces print's behavior
print(" ...so this continues right after it")

print()   # empty print() just moves to the next line, same as Java's println()

import sys
print("This prints to the ERROR stream", file=sys.stderr)
# file=sys.stderr redirects output - conceptually similar to System.err,
# though it requires importing sys first (not built in like Java's System.err)


# ============================================
# SECTION 2: f-STRINGS - THE MODERN STANDARD (USE THIS BY DEFAULT)
# Put an 'f' right before the opening quote, then embed ANY
# expression directly inside curly braces { }
# ============================================

name = "RDJ"
age = 25
salary = 55000.5

print(f"Name: {name}, Age: {age}, Salary: {salary}")

# f-strings embed EXPRESSIONS, not just variables - this is
# something Java's printf cannot do at all:
print(f"Next year you'll be {age + 1}")
print(f"Uppercase name: {name.upper()}")


# ============================================
# SECTION 3: CONTROLLING DECIMAL PRECISION INSIDE f-STRINGS
# The format spec goes AFTER a colon, inside the same braces
# ============================================

pi = 3.14159265

print(f"Default: {pi}")              # 3.14159265 - Python does NOT auto-round by default!
print(f"2 decimals: {pi:.2f}")       # 3.14
print(f"4 decimals: {pi:.4f}")       # 3.1416 - rounds, same rule as Java's %.4f
print(f"0 decimals: {pi:.0f}")       # 3

# IMPORTANT DIFFERENCE: Java's printf ALWAYS shows 6 decimals by
# default for %f. Python's f-strings show the FULL precision of
# the actual float value unless you specify precision yourself.


# ============================================
# SECTION 4: FIELD WIDTH AND ALIGNMENT
# Different symbol placement than Java's printf, but same idea
# ============================================

print(f"[{42:10d}]")      # right-aligned, padded to 10 characters wide (default for numbers)
print(f"[{42:<10d}]")     # < forces LEFT alignment
print(f"[{'Hi':10s}]")    # strings default to LEFT alignment already
print(f"[{'Hi':>10s}]")   # > forces RIGHT alignment for strings
print(f"[{'Hi':^10s}]")   # ^ CENTERS the text - Java's printf has NO centering option at all!


# ============================================
# SECTION 5: PRACTICAL EXAMPLE - ALIGNED TABLE OUTPUT
# ============================================

items = ["Apple", "Bread", "Milk"]
prices = [1.50, 3.25, 2.10]

print(f"{'Item':<10} {'Price':>10}")
print(f"{'----':<10} {'-----':>10}")
for item, price in zip(items, prices):   # zip() pairs up two lists element-by-element
    print(f"{item:<10} {price:>10.2f}")

# zip() has NO direct Java equivalent - it's the idiomatic way
# to loop through two lists together without manual indexing


# ============================================
# SECTION 6: THE OLDER .format() METHOD (STILL SEEN IN EXISTING CODE)
# Predates f-strings - functionally similar, but more verbose
# ============================================

formatted_message = "Hello {}, you are {} years old.".format(name, age)
print(formatted_message)

# You'll encounter this in older Python codebases - but for NEW
# code, f-strings are strictly preferred for being more readable


# ============================================
# SECTION 7: THE OLDEST %-FORMATTING (RARELY USED NOW, GOOD TO RECOGNIZE)
# This is the style MOST similar to Java's printf, historically
# ============================================

old_style = "Name: %s, Age: %d" % (name, age)
print(old_style)

# %s and %d work almost identically to Java's printf specifiers -
# this is genuinely the closest historical cousin to Java's printf,
# but it's considered outdated Python style today


# ============================================
# SECTION 8: ESCAPE SEQUENCES - SAME SYMBOLS AS JAVA
# ============================================

print("Newline example:\nThis is on a new line")
print("Tab example:\tThis is tabbed over")
print("Quote example: \"This is in quotes\"")
print("Backslash example: C:\\Users\\RDJ")

# Python ALSO supports raw strings - prefix with 'r' to disable
# ALL escape sequence processing entirely (no Java equivalent at all!)
raw_path = r"C:\Users\RDJ"   # backslashes are LITERAL here, no need to double them
print("Raw string:", raw_path)


# ============================================
# SECTION 9: TRIPLE-QUOTED STRINGS (RECAP FROM TOPIC 8)
# Python's answer to Java's text blocks - but supported since
# Python's earliest versions, not just a recent addition
# ============================================

text_block = """This spans multiple lines.
No escape characters needed at all.
Great for JSON, HTML, or SQL snippets."""

print(text_block)


# ============================================
# SECTION 10: NUMBER FORMATTING WITH COMMAS
# Same comma trick as Java, just placed differently in the syntax
# ============================================

large_number = 1234567
print(f"With commas: {large_number:,}")          # 1,234,567

large_money = 9876543.21
print(f"Money with commas: ${large_money:,.2f}")  # $9,876,543.21


# ============================================
# SECTION 11: f-STRINGS WITH NESTED QUOTES AND DEBUGGING SHORTCUT
# Two genuinely Python-only conveniences
# ============================================

# You can use different quote styles inside vs outside an f-string:
print(f"She said {'hello' if True else 'goodbye'}")

# The = specifier (Python 3.8+) prints BOTH the expression AND its
# value - incredibly useful for quick debugging, NO Java equivalent at all
x = 42
print(f"{x=}")                    # prints: x=42
print(f"{age + 1=}")              # prints: age + 1=26