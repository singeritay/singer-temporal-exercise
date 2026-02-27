import asyncio
import uuid
from timeit import timeit

from calculator.constants import MathTaskQueue
from calculator.workflows.calculator_workflow import CalculatorWorkflow
from temporal_infra import TemporalClient


async def get_result():
    return await TemporalClient().run_workflow(CalculatorWorkflow.run, ["7+30"], id=str(uuid.uuid4()),
                                               task_queue=MathTaskQueue.ORCHESTRATOR.value)


async def main():
    # results = []
    # for i in range(100_000):
    #     result = get_result()
    #     results.append(result)
    # await asyncio.gather(*results)
    await get_result()


if __name__ == '__main__':
    import time

    start_time = time.perf_counter()
    asyncio.run(main())
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    print(elapsed_time)
