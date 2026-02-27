import asyncio

from calculator.activities.math_activities import add, subtract, divide, multiply, power
from calculator.constants import MathTaskQueue
from calculator.workflows.calculator_workflow import CalculatorWorkflow
from temporal_infra import TemporalWorker


subtract_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.SUBTRACT.value, activities=[subtract])
multiply_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.MULTIPLY.value, activities=[multiply])
divide_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.DIVIDE.value, activities=[divide])
power_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.POWER.value, activities=[power])

calculator_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.ORCHESTRATOR.value, workflows=[CalculatorWorkflow])
math_workers = [subtract_worker, multiply_worker, divide_worker, power_worker, calculator_worker]

if __name__ == '__main__':
    for worker in math_workers:
        asyncio.run(worker.run())
