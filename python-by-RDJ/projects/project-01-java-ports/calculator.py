# Completed and verified (run with Python 3.13). Written with Claude (Sonnet 5.5); authorship disclosed.
"""Calculator: a Python port of project-01 (menu calculator, with the expression-parsing extension).

Core: operation functions, a recursive-descent expression parser (correct
precedence, no eval()), a Calculator class with 10-item history and one memory
slot. Errors (divide by zero, sqrt of negative, bad syntax) raise
CalculatorError; the CLI reports them and never crashes.
"""
from __future__ import annotations

import math
import re
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

HISTORY_SIZE = 10


class CalculatorError(ValueError):
    """A user-facing calculation problem (not a program bug)."""


# ===== SECTION 1: operations =====
def _finite(x: float) -> float:
    if not math.isfinite(x):
        raise CalculatorError("Result is too large to represent.")
    return x


def add(a: float, b: float) -> float:
    return _finite(a + b)


def subtract(a: float, b: float) -> float:
    return _finite(a - b)


def multiply(a: float, b: float) -> float:
    return _finite(a * b)


def divide(a: float, b: float) -> float:
    if b == 0:
        raise CalculatorError("Cannot divide by zero.")
    return _finite(a / b)


def modulus(a: float, b: float) -> float:
    """Remainder with the sign of the dividend (Java's %), via fmod, not Python's floor %."""
    if b == 0:
        raise CalculatorError("Cannot take a remainder by zero.")
    return math.fmod(a, b)


def power(a: float, b: float) -> float:
    try:
        return _finite(math.pow(a, b))  # math.pow raises instead of returning complex like **
    except OverflowError:
        raise CalculatorError("Result is too large to represent.") from None
    except ValueError:
        if a == 0 and b < 0:
            raise CalculatorError("Cannot divide by zero (0 to a negative power).") from None
        raise CalculatorError("Negative base with a fractional exponent is not a real number.") from None


def sqrt(a: float) -> float:
    if a < 0:
        raise CalculatorError("Cannot take the square root of a negative number.")
    return math.sqrt(a)


def percent(value: float, pct: float) -> float:
    """pct percent of value: percent(200, 15) == 30."""
    return _finite(value * pct / 100)


BINARY_OPS: dict[str, Callable[[float, float], float]] = {
    "+": add, "-": subtract, "*": multiply, "/": divide, "%": modulus, "^": power,
}


def format_number(x: float) -> str:
    """12 significant digits, so 0.1 + 0.2 shows as 0.3 and -0.0 shows as 0."""
    text = f"{x:.12g}"
    return "0" if text == "-0" else text


# ===== SECTION 2: tokenizer and parser =====
_TOKEN_RE = re.compile(r"\s*(?:(\d+\.?\d*|\.\d+)|(sqrt)|([-+*/%^()]))", re.ASCII)


def tokenize(text: str) -> list[tuple[str, str]]:
    """Return (kind, value) tokens; kinds: num, func, op. Raises CalculatorError on junk."""
    tokens: list[tuple[str, str]] = []
    pos = 0
    text = text.rstrip()
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if not m:
            raise CalculatorError(f"Unexpected character {text[pos:].lstrip()[0]!r}.")
        if m.group(1) is not None:
            tokens.append(("num", m.group(1)))
        elif m.group(2) is not None:
            tokens.append(("func", "sqrt"))
        else:
            tokens.append(("op", m.group(3)))
        pos = m.end()
    return tokens


class _Parser:
    """Grammar (lowest to highest precedence):
        expr   := term (('+' | '-') term)*
        term   := unary (('*' | '/' | '%') unary)*
        unary  := ('-' | '+') unary | power
        power  := atom ('^' unary)?          right-associative; -2^2 == -(2^2)
        atom   := NUMBER | '(' expr ')' | 'sqrt' '(' expr ')'
    """

    def __init__(self, tokens: list[tuple[str, str]]) -> None:
        self.tokens = tokens
        self.i = 0

    def _peek(self) -> tuple[str, str] | None:
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def _take_op(self, *ops: str) -> str | None:
        tok = self._peek()
        if tok and tok[0] == "op" and tok[1] in ops:
            self.i += 1
            return tok[1]
        return None

    def parse(self) -> float:
        if not self.tokens:
            raise CalculatorError("Empty expression.")
        value = self._expr()
        if self._peek() is not None:
            raise CalculatorError(f"Unexpected {self._peek()[1]!r}.")
        return value

    def _expr(self) -> float:
        value = self._term()
        while (op := self._take_op("+", "-")):
            value = BINARY_OPS[op](value, self._term())
        return value

    def _term(self) -> float:
        value = self._unary()
        while (op := self._take_op("*", "/", "%")):
            value = BINARY_OPS[op](value, self._unary())
        return value

    def _unary(self) -> float:
        if (op := self._take_op("-", "+")):
            inner = self._unary()
            return -inner if op == "-" else inner
        return self._power()

    def _power(self) -> float:
        base = self._atom()
        if self._take_op("^"):
            return power(base, self._unary())
        return base

    def _atom(self) -> float:
        tok = self._peek()
        if tok is None:
            raise CalculatorError("Expression ended unexpectedly.")
        kind, val = tok
        self.i += 1
        if kind == "num":
            return _finite_literal(float(val))
        if kind == "func":
            if not self._take_op("("):
                raise CalculatorError("sqrt must be followed by '('.")
            arg = self._expr()
            if not self._take_op(")"):
                raise CalculatorError("Missing ')'.")
            return sqrt(arg)
        if val == "(":
            inner = self._expr()
            if not self._take_op(")"):
                raise CalculatorError("Missing ')'.")
            return inner
        raise CalculatorError(f"Unexpected {val!r}.")


