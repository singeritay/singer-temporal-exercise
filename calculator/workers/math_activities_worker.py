import asyncio

from calculator.activities.math_activities import add, subtract, divide, multiply, power
from temporal_infra import TemporalWorker

math_activities_worker = TemporalWorker(activities=[add, subtract, divide, multiply, power], use_prometheus_server=True)

if __name__ == '__main__':
    asyncio.run(math_activities_worker.run())
