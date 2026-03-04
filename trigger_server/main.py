import uuid

from fastapi import FastAPI, HTTPException, Query

from calculator.constants import MathTaskQueue
from calculator.workflows.calculator_workflow import CalculatorWorkflow
from temporal_infra import TemporalClient

app = FastAPI(title="Trigger Server", version="1.0.0")


@app.get("/calculate")
async def calculate(expression: str = Query(..., min_length=1)) -> dict[str, float | str]:
    try:
        result = await TemporalClient().run_workflow(
            CalculatorWorkflow.run,
            [expression],
            id=str(uuid.uuid4()),
            task_queue=MathTaskQueue.ORCHESTRATOR.value,
        )
        return {"expression": expression, "result": float(result)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to calculate expression: {exc}") from exc
