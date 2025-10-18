import asyncio
from util.logging_to_file import Logging

class RecursiveScheduler:
    
    def __init__(self, task_name = "task", sleep_interval: float = 1.0, pre_wait: bool = False):
        self.task_name = task_name
        self.sleep_interval = sleep_interval
        self.pre_wait = pre_wait
        self.task = None

    async def init_work(self):
        raise NotImplementedError()
        
    async def main(self):
        raise NotImplementedError()
        
    def error_handle(self, e: Exception):
        Logging.error(e)
    
    def update_sleep_interval(self):
        return self.sleep_interval

    async def single_run_and_schedule(self):
        try:
            await self.main()
        except Exception as e:
            self.error_handle(e)
        
        self.sleep_interval = self.update_sleep_interval()
        Logging.log(f"{self.task_name} is scheduled after {self.sleep_interval} seconds.")
        await asyncio.sleep(self.sleep_interval)
        asyncio.create_task(self.single_run_and_schedule())

    def callback_handle(self, future: asyncio.Future):
        exception = future.exception()
        if exception:
            if isinstance(exception, asyncio.CancelledError):
                Logging.log(f"Scheduled task {self.task_name} explicitly cancelled and stopped.")
            else:
                Logging.log(f"Scheduled task {self.task_name} failed with unhandled exception: {exception}")
        else:
            Logging.log(f"Scheduled task {self.task_name} finished (unexpected stop).")

    async def start(self):
        if self.task is not None and not self.task.done():
            Logging.log(f"{self.task_name} is scheduled.")
            return

        Logging.log(f"Start Scheduling {self.task_name}")
        await self.init_work()
        if self.pre_wait:
            Logging.log(f"{self.task_name} will start after {self.sleep_interval} seconds")
            await asyncio.sleep(self.sleep_interval)
        self.task = asyncio.create_task(self.single_run_and_schedule())
        self.task.add_done_callback(self.callback_handle)
        
        Logging.log(f"Scheduling {self.task_name} started.")
        return self.task