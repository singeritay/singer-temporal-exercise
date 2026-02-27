import asyncio
import time

from temporalio import activity


@activity.defn
async def add(a, b):
    # print("Waiting")
    # time.sleep(1)
    await asyncio.sleep(1)
    # print("finished waiting")
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    return a / b


def power(a, b):
    return a ** b
