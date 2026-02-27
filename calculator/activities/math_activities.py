from temporalio import activity


@activity.defn
async def add(a, b):
    return a + b


@activity.defn
async def subtract(a, b):
    return a - b


@activity.defn
def multiply(a, b):
    return a * b


@activity.defn
def divide(a, b):
    return a / b


@activity.defn
def power(a, b):
    return a ** b
