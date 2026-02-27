from datetime import timedelta
from typing import List

from temporalio import workflow

from calculator.activities.math_activities import add
from calculator.constants import MathTaskQueue


@workflow.defn
class CalculatorWorkflow:
    @workflow.run
    async def run(self, numbers: List[int]):
        add_output = await workflow.execute_activity(
            add,
            args=[1, 5],
            task_queue=MathTaskQueue.ADD.value,
            start_to_close_timeout=timedelta(seconds=30)
        )
        return add_output
