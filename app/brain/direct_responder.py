"""Deterministic direct replies for common low-risk prompts."""
from __future__ import annotations

import ast
import operator
import re
from collections.abc import Callable
from typing import Any

_MAX_EXPR_LENGTH = 80
_MAX_ABS_VALUE = 1_000_000_000

_OPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def try_direct_reply(message: str) -> str | None:
    """Return a deterministic JARVIS-style reply when no model call is needed."""
    arithmetic = _extract_arithmetic(message)
    if arithmetic is None:
        return None

    try:
        value = _safe_eval(arithmetic)
    except (ArithmeticError, ValueError, SyntaxError):
        return None

    return f"{_format_number(value)}, sir."


def _extract_arithmetic(message: str) -> str | None:
    text = message.strip().lower()
    text = re.sub(r"^(jarvis[, ]+)?", "", text)
    text = re.sub(r"^(what is|what's|calculate|compute|solve)\s+", "", text)
    text = text.rstrip(" ?.")

    if not text or len(text) > _MAX_EXPR_LENGTH:
        return None
    if not re.fullmatch(r"[0-9+\-*/%().\s]+", text):
        return None
    if not re.search(r"\d\s*[+\-*/%]\s*\d", text):
        return None

    return text


def _safe_eval(expression: str) -> float:
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body)


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise ValueError("Unsupported constant.")
        return _bounded(float(node.value))

    if isinstance(node, ast.BinOp):
        op = _OPS.get(type(node.op))
        if op is None:
            raise ValueError("Unsupported operator.")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _bounded(op(left, right))

    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError("Unsupported unary operator.")
        return _bounded(op(_eval_node(node.operand)))

    raise ValueError("Unsupported expression.")


def _bounded(value: float) -> float:
    if abs(value) > _MAX_ABS_VALUE:
        raise ValueError("Expression result is too large.")
    return value


def _format_number(value: Any) -> str:
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"