def _finite_literal(x: float) -> float:
    if not math.isfinite(x):
        raise CalculatorError("Number is too large.")
    return x


def evaluate(expression: str) -> float:
    """Evaluate an arithmetic expression safely (no eval())."""
    try:
        return _Parser(tokenize(expression)).parse()
    except RecursionError:
        raise CalculatorError("Expression is nested too deeply.") from None


_NUMBER_RE = re.compile(r"[+-]?(\d+\.?\d*|\.\d+)", re.ASCII)


def parse_number(text: str) -> float:
    """Typed text to float. Rejects 'nan', 'inf' and blanks, which float() would accept."""
    text = text.strip()
    if not _NUMBER_RE.fullmatch(text):
        raise CalculatorError("That's not a number.")
    return _finite_literal(float(text))


# ===== SECTION 3: stateful calculator =====
@dataclass(frozen=True)
class HistoryEntry:
    description: str
    result: str


class Calculator:
    """Keeps the last HISTORY_SIZE successful calculations and one memory value."""

    def __init__(self) -> None:
        self.history: deque[HistoryEntry] = deque(maxlen=HISTORY_SIZE)  # oldest drops when full
        self.memory: float | None = None
        self.last_result: float | None = None

    def _record(self, description: str, result: float) -> float:
        self.history.append(HistoryEntry(description, format_number(result)))
        self.last_result = result
        return result

    def binary(self, symbol: str, a: float, b: float) -> float:
        result = BINARY_OPS[symbol](a, b)
        return self._record(f"{format_number(a)} {symbol} {format_number(b)}", result)

    def sqrt(self, a: float) -> float:
        return self._record(f"sqrt({format_number(a)})", sqrt(a))

    def percent(self, value: float, pct: float) -> float:
        return self._record(f"{format_number(pct)}% of {format_number(value)}", percent(value, pct))

    def evaluate(self, expression: str) -> float:
        return self._record(expression.strip(), evaluate(expression))

    def memory_store(self, value: float) -> None:
        self.memory = value

    def memory_recall(self) -> float:
        if self.memory is None:
            raise CalculatorError("Memory is empty.")
        return self.memory

    def memory_clear(self) -> None:
        self.memory = None


# ===== SECTION 4: interactive layer =====
Reader = Callable[[str], str]
Writer = Callable[[str], None]

MENU = """\
===== CALCULATOR =====
1. Add          2. Subtract     3. Multiply
4. Divide       5. Modulus      6. Power
7. Square root  8. Percentage   9. Evaluate expression
10. History     11. Memory store  12. Memory recall  13. Memory clear
0. Exit"""

_SYMBOLS = {"1": "+", "2": "-", "3": "*", "4": "/", "5": "%", "6": "^"}


def run(read: Reader = input, write: Writer = print, calc: Calculator | None = None) -> Calculator:
    calc = calc or Calculator()
    while True:
        write(MENU)
        choice = read("Choose an option: ").strip()
        try:
            if choice == "0":
                write("Goodbye!")
                return calc
            if choice in _SYMBOLS:
                a = parse_number(read("First number: "))
                b = parse_number(read("Second number: "))
                write("Result: " + format_number(calc.binary(_SYMBOLS[choice], a, b)))
            elif choice == "7":
                write("Result: " + format_number(calc.sqrt(parse_number(read("Number: ")))))
            elif choice == "8":
                value = parse_number(read("Value: "))
                pct = parse_number(read("Percent: "))
                write("Result: " + format_number(calc.percent(value, pct)))
            elif choice == "9":
                write("Result: " + format_number(calc.evaluate(read("Expression: "))))
            elif choice == "10":
                if not calc.history:
                    write("No history yet.")
                for n, entry in enumerate(calc.history, 1):
                    write(f"{n}. {entry.description} = {entry.result}")
            elif choice == "11":
                calc.memory_store(parse_number(read("Value to store: ")))
                write("Stored.")
            elif choice == "12":
                write("Memory: " + format_number(calc.memory_recall()))
            elif choice == "13":
                calc.memory_clear()
                write("Memory cleared.")
            else:
                write("Invalid option.")
        except CalculatorError as err:
            write(f"Error: {err}")
        write("")


def main() -> None:
    try:
        run()
    except EOFError:
        print("\nInput ended. Goodbye!")


if __name__ == "__main__":
    main()
