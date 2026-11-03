# Tags: #Python #Project #JavaToPython #Tests #todoapp | @rdj_369 | Python 3.13
# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""pytest tests for todo_app.py."""
from datetime import date

import pytest

import todo_app as td

TODAY = date(2026, 6, 15)


def make_io(lines):
    it = iter(lines)
    out: list[str] = []
    return (lambda prompt: next(it)), out.append, out


@pytest.fixture
def mgr():
    m = td.TaskManager()
    m.add("Write report", td.Priority.HIGH, date(2026, 6, 10))   # 1 overdue
    m.add("buy milk", td.Priority.LOW)                            # 2
    m.add("Call Bob", td.Priority.MEDIUM, date(2026, 6, 20))     # 3
    m.add("Alpha task", td.Priority.HIGH, date(2026, 6, 10))     # 4
    return m


@pytest.mark.parametrize("text,p", [("low", td.Priority.LOW), (" HIGH ", td.Priority.HIGH),
                                    ("2", td.Priority.MEDIUM), ("Medium", td.Priority.MEDIUM)])
def test_priority_parse(text, p):
    assert td.Priority.parse(text) is p


@pytest.mark.parametrize("text", ["", "urgent", "0", "4", "-1", "1.5"])
def test_priority_parse_rejects(text):
    with pytest.raises(ValueError):
        td.Priority.parse(text)


def test_parse_due():
    assert td.parse_due("") is None and td.parse_due(" None ") is None
    assert td.parse_due("2026-02-03") == date(2026, 2, 3)
    for bad in ["2026-02-30", "tomorrow", "02/03/2026", "2026-13-01"]:
        with pytest.raises(ValueError):
            td.parse_due(bad)


def test_add_rejects_blank_title_and_does_not_burn_an_id():
    m = td.TaskManager()
    with pytest.raises(ValueError):
        m.add("   ")
    assert m.add("ok").id == 1 and len(m) == 1


def test_ids_never_reused_after_delete():
    m = td.TaskManager()
    a, b = m.add("a"), m.add("b")
    m.delete(b.id)
    c = m.add("c")
    assert c.id == 3 and [t.id for t in m.list_tasks()] == [a.id, c.id]


def test_unknown_id_everywhere(mgr):
    for call in (lambda: mgr.get(99), lambda: mgr.set_done(99), lambda: mgr.delete(99),
                 lambda: mgr.edit(99, title="x")):
        with pytest.raises(td.TaskNotFoundError, match="99"):
            call()


def test_mark_done_and_not_done_and_filters(mgr):
    mgr.set_done(2)
    assert [t.id for t in mgr.list_tasks(done=True)] == [2]
    assert [t.id for t in mgr.list_tasks(done=False)] == [1, 3, 4]
    assert [t.id for t in mgr.list_tasks(priority=td.Priority.HIGH)] == [1, 4]
    assert [t.id for t in mgr.list_tasks(done=False, priority=td.Priority.HIGH)] == [1, 4]
    mgr.set_done(2, False)
    assert mgr.list_tasks(done=True) == []


def test_edit_partial_and_clear_due(mgr):
    mgr.edit(1, title="  New  ")
    t = mgr.get(1)
    assert t.title == "New" and t.priority is td.Priority.HIGH and t.due == date(2026, 6, 10)
    mgr.edit(1, due=None)  # None means "clear", UNSET means "leave alone"
    assert mgr.get(1).due is None
    mgr.edit(1, priority=td.Priority.LOW)
    assert mgr.get(1).priority is td.Priority.LOW and mgr.get(1).title == "New"


def test_edit_blank_title_changes_nothing(mgr):
    with pytest.raises(ValueError):
        mgr.edit(1, title="  ", priority=td.Priority.LOW)
    assert mgr.get(1).title == "Write report" and mgr.get(1).priority is td.Priority.HIGH


def test_sort_by_priority_ties_by_id(mgr):
    assert [t.id for t in mgr.sorted_tasks("priority")] == [1, 4, 3, 2]


