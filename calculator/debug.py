import asyncio

from calculator.workflows.calculator_workflow import CalculatorWorkflow

async def run_basi_replace(s, a, b):
    return eval(f"{a}{s.replace('^', '**')}{b}")

async def debug():
    calc = CalculatorWorkflow()
    calc._run_basic_calculation = run_basi_replace
    edge_case_expressions = [
        "-5 + (2 * (-3)) ^ 2",
    ]
    for expression in edge_case_expressions:
        result = await calc.calculate_expression(expression)
        correct_result = eval(expression.replace("^", "**"))
        print(result)
        if result == correct_result:
            print('YES')
        else:
            print(f'NO -> {expression} got {result}, should have goe {correct_result}')

if __name__ == '__main__':

    asyncio.run(debug())