import asyncio
import uuid

from calculator.constants import MathTaskQueue
from calculator.workflows.calculator_workflow import CalculatorWorkflow
from temporal_infra import TemporalClient


async def get_result():
    return await TemporalClient().run_workflow(CalculatorWorkflow.run, ["-5 + (2 * (-3)) ^ 2"], id=str(uuid.uuid4()),
                                               task_queue=MathTaskQueue.ORCHESTRATOR.value)


async def main():
    # results = []
    # for i in range(100_000):
    #     result = get_result()
    #     results.append(result)
    # await asyncio.gather(*results)
    return await get_result()


if __name__ == '__main__':
    import time

    start_time = time.perf_counter()
    print(asyncio.run(main()))
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    print(elapsed_time)
