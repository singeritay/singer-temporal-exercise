from temporalio import activity


@activity.defn
async def add(a, b):
    activity.logger.info(f'adding {a} to {b}')
    return a + b


@activity.defn
async def subtract(a, b):
    activity.logger.info(f'subtracting {b} from {a}')
    return a - b


@activity.defn
async def multiply(a, b):
    activity.logger.info(f'multiplying {a} by {b}')
    return a * b


@activity.defn
async def divide(a, b):
    activity.logger.info(f'dividing {a} by {b}')
    return a / b


@activity.defn
async def power(a, b):
    activity.logger.info(f'powering {a} by {b}')
    return a ** b
