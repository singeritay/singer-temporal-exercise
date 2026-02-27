import asyncio

from calculator.constants import MathTaskQueue
from calculator.workflows.calculator_workflow import CalculatorWorkflow
from temporal_infra import TemporalWorker

calculator_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.ORCHESTRATOR.value, workflows=[CalculatorWorkflow])

if __name__ == '__main__':
    asyncio.run(calculator_worker.run())