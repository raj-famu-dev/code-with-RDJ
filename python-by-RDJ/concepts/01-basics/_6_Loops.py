# ============================================
# TOPIC 6: LOOPS
# Python has 'for' and 'while' - but NO traditional C-style
# for(i=0; i<5; i++) loop at all. Python's 'for' ALWAYS iterates
# over a sequence - there's no separate "counting loop" syntax.
# Python also has NO do-while loop whatsoever.
# ============================================


# ============================================
# SECTION 1: FOR LOOP - ALWAYS ITERATES OVER A SEQUENCE
# To count like Java's for(i=0; i<5; i++), you use range()
# ============================================

for i in range(1, 6):   # start=1, stop=6 (EXCLUSIVE - stops before 6)
    print("For loop iteration:", i)

# Breakdown of range(1, 6):
# - starts at 1 (inclusive)
# - stops BEFORE 6 (exclusive) - so it produces 1, 2, 3, 4, 5
# - there is no separate "initialization; condition; update" syntax at all -
#   range() handles the whole counting sequence in one function call

# range() can also take just ONE argument (assumes start=0):
for i in range(5):      # produces 0, 1, 2, 3, 4
    print("range(5) gives:", i)

# range() can take a THIRD argument for step size:
for i in range(0, 10, 2):   # start=0, stop=10, step=2
    print("Even number:", i)   # 0, 2, 4, 6, 8


# ============================================
# SECTION 2: WHILE LOOP
# Same core idea as Java - condition checked BEFORE each iteration
# ============================================

count = 1
while count <= 5:
    print("While loop count:", count)
    count += 1   # must manually update - NO ++ exists, same as Topic 3

# Just like Java: forgetting to update the condition variable here
# causes an infinite loop, since nothing would ever make count > 5


# ============================================
# SECTION 3: PYTHON HAS NO do-while LOOP AT ALL
# This is a genuine missing feature - no direct equivalent exists.
# The common workaround is while True: with a break at the end
# ============================================

attempts = 10
while True:
    print("Simulating do-while, attempts =", attempts)
    attempts += 1
    if attempts >= 15:
        break   # exits the loop - without this, it runs forever

# This achieves the SAME effect as Java's do-while (body runs at
# least once), but Python has no dedicated syntax for it - you
# build it yourself using while True + break


# ============================================
# SECTION 4: NESTED LOOPS
# Indentation nests exactly like nested if statements from Topic 5
# ============================================

print("Multiplication table (nested loop):")
for row in range(1, 4):
    for col in range(1, 4):
        print(row, "x", col, "=", row * col)

# Outer loop runs 3 times; for EACH outer iteration, inner loop
# runs 3 times fully - identical logic to Java, just no braces


# ============================================
# SECTION 5: BREAK STATEMENT
# Identical keyword and behavior to Java
# ============================================

print("Using break:")
for i in range(1, 11):
    if i == 6:
        break
    print("break demo, i =", i)

# Output: prints 1 through 5, then stops


# ============================================
# SECTION 6: CONTINUE STATEMENT
# Identical keyword and behavior to Java
# ============================================

print("Using continue:")
for i in range(1, 11):
    if i % 2 == 0:
        continue   # skip printing for even numbers
    print("continue demo, odd number:", i)

# Output: prints only odd numbers 1, 3, 5, 7, 9


# ============================================
# SECTION 7: FOR-EACH IS THE ONLY WAY PYTHON'S for WORKS
# There's no separate "enhanced for loop" - EVERY Python for loop
# is fundamentally a for-each loop, whether iterating a range,
# a list, or a string
# ============================================

numbers = [10, 20, 30, 40, 50]   # a Python list (covered fully in Topic 7)

for num in numbers:
    print("For-each value:", num)

names = ["Alice", "Bob", "Charlie"]
for name in names:
    print("Name:", name)

# Strings are ALSO directly iterable - no separate method needed!
for letter in "Python":
    print("Letter:", letter)

# Java has NOTHING like this - you can't for-each over a String
# directly without first converting it to a char array


# ============================================
# SECTION 8: GETTING THE INDEX DURING A FOR-EACH - enumerate()
# Python's for loop normally gives you ONLY the value, not the index.
# enumerate() wraps a sequence to give you BOTH at once
# ============================================

for index, value in enumerate(names):
    print(f"Index {index}: {value}")

# This replaces Java's indexed for(int i = 0; i < arr.length; i++)
# pattern when you need the position AND the value together


# ============================================
# SECTION 9: INFINITE LOOPS
# ============================================

safety_counter = 0
while True:
    print("Infinite loop iteration:", safety_counter)
    safety_counter += 1
    if safety_counter >= 3:
        break   # without this, it would run forever

# Common ACCIDENTAL infinite loop bug (commented out - don't run as-is):
# mistake = 1
# while mistake <= 5:
#     print(mistake)
#     # forgot mistake += 1 here! condition never becomes false -> infinite loop


# ============================================
# SECTION 10: PYTHON HAS NO LABELED BREAK AT ALL
# Java's 'break outerLoop;' syntax has NO equivalent in Python -
# this is a genuine missing feature with a few different workarounds
# ============================================

# Workaround 1: use a flag variable
found = False
for i in range(1, 4):
    for j in range(1, 4):
        if i == 2 and j == 2:
            found = True
            break   # only breaks the INNER loop
    if found:
        break   # manually check the flag to break the OUTER loop too
    print(f"i={i}, j={j}")

# Workaround 2 (cleaner, when applicable): put the nested loops
# inside a function, and use 'return' to exit everything at once
def find_pair():
    for i in range(1, 4):
        for j in range(1, 4):
            if i == 2 and j == 2:
                return i, j   # exits BOTH loops instantly, from any depth
    return None

result = find_pair()
print("Found pair:", result)


# ============================================
# SECTION 11: for...else AND while...else - PYTHON-ONLY FEATURE
# Java has NOTHING like this at all. The 'else' block runs ONLY
# if the loop completed WITHOUT hitting a break
# ============================================

for i in range(1, 6):
    if i == 10:   # this condition never becomes true
        break
    print("Searching...", i)
else:
    print("Loop completed without breaking - else block runs!")

# If a break DOES happen, the else block is SKIPPED entirely:
for i in range(1, 6):
    if i == 3:
        break
    print("Searching again...", i)
else:
    print("This will NOT print, because break happened.")


# ============================================
# SECTION 12: CHOOSING THE RIGHT LOOP
# ============================================

# Use 'for' when: iterating over a known range or sequence
#   (this covers MOST of what Java's traditional for loop did too)
# Use 'while' when: looping based on a condition, count unknown upfront
# Use 'while True' + break when: you need "at least once" behavior
#   (Python's do-while substitute)