"""Core scheduler setup for Dreema.

This module configures Celery with Redis broker and backend settings,
and provides helpers for running async jobs within Celery tasks.
"""

from celery import Celery
from dreema.helpers import getenv
import asyncio

REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = getenv("REDIS_PASSWORD", "")
REDIS_AUTH = f":{REDIS_PASSWORD}@" if REDIS_PASSWORD else ""

# Redis DB 1 for broker, DB 2 for result backend
broker = f"redis://{REDIS_AUTH}{REDIS_HOST}:{REDIS_PORT}/1"
backend = f"redis://{REDIS_AUTH}{REDIS_HOST}:{REDIS_PORT}/2"

scheduler = Celery("dreema", broker=broker, backend=backend)

scheduler.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    broker_connection_max_retries=30,
)


def runAsyncJob(coroutine):
    """Run an async coroutine from within a Celery task."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Use Thread-safe future blocking
        return asyncio.run_coroutine_threadsafe(coroutine, loop).result()
    else:
        return asyncio.run(coroutine)


def configureBeatSchedule(beat_schedule: dict):
    """Configure the Celery beat schedule with the provided schedule dict."""
    scheduler.conf.beat_schedule = beat_schedule
