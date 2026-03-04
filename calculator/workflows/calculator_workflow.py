import re
from datetime import timedelta
from typing import List, Tuple

from temporalio import workflow

from calculator.activities.math_activities import add, power, multiply, divide, subtract
from calculator.constants import MathTaskQueue

OPERATORS = {
    "^": (power, MathTaskQueue.POWER.value),
    "*": (multiply, MathTaskQueue.MULTIPLY.value),
    "/": (divide, MathTaskQueue.DIVIDE.value),
    "+": (add, MathTaskQueue.ADD.value),
    "-": (subtract, MathTaskQueue.SUBTRACT.value),
}


@workflow.defn
class CalculatorWorkflow:
    @workflow.run
    async def run(self, expression: str) -> float:
        return await self.calculate_expression(expression)

    async def calculate_expression(self, expression: str):
        elements = self._split_expression_to_elements(expression)
        while "(" in elements:
            open_idx, close_idx = self._find_parenthesis_indexes(elements)
            sub_expr = elements[open_idx + 1: close_idx]
            sub_result = await self._calculate_flat_expression(sub_expr)
            elements[open_idx: close_idx + 1] = [sub_result]

        return await self._calculate_flat_expression(elements)

    @staticmethod
    def _find_parenthesis_indexes(elements: List) -> Tuple[int, int]:
        close_idx = elements.index(")")
        for i in range(close_idx - 1, -1, -1):
            if elements[i] == "(":
                return i, close_idx

        raise ValueError(f"Bad math expression: mismatched parenthesis")


    async def _calculate_flat_expression(self, elements: List[str | int | float]):
        if elements[0] == "-":
            elements.insert(0, 0.0)
        for op_symbols in [["^"], ["*", "/"], ["+", "-"]]:
            i = 0
            while i < len(elements):
                if elements[i] in op_symbols:
                    if i == 0 or i == len(elements) - 1:
                        raise ValueError(f"Bad math expression: Operator {elements[i]} at edge.")
                    symbol = elements[i]
                    result = await self._run_basic_calculation(symbol, elements[i - 1], elements[i + 1])
                    elements[i - 1: i + 2] = [result]
                    i -= 1
                i += 1
        return float(elements[0])

    @staticmethod
    async def _run_basic_calculation(symbol: str, first_element: float, second_element: float) -> float:
        activity_fn, queue_name = OPERATORS.get(symbol)
        result = await workflow.execute_activity(
            activity_fn,
            args=[float(first_element), float(second_element)],
            task_queue=queue_name,
            start_to_close_timeout=timedelta(seconds=10)
        )
        return result

    @staticmethod
    def _split_expression_to_elements(expression: str) -> List[str | float]:
        elements = []
        expression = expression.replace(" ", "")
        raw_elements = re.findall(r'\d+\.?\d*|[\+\-\*\/\^\(\)]', expression)
        for x in raw_elements:
            if x[0].isdigit() or (len(x) > 1 and x[1].isdigit()):
                elements.append(float(x))
            else:
                elements.append(x)
        return elements
