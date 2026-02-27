import asyncio

from calculator.activities.math_activities import divide
from calculator.constants import MathTaskQueue
from temporal_infra import TemporalWorker

divide_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.DIVIDE.value, activities=[divide])

if __name__ == '__main__':
    asyncio.run(divide_worker.run())