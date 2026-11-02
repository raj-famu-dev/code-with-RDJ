# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""pytest tests for calculator.py."""
import pytest

import calculator as calc


def make_io(lines):
    it = iter(lines)
    out: list[str] = []
    return (lambda prompt: next(it)), out.append, out


@pytest.mark.parametrize("expr,expected", [
    ("2+3*4", 14), ("(2+3)*4", 20), ("10-4-3", 3), ("100/10/5", 2),
    ("2^3^2", 512), ("-2^2", -4), ("2^-1", 0.5), ("(-2)^2", 4),
    ("--3", 3), ("-(3+4)", -7), ("7%4", 3), ("-7%4", -3), ("2+7%4*2", 8),
    ("sqrt(16)+1", 5), ("sqrt(2+2)*3", 6), (" 1 + 2 ", 3), (".5+.5", 1), ("3.", 3),
    ("2*-3", -6), ("+4", 4),
])
def test_expression_precedence(expr, expected):
    assert calc.evaluate(expr) == pytest.approx(expected)


@pytest.mark.parametrize("expr", ["", "   ", "2+", "*3", "(2+3", "2+3)", "2 3", "abc", "2$3",
                                  "sqrt 4", "sqrt(4", "()", "1..2", "2**3"])
def test_bad_syntax_reports_not_crashes(expr):
    with pytest.raises(calc.CalculatorError):
        calc.evaluate(expr)


@pytest.mark.parametrize("expr,msg", [("1/0", "divide by zero"), ("5%0", "remainder"),
                                      ("sqrt(0-1)", "negative"), ("0^-1", "zero"),
                                      ("(-8)^0.5", "not a real"), ("10^400", "too large"),
                                      ("9" * 400, "too large")])
def test_math_errors(expr, msg):
    with pytest.raises(calc.CalculatorError, match=msg):
        calc.evaluate(expr)


def test_deep_nesting_does_not_crash():
    with pytest.raises(calc.CalculatorError, match="deeply"):
        calc.evaluate("(" * 5000 + "1" + ")" * 5000)


def test_eval_is_not_used_so_code_is_rejected():
    with pytest.raises(calc.CalculatorError):
        calc.evaluate("__import__('os').system('echo hi')")


def test_modulus_sign_follows_dividend_like_java():
    assert calc.modulus(-7, 4) == -3
    assert calc.modulus(7, -4) == 3


def test_percent():
    assert calc.percent(200, 15) == 30


@pytest.mark.parametrize("x,text", [(0.1 + 0.2, "0.3"), (3.0, "3"), (-0.0, "0"),
                                    (1 / 3, "0.333333333333"), (1e20, "1e+20"), (-2.5, "-2.5")])
def test_format_number_hides_float_noise(x, text):
    assert calc.format_number(x) == text


@pytest.mark.parametrize("text", ["nan", "inf", "-inf", "", "abc", "1e5", "1,5", "--1"])
def test_parse_number_rejects(text):
    with pytest.raises(calc.CalculatorError):
        calc.parse_number(text)


def test_parse_number_accepts():
    assert calc.parse_number(" -2.5 ") == -2.5 and calc.parse_number(".5") == 0.5


def test_history_keeps_last_ten_only():
    c = calc.Calculator()
    for i in range(15):
        c.binary("+", i, 1)
    assert len(c.history) == 10
    assert c.history[0].description == "5 + 1" and c.history[-1].result == "15"


def test_failed_calculation_not_recorded():
    c = calc.Calculator()
    with pytest.raises(calc.CalculatorError):
        c.binary("/", 1, 0)
    assert len(c.history) == 0


def test_memory_store_recall_clear():
    c = calc.Calculator()
    with pytest.raises(calc.CalculatorError, match="empty"):
        c.memory_recall()
    c.memory_store(0.0)  # zero is a real value, not "empty"
    assert c.memory_recall() == 0.0
    c.memory_clear()
    assert c.memory is None


def test_cli_flow_errors_do_not_crash_and_loop_continues():
    read, write, out = make_io(["4", "1", "0", "7", "-4", "1", "abc", "1", "0.1", "0.2",
                                "9", "2+3*4", "10", "x", "0"])
    calculator = calc.run(read, write)
    text = "\n".join(out)
    assert "Error: Cannot divide by zero." in text
    assert "Error: Cannot take the square root of a negative number." in text
    assert "Error: That's not a number." in text
    assert "Result: 0.3" in text and "Result: 14" in text
    assert "1. 0.1 + 0.2 = 0.3" in text and "2. 2+3*4 = 14" in text
    assert "Invalid option." in text and "Goodbye!" in text
    assert len(calculator.history) == 2


def test_cli_memory_and_percent():
    read, write, out = make_io(["12", "11", "42", "12", "8", "200", "15", "13", "12", "0"])
    calc.run(read, write)
    text = "\n".join(out)
    assert "Error: Memory is empty." in text and "Memory: 42" in text
    assert "Result: 30" in text and "Memory cleared." in text
    assert text.count("Error: Memory is empty.") == 2
