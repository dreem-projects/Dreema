"""Task decorator utilities for Dreema scheduler."""

from scheduler.setup import scheduler, runAsyncJob

def createTask(name: str):
    """
    Decorator factory to create a named Celery task.
    
    Example:
        @createTask("MyTaskName")
        def myTask():
            pass
    """
    return scheduler.task(name=name)


def createAsyncTask(name: str):
    """
    Decorator factory to create a named Celery task that runs an async function.
    
    Example:
        @createAsyncTask("MyAsyncTask")
        async def myTask():
            await someAsyncOperation()
    """
    def decorator(func):
        @scheduler.task(name=name)
        def wrapper(*args, **kwargs):
            async def run():
                return await func(*args, **kwargs)
            return runAsyncJob(run())
        return wrapper
    return decorator


@scheduler.task(name="CallbackScheduler")
def CallbackScheduler(job, *args, **kwargs):
    """
    Generic callback scheduler for running arbitrary async jobs.
    """
    async def run():
        await job(*args, **kwargs)
    runAsyncJob(run())
