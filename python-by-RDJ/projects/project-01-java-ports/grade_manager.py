# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Student Grade Manager: a Python port of project-04 (StudentGradeManager.java).

The core (Student, GradeBook, parse_score, format_* helpers) is pure and has no
input(). The interactive menu lives in run()/main() so tests can drive it.
Subjects are Math, Physics, Biology everywhere (the Java table header said
Science/English by mistake).
"""
from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

SUBJECTS: tuple[str, ...] = ("Math", "Physics", "Biology")
MAX_STUDENTS = 50
_INT_RE = re.compile(r"[+-]?\d+", re.ASCII)


# ===== SECTION 1: data model =====
def assign_grade(average: float) -> str:
    """Letter grade from an average (same cut-offs as the Java version)."""
    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "F"


@dataclass(frozen=True)
class Student:
    """One student: a name and one score per subject (replaces parallel arrays)."""

    name: str
    scores: tuple[int, ...]

    def __post_init__(self) -> None:
        clean = self.name.strip()
        if not clean:
            raise ValueError("name cannot be empty")
        if len(self.scores) != len(SUBJECTS):
            raise ValueError(f"expected {len(SUBJECTS)} scores")
        for s in self.scores:
            if isinstance(s, bool) or not isinstance(s, int) or not 0 <= s <= 100:
                raise ValueError("Score must be between 0 and 100.")
        object.__setattr__(self, "name", clean)  # frozen: bypass to store the trimmed name
        object.__setattr__(self, "scores", tuple(self.scores))

    @property
    def average(self) -> float:
        return sum(self.scores) / len(self.scores)  # "/" is true division, no cast needed

    @property
    def grade(self) -> str:
        return assign_grade(self.average)


@dataclass(frozen=True)
class ClassStats:
    count: int
    class_average: float
    top: Student
    bottom: Student


class GradeBookFullError(Exception):
    """Raised when MAX_STUDENTS is reached."""


@dataclass
class GradeBook:
    students: list[Student] = field(default_factory=list)
    capacity: int = MAX_STUDENTS

    def add(self, name: str, scores: tuple[int, ...] | list[int]) -> Student:
        if len(self.students) >= self.capacity:
            raise GradeBookFullError("Cannot add more students - storage is full.")
        student = Student(name, tuple(scores))  # validates before anything is stored
        self.students.append(student)
        return student

    def find(self, query: str) -> Student | None:
        """First student whose name equals the query, ignoring case."""
        wanted = query.strip().casefold()
        for student in self.students:
            if student.name.casefold() == wanted:
                return student
        return None

    def statistics(self) -> ClassStats | None:
        if not self.students:
            return None
        top = bottom = self.students[0]
        for s in self.students:  # strict comparisons: first student wins ties, like Java
            if s.average > top.average:
                top = s
            if s.average < bottom.average:
                bottom = s
        class_avg = sum(s.average for s in self.students) / len(self.students)
        return ClassStats(len(self.students), class_avg, top, bottom)


# ===== SECTION 2: validation of raw text =====
def parse_score(text: str) -> int:
    """Turn typed text into a 0-100 int, or raise ValueError with the user-facing message."""
    text = text.strip()
    if not _INT_RE.fullmatch(text):  # int() alone would accept "1_0"; Java's nextInt would not
        raise ValueError("That's not a number.")
    value = int(text)
    if not 0 <= value <= 100:
        raise ValueError("Score must be between 0 and 100.")
    return value


def parse_menu_choice(text: str) -> int:
    """Menu number, or -1 for anything that is not an integer."""
    text = text.strip()
    return int(text) if _INT_RE.fullmatch(text) else -1


# ===== SECTION 3: formatting (pure: returns strings) =====
def format_table(students: list[Student]) -> str:
    header = f"{'Name':<15} " + " ".join(f"{s:>8}" for s in SUBJECTS) + f" {'Average':>10}"
    lines = [header, "-" * 55]
    for st in students:
        cells = " ".join(f"{sc:>8d}" for sc in st.scores)
        lines.append(f"{st.name:<15} {cells} {st.average:>10.2f}")
    return "\n".join(lines)


def format_student(st: Student) -> str:
    scores = " | ".join(f"{sub}: {sc}" for sub, sc in zip(SUBJECTS, st.scores))
    return "\n".join([
        "--- Student Found ---",
        f"Name: {st.name}",
        scores,
        f"Average: {st.average:.2f} | Grade: {st.grade}",
    ])


def format_statistics(stats: ClassStats) -> str:
    return "\n".join([
        "--- Class Statistics ---",
        f"Total students: {stats.count}",
        f"Class average: {stats.class_average:.2f} (Grade: {assign_grade(stats.class_average)})",
        f"Top performer: {stats.top.name} ({stats.top.average:.2f})",
        f"Needs support: {stats.bottom.name} ({stats.bottom.average:.2f})",
    ])


MENU = "\n".join([
    "=========================================",
    "   STUDENT GRADE MANAGEMENT SYSTEM",
    "=========================================",
    "1. Add Student",
    "2. View All Students",
    "3. Search Student by Name",
    "4. Class Statistics (avg/highest/lowest)",
    "5. Exit",
])


# ===== SECTION 4: interactive layer =====
Reader = Callable[[str], str]
Writer = Callable[[str], None]


def read_valid_score(subject: str, read: Reader, write: Writer) -> int:
    while True:
        try:
            return parse_score(read(f"Enter {subject} score (0-100): "))
        except ValueError as err:
            write(str(err))


def add_student(book: GradeBook, read: Reader, write: Writer) -> None:
    if len(book.students) >= book.capacity:
        write("Cannot add more students - storage is full.")
        return
    name = read("Enter student name: ").strip()
    if not name:
        write("name cannot be empty. Student not added.")
        return
    scores = tuple(read_valid_score(sub, read, write) for sub in SUBJECTS)
    student = book.add(name, scores)
    write(f"Student '{student.name}' added successfully.")


def search_student(book: GradeBook, read: Reader, write: Writer) -> None:
    if not book.students:
        write("No students to search.")
        return
    found = book.find(read("Enter name to search: "))
    write(format_student(found) if found else "No student found with that name.")


def run(read: Reader = input, write: Writer = print, book: GradeBook | None = None) -> GradeBook:
    """Menu loop. `read(prompt)` returns a line; `write(text)` shows a line."""
    book = book if book is not None else GradeBook()
    while True:
        write(MENU)
        choice = parse_menu_choice(read("Choose an option (1-5): "))
        if choice == 1:
            add_student(book, read, write)
        elif choice == 2:
            write(format_table(book.students) if book.students else "No students recorded yet.")
        elif choice == 3:
            search_student(book, read, write)
        elif choice == 4:
            stats = book.statistics()
            write(format_statistics(stats) if stats else "No students recorded yet.")
        elif choice == 5:
            write("Goodbye!")
            return book
        else:
            write("Invalid Option. Try again!")
        write("")


def main() -> None:
    try:
        run()
    except EOFError:  # stdin closed (piped input ran out): exit cleanly instead of a traceback
        print("\nInput ended. Goodbye!")


if __name__ == "__main__":
    main()
