# ============================================
# TOPIC 1: HELLO WORLD & PROGRAM STRUCTURE
# Unlike Java, Python has NO required class or main() method.
# Code runs top-to-bottom, directly, the moment the file executes.
# ============================================

print("Hello, RDJ is coding in Python!")

# That's it. No public class, no static void main, no semicolons.
# Python's "entry point" is just the top of the file itself.


# ============================================
# THE if __name__ == "__main__": PATTERN
# This IS something like Java's main() - but it's a CONVENTION,
# not a requirement. Used when a file might be imported by
# another file, and you only want this code to run when the
# file is executed DIRECTLY (not when imported as a module).
# ============================================

def greet():
    print("This only runs when the file is executed directly.")

if __name__ == "__main__":
    greet()

# __name__ is a special built-in variable - Python sets it to
# "__main__" automatically when you RUN this file directly,
# but sets it to the module's name if this file is IMPORTED
# by another file instead.