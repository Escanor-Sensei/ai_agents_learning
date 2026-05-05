"""
Tool: Calculator
Responsibility: Safely evaluate math expressions.

.NET analogy: A scoped ICalculatorService registered in DI.
The docstring below is read by the LLM to decide WHEN to invoke this tool.
Treat it like an XML doc comment on a public interface — it IS the contract.
"""

import ast
import operator
from langchain_core.tools import tool

# Whitelist of safe operators — avoids arbitrary code execution via eval()
# .NET analogy: input validation / allowlist before processing a request
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _safe_eval(expression: str) -> float:
    """Parse and evaluate a math expression using AST — no exec/eval risk."""
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.n
        if isinstance(node, ast.BinOp):
            op = _SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {node.op}")
            return op(_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            op = _SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {node.op}")
            return op(_eval(node.operand))
        raise ValueError(f"Unsupported expression type: {type(node)}")

    tree = ast.parse(expression, mode="eval")
    return _eval(tree.body)


@tool
def calculator(expression: str) -> str:
    """
    Evaluates a mathematical expression and returns the numeric result.
    Use this tool when the user asks to calculate, compute, add, subtract,
    multiply, divide, or solve any arithmetic problem.
    Input must be a valid math expression string, e.g. '2 + 2', '10 * (3 + 5)', '2 ** 8'.
    Do NOT include units or words — only the math expression itself.
    """
    try:
        result = _safe_eval(expression.strip())
        return str(result)
    except Exception as e:
        return f"Calculator error: {e}"
