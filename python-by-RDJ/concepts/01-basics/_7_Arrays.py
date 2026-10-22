# ============================================
# TOPIC 7: LISTS & ARRAYS
# Python's 'list' replaces Java's array ENTIRELY for everyday use -
# it's dynamic-size, can hold MIXED types, and has dozens of
# built-in methods. There's no separate "ArrayList vs array"
# decision to make - list is almost always the right default.
# ============================================


# ============================================
# SECTION 1: DECLARING AND INITIALIZING LISTS
# No size declaration needed at all - lists grow/shrink freely
# ============================================

scores = [90, 85, 78, 92, 88]   # square brackets, comma-separated - that's it
print("Scores:", scores)

ages = [21, 25, 19, 34, 40]
fruits = ["Apple", "Banana", "Cherry"]

print("First score:", scores[0])
print("First age:", ages[0])
print("First fruit:", fruits[0])

# Python lists can hold MIXED types in the same list - Java arrays CANNOT do this
mixed_list = [1, "two", 3.0, True, None]
print("Mixed list:", mixed_list)
# Java would require Object[] and constant casting to even attempt this


# ============================================
# SECTION 2: ACCESSING AND MODIFYING ELEMENTS
# Zero-indexed, same as Java - but Python ALSO supports NEGATIVE indices!
# ============================================

print("Original age at index 2:", ages[2])
ages[2] = 20
print("Updated age at index 2:", ages[2])

# len() replaces Java's .length - it's a FUNCTION, not a property or method
print("Length of ages list:", len(ages))

# NEGATIVE INDEXING - Java has NOTHING like this at all
print("Last element (index -1):", ages[-1])    # same as ages[len(ages)-1] in Java
print("Second-to-last (index -2):", ages[-2])


# ============================================
# SECTION 3: LOOPING THROUGH LISTS (RECAP FROM TOPIC 6)
# ============================================

print("Scores using indexed loop:")
for i in range(len(scores)):
    print(f"Index {i}: {scores[i]}")

print("Fruits using direct for-each:")
for fruit in fruits:
    print(fruit)


# ============================================
# SECTION 4: LISTS ARE DYNAMIC - ADDING AND REMOVING ELEMENTS
# THIS is the biggest structural difference from Java arrays.
# Java arrays are FIXED SIZE - Python lists can grow/shrink freely,
# with none of the "create a new array" dance Java requires
# ============================================

fruits.append("Mango")           # adds to the END
print("After append:", fruits)

fruits.insert(1, "Blueberry")    # inserts at a SPECIFIC index, shifts others right
print("After insert:", fruits)

fruits.remove("Banana")          # removes by VALUE (first match), not by index
print("After remove('Banana'):", fruits)

popped = fruits.pop()            # removes and RETURNS the last element
print("Popped element:", popped)
print("After pop():", fruits)

popped_at_index = fruits.pop(0)  # removes and returns element at a specific index
print("Popped at index 0:", popped_at_index)
print("After pop(0):", fruits)

del fruits[0]                     # another way to delete by index (no return value)
print("After del fruits[0]:", fruits)


# ============================================
# SECTION 5: COMMON LIST OPERATIONS
# ============================================

# Sum, average, max, min - Python has BUILT-IN functions for all of these.
# Java requires manual loops for every single one of these.
print("Sum of scores:", sum(scores))
print("Average score:", sum(scores) / len(scores))
print("Highest score:", max(scores))
print("Lowest score:", min(scores))
print("Sorted scores:", sorted(scores))          # returns a NEW sorted list
scores.sort()                                     # sorts the ORIGINAL list in place
print("Scores after .sort():", scores)
scores.sort(reverse=True)
print("Scores sorted descending:", scores)


# ============================================
# SECTION 6: THE IndexError GOTCHA
# Same concept as Java's ArrayIndexOutOfBoundsException,
# just a different exception name
# ============================================

# Valid indices for 'ages' (length 5) are 0 through 4, or -1 through -5
# ages[10] would throw: IndexError: list index out of range
# Uncomment below to see the crash:
# print(ages[10])

print("Valid last index of ages:", ages[len(ages) - 1])
print("Same thing, using negative indexing:", ages[-1])   # much more common in Python


