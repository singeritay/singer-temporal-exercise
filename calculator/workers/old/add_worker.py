import asyncio

from calculator.activities.math_activities import add
from calculator.constants import MathTaskQueue
from temporal_infra import TemporalWorker

add_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.ADD.value, activities=[add])

if __name__ == '__main__':
    asyncio.run(add_worker.run())