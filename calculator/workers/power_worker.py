import asyncio

from calculator.activities.math_activities import power
from calculator.constants import MathTaskQueue
from temporal_infra import TemporalWorker

power_worker = TemporalWorker(tasks_queue_name=MathTaskQueue.POWER.value, activities=[power])

if __name__ == '__main__':
    asyncio.run(power_worker.run())