def test_sort_by_due_none_last(mgr):
    assert [t.id for t in mgr.sorted_tasks("due")] == [1, 4, 3, 2]


def test_sort_by_title_case_insensitive(mgr):
    assert [t.title for t in mgr.sorted_tasks("title")] == ["Alpha task", "buy milk", "Call Bob", "Write report"]


def test_sort_does_not_reorder_storage_and_rejects_bad_key(mgr):
    mgr.sorted_tasks("title")
    assert [t.id for t in mgr.list_tasks()] == [1, 2, 3, 4]
    with pytest.raises(ValueError):
        mgr.sorted_tasks("colour")


def test_search_case_insensitive_substring(mgr):
    assert [t.id for t in mgr.search("BOB")] == [3]
    assert [t.id for t in mgr.search("task")] == [4]
    assert mgr.search("zzz") == []


def test_summary_counts_overdue_only_when_not_done(mgr):
    s = mgr.summary(TODAY)
    assert (s.total, s.done, s.overdue) == (4, 0, 2)
    assert s.by_priority == {td.Priority.LOW: 1, td.Priority.MEDIUM: 1, td.Priority.HIGH: 2}
    mgr.set_done(1)
    assert mgr.summary(TODAY).overdue == 1 and mgr.summary(TODAY).done == 1


def test_due_today_is_not_overdue():
    m = td.TaskManager()
    m.add("x", due=TODAY)
    assert m.summary(TODAY).overdue == 0


def test_clear_done_deletes_safely_while_iterating(mgr):
    mgr.set_done(1)
    mgr.set_done(3)
    assert mgr.clear_done() == 2
    assert [t.id for t in mgr.list_tasks()] == [2, 4]


def test_naive_delete_while_looping_raises():
    d = {1: "a", 2: "b"}
    with pytest.raises(RuntimeError):
        for k in d:
            del d[k]


def test_task_equality_by_id_and_hashable():
    a = td.Task(1, "x")
    b = td.Task(1, "different")
    assert a == b and len({a, b}) == 1 and a != td.Task(2, "x")


def test_format_tasks_marks_overdue_and_empty(mgr):
    assert td.format_tasks([]) == "No tasks to show."
    text = td.format_tasks(mgr.list_tasks(), TODAY)
    assert text.count("OVERDUE") == 2 and "[ ]" in text


def test_cli_flow():
    read, write, out = make_io([
        "1", "Pay rent", "high", "2026-06-01",
        "1", "  ", "", "",            # blank title -> error
        "1", "Read", "urgent", "",    # bad priority -> error
        "1", "Read", "", "31/12/2026",  # bad date -> error
        "1", "Read book", "", "",
        "2", "open", "high",
        "3", "1", "3", "abc", "6", "42",
        "5", "2", "", "low", "2026-07-01",
        "7", "priority", "8", "BOOK", "9", "x", "0"])
    mgr = td.run(read, write, TODAY)
    text = "\n".join(out)
    assert "Added task 1: Pay rent" in text and "Added task 2: Read book" in text
    assert text.count("Error: Title cannot be blank.") == 1
    assert "Error: Priority must be one of" in text and "Error: Due date must look like" in text
    assert "Task 1 marked done." in text and "Task id must be a whole number." in text
    assert "No task with id 42." in text and "Task 2 updated." in text
    assert "Total: 2 | Done: 1 | Overdue: 0" in text and "Invalid option." in text
    assert mgr.get(2).priority is td.Priority.LOW and mgr.get(2).due == date(2026, 7, 1)
    assert mgr.get(2).title == "Read book"


def test_cli_delete_then_add_does_not_reuse_id():
    read, write, out = make_io(["1", "a", "", "", "6", "1", "1", "b", "", "", "0"])
    mgr = td.run(read, write, TODAY)
    assert [t.id for t in mgr.list_tasks()] == [2]
