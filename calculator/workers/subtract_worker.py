import asyncio

from calculator.activities.math_activities import subtract
from calculator.constants import MathTaskQueue
from temporal_infra import TemporalWorker

subtract_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.SUBTRACT.value, activities=[subtract])

if __name__ == '__main__':
    asyncio.run(subtract_worker.run())