from enum import StrEnum


class MathTaskQueue(StrEnum):
    ADD = "addition-queue"
    SUBTRACT = "subtraction-queue"
    MULTIPLY = "multiplication-queue"
    DIVIDE = "division-queue"
    POWER = "power-queue"
    ORCHESTRATOR = "calculator-queue"
