# Tags: #Python #Project #JavaToPython #Tests #grademanager | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""pytest tests for grade_manager.py."""
import pytest

import grade_manager as gm


def make_io(lines):
    it = iter(lines)
    out: list[str] = []
    return (lambda prompt: next(it)), out.append, out


@pytest.mark.parametrize("avg,grade", [(100, "A"), (90, "A"), (89.99, "B"), (80, "B"),
                                       (70, "C"), (60, "D"), (59.99, "F"), (0, "F")])
def test_assign_grade_boundaries(avg, grade):
    assert gm.assign_grade(avg) == grade


def test_student_average_is_true_division():
    assert gm.Student("Ada", (90, 80, 71)).average == pytest.approx(80.3333333)


@pytest.mark.parametrize("name,scores", [("", (1, 2, 3)), ("   ", (1, 2, 3)),
                                         ("A", (101, 0, 0)), ("A", (-1, 0, 0)),
                                         ("A", (1, 2)), ("A", (True, 1, 1))])
def test_student_rejects_bad_data(name, scores):
    with pytest.raises(ValueError):
        gm.Student(name, scores)


def test_student_trims_name_and_accepts_bounds():
    s = gm.Student("  Ada  ", (0, 100, 50))
    assert s.name == "Ada"


@pytest.mark.parametrize("text,value", [("0", 0), ("100", 100), (" 55 ", 55), ("+7", 7)])
def test_parse_score_ok(text, value):
    assert gm.parse_score(text) == value


@pytest.mark.parametrize("text", ["abc", "", "85.5", "1_0", "1e2", "٣"])
def test_parse_score_not_a_number(text):
    with pytest.raises(ValueError, match="not a number"):
        gm.parse_score(text)


@pytest.mark.parametrize("text", ["-1", "101", "999"])
def test_parse_score_out_of_range(text):
    with pytest.raises(ValueError, match="between 0 and 100"):
        gm.parse_score(text)


def test_find_is_case_insensitive_and_trims():
    book = gm.GradeBook()
    book.add("Ada Lovelace", (1, 2, 3))
    assert book.find("  ADA lovelace ").name == "Ada Lovelace"
    assert book.find("Bob") is None


def test_find_returns_first_duplicate():
    book = gm.GradeBook()
    book.add("Sam", (10, 10, 10))
    book.add("sam", (90, 90, 90))
    assert book.find("SAM").scores == (10, 10, 10)


def test_statistics_empty_and_values():
    book = gm.GradeBook()
    assert book.statistics() is None
    book.add("Ada", (90, 80, 70))
    book.add("Lin", (60, 70, 80))
    stats = book.statistics()
    assert stats.count == 2 and stats.class_average == 75.0
    assert stats.top.name == "Ada" and stats.top.average == 80
    assert stats.bottom.name == "Lin"


def test_statistics_tie_first_wins_and_single_student():
    book = gm.GradeBook()
    book.add("A", (70, 70, 70))
    book.add("B", (70, 70, 70))
    stats = book.statistics()
    assert stats.top.name == "A" and stats.bottom.name == "A"


def test_capacity_enforced():
    book = gm.GradeBook(capacity=2)
    book.add("A", (1, 1, 1))
    book.add("B", (1, 1, 1))
    with pytest.raises(gm.GradeBookFullError):
        book.add("C", (1, 1, 1))
    assert len(book.students) == 2


def test_failed_add_stores_nothing():
    book = gm.GradeBook()
    with pytest.raises(ValueError):
        book.add("A", (1, 2, 500))
    assert book.students == []


def test_table_uses_correct_subject_labels_and_aligns():
    book = gm.GradeBook()
    book.add("Ada", (90, 80, 70))
    table = gm.format_table(book.students)
    header = table.splitlines()[0]
    assert "Physics" in header and "Biology" in header
    assert "Science" not in table and "English" not in table
    assert table.splitlines()[2].endswith("80.00")


def test_menu_flow_add_view_search_stats_exit():
    read, write, out = make_io(["1", "Ada", "90", "80", "70", "2", "3", "ada", "4", "5"])
    book = gm.run(read, write)
    text = "\n".join(out)
    assert "Student 'Ada' added successfully." in text
    assert "--- Student Found ---" in text and "Grade: B" in text
    assert "Class average: 80.00 (Grade: B)" in text
    assert text.count("Goodbye!") == 1
    assert len(book.students) == 1


def test_menu_validation_retries():
    read, write, out = make_io(["1", "Bob", "abc", "150", "-3", "50", "60", "70", "5"])
    book = gm.run(read, write)
    text = "\n".join(out)
    assert "That's not a number." in text
    assert text.count("Score must be between 0 and 100.") == 2
    assert book.students[0].scores == (50, 60, 70)


def test_menu_blank_name_and_invalid_options_and_empty_messages():
    read, write, out = make_io(["1", "   ", "x", "9", "2", "3", "4", "5"])
    book = gm.run(read, write)
    text = "\n".join(out)
    assert "name cannot be empty. Student not added." in text
    assert text.count("Invalid Option. Try again!") == 2
    assert "No students recorded yet." in text and "No students to search." in text
    assert book.students == []


def test_menu_search_not_found():
    read, write, out = make_io(["1", "Ada", "1", "1", "1", "3", "zed", "5"])
    gm.run(read, write)
    assert "No student found with that name." in "\n".join(out)


def test_menu_full_storage_message():
    book = gm.GradeBook(capacity=1)
    book.add("A", (1, 1, 1))
    read, write, out = make_io(["1", "5"])
    gm.run(read, write, book)
    assert "storage is full" in "\n".join(out)
