import asyncio

from calculator.activities.math_activities import add, subtract, divide, multiply, power
from temporal_infra import TemporalWorker

subtract_worker = TemporalWorker(activities=[add, subtract, divide, multiply, power])

if __name__ == '__main__':
    asyncio.run(subtract_worker.run())