# ============================================
# SECTION 7: SLICING - A MAJOR PYTHON-ONLY FEATURE
# Java has NOTHING like this at all for arrays - this is genuinely
# one of Python's most powerful list features
# ============================================

numbers_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print("Slice [2:5]:", numbers_list[2:5])      # indices 2, 3, 4 (end EXCLUSIVE, like range())
print("Slice [:3]:", numbers_list[:3])        # from the start up to (not including) index 3
print("Slice [7:]:", numbers_list[7:])        # from index 7 to the end
print("Slice [::2]:", numbers_list[::2])      # every 2nd element: 0,2,4,6,8
print("Slice [::-1]:", numbers_list[::-1])    # REVERSES the entire list!

# This single [::-1] trick replaces what Java needs a whole loop
# (or Collections.reverse()) to accomplish


# ============================================
# SECTION 8: 2D LISTS (NESTED LISTS) - LIKE JAVA'S 2D ARRAYS
# No special [][] syntax - just a list containing other lists
# ============================================

grid = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

print("Element at grid[1][2]:", grid[1][2])
print("Element at grid[2][1]:", grid[2][1])

# Looping through a 2D list - same nested pattern as Java
print("Printing the full grid:")
for row in grid:
    for value in row:
        print(value, end=" ")
    print()   # moves to next line after each row


# ============================================
# SECTION 9: LISTS ARE NOT FIXED SIZE - NO "ArrayList VS array" DECISION
# Java forces you to choose between array (fixed) and ArrayList (dynamic).
# Python's list IS the dynamic version by default - there's no fixed-size
# equivalent used in everyday code at all
# ============================================

flexible_list = []          # starts completely empty - no size needed upfront
flexible_list.append(10)
flexible_list.append(20)
flexible_list.append(30)
print("Grew from empty:", flexible_list)

# In Java, int[] arr = new int[3]; LOCKS you into exactly 3 slots forever.
# Python's list never has this limitation at all.


# ============================================
# SECTION 10: COPYING LISTS - SAME REFERENCE GOTCHA AS JAVA ARRAYS
# ============================================

original = [1, 2, 3]
wrong_copy = original     # this is a REFERENCE copy, NOT a real copy - same as Java!
wrong_copy[0] = 999
print("Original after 'wrong copy' modification:", original)
# prints [999, 2, 3] - because wrong_copy and original point to the SAME list

# Correct ways to actually copy a list's contents:
real_copy_1 = original.copy()        # method 1: .copy()
real_copy_2 = original[:]            # method 2: full slice (very common idiom)
real_copy_3 = list(original)         # method 3: list() constructor

real_copy_1[0] = 111
print("Original after 'real copy' modification:", original)   # unaffected - stays [999, 2, 3]


# ============================================
# SECTION 11: TUPLES - PYTHON'S "IMMUTABLE LIST" (NO JAVA EQUIVALENT)
# Written with parentheses instead of brackets. Once created,
# a tuple can NEVER be modified - similar spirit to Java's final,
# but for an entire ordered collection rather than one variable
# ============================================

coordinates = (10, 20)
print("Tuple:", coordinates)
print("First value:", coordinates[0])

# coordinates[0] = 99   # <-- CRASHES: TypeError: 'tuple' object does not support item assignment

# Use a tuple when you want to GUARANTEE the data never changes -
# e.g., representing a fixed (x, y) point, or returning multiple
# values from a function (recap: Topic 6's find_pair() actually
# returned a tuple!)


# ============================================
# SECTION 12: LIST COMPREHENSIONS - A SIGNATURE PYTHON FEATURE
# Builds a new list in ONE LINE, based on a loop + optional condition.
# Java has nothing this concise built into the language itself
# ============================================

squares = [x ** 2 for x in range(1, 6)]
print("Squares:", squares)         # [1, 4, 9, 16, 25]

even_numbers = [x for x in range(1, 20) if x % 2 == 0]
print("Even numbers:", even_numbers)

# The Java equivalent would be a full for loop with a manually
# created ArrayList and repeated .add() calls - this one line
# replaces all of that