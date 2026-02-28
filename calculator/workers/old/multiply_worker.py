import asyncio

from calculator.activities.math_activities import multiply
from calculator.constants import MathTaskQueue
from temporal_infra import TemporalWorker

multiply_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.MULTIPLY.value, activities=[multiply])

if __name__ == '__main__':
    asyncio.run(multiply_worker.run())