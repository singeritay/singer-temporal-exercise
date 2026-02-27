import asyncio
import time

from temporalio import activity


@activity.defn
async def add(a, b):
    return a + b


@activity.defn
async def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    return a / b


def power(a, b):
    return a ** b
