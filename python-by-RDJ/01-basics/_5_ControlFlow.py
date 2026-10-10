# ============================================
# TOPIC 5: CONTROL FLOW
# The BIGGEST visual difference from Java: NO CURLY BRACES at all.
# Python uses INDENTATION itself to define code blocks.
# Get the indentation wrong, and your code either crashes
# or - worse - runs with completely different logic than you intended.
# ============================================


# ============================================
# SECTION 1: IF STATEMENT
# ============================================

temperature = 35

if temperature > 30:
    print("It's hot outside.")

# NOTICE: no parentheses REQUIRED around the condition (though allowed),
# no curly braces at all, and a COLON ':' after the condition.
# The indented line(s) below belong to this if - that's the ENTIRE
# mechanism Python uses to know what's "inside" the if block.


# ============================================
# SECTION 2: IF-ELSE STATEMENT
# ============================================

age = 16

if age >= 18:
    print("You can vote.")
else:
    print("You cannot vote yet.")


# ============================================
# SECTION 3: IF-ELIF-ELSE CHAIN
# Java's "else if" becomes Python's single word: elif
# ============================================

score = 72

if score >= 90:
    print("Grade: A")
elif score >= 80:
    print("Grade: B")
elif score >= 70:
    print("Grade: C")
elif score >= 60:
    print("Grade: D")
else:
    print("Grade: F")

# Same behavior as Java: only ONE branch runs, checked top to bottom,
# stops at the first true condition


# ============================================
# SECTION 4: NESTED IF STATEMENTS
# Indentation nests INSIDE further indentation - no braces to count,
# just indentation LEVELS (standard is 4 spaces per level)
# ============================================

has_ticket = True
visitor_age = 25

if has_ticket:
    if visitor_age >= 18:
        print("Entry allowed: Adult with ticket.")
    else:
        print("Entry denied: Minor, even with ticket.")
else:
    print("Entry denied: No ticket.")


# ============================================
# SECTION 5: LOGICAL OPERATORS IN CONDITIONS
# Recap from Topic 3: 'and' / 'or', not && / ||
# ============================================

is_weekend = True
is_holiday = False

if is_weekend or is_holiday:
    print("No work today!")
else:
    print("It's a work day.")

account_balance = 500
is_verified = True

if account_balance > 0 and is_verified:
    print("Transaction approved.")
else:
    print("Transaction denied.")


# ============================================
# SECTION 6: PYTHON HAS NO TRADITIONAL switch AT ALL
# For decades, Python simply had no switch statement -
# developers used if-elif chains instead (what you just saw above)
# ============================================


# ============================================
# SECTION 7: match-case (Python 3.10+) - THE MODERN REPLACEMENT
# Conceptually similar to Java's modern arrow-style switch
# ============================================

day_number = 3

match day_number:
    case 1:
        day_name = "Monday"
    case 2:
        day_name = "Tuesday"
    case 3:
        day_name = "Wednesday"
    case 4:
        day_name = "Thursday"
    case 5:
        day_name = "Friday"
    case 6:
        day_name = "Saturday"
    case 7:
        day_name = "Sunday"
    case _:
        day_name = "Invalid day number"

print("Day:", day_name)

# KEY DIFFERENCES from Java's switch:
# - 'case _:' is the default/fallback case (underscore means "match anything")
# - NO break needed at all - Python's match-case NEVER falls through,
#   so the fall-through bug that plagues Java's traditional switch
#   simply cannot happen in Python


# ============================================
# SECTION 8: match-case WITH MULTIPLE VALUES PER CASE
# Similar to Java's modern "case 1, 2, 3 ->" syntax
# ============================================

month_number = 4

match month_number:
    case 12 | 1 | 2:
        season = "Winter"
    case 3 | 4 | 5:
        season = "Spring"
    case 6 | 7 | 8:
        season = "Summer"
    case 9 | 10 | 11:
        season = "Autumn"
    case _:
        season = "Invalid month"

print("Season:", season)

# The '|' here means OR within a single case - same spirit as
# Java's comma-separated case values, just a different symbol


# ============================================
# SECTION 9: TERNARY-STYLE SHORTCUT (RECAP FROM TOPIC 3)
# ============================================

number = 15
parity = "Even" if number % 2 == 0 else "Odd"
print(number, "is", parity)


# ============================================
# SECTION 10: COMMON PITFALLS TO AVOID IN PYTHON SPECIFICALLY
# ============================================

# Pitfall 1: Using = instead of == -
# Python PREVENTS this entirely differently than Java.
# In Java, assignment inside an if is a compile error (doesn't evaluate to boolean).
# In Python, writing "if x = 10:" is a FLAT-OUT SYNTAX ERROR - it won't
# even parse, because Python's grammar doesn't allow '=' inside a condition at all.
pitfall_value = 10
if pitfall_value == 10:   # correct: comparing
    print("Correct comparison works.")
# if pitfall_value = 10:  # <-- SyntaxError if uncommented, won't even run

# Pitfall 2: INDENTATION ERRORS - Python's version of "forgetting braces"
# Mixing tabs and spaces, or inconsistent indentation levels, causes
# an IndentationError - THIS is Python's most common beginner mistake,
# replacing Java's "forgot a curly brace" category of bugs entirely
x = 5
if x > 0:
    print("x is positive")
else:
    print("x is zero or negative")

# Pitfall 3: Forgetting the colon ':'
# Every if/elif/else/match/case line MUST end in a colon - forgetting
# it is a SyntaxError, and it's an extremely common typo coming from Java,
# since Java never requires anything like this