import asyncio
from ..util.logging_standard import DefaultLogger as Logging
from ..util.session_context import SessionIDHelper

logger = Logging.getLogger("recursive_scheduler")

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
        logger.error(e)
    
    def update_sleep_interval(self):
        return self.sleep_interval

    async def single_run_and_schedule(self):
        session = SessionIDHelper()
        session.create_session_id()
        try:
            await self.main()
        except Exception as e:
            self.error_handle(e)
        finally:
            session.reset_session_id()
        
        self.sleep_interval = self.update_sleep_interval()
        logger.info(f"{self.task_name} is scheduled after {self.sleep_interval} seconds.")
        await asyncio.sleep(self.sleep_interval)
        self.task = asyncio.create_task(self.single_run_and_schedule())
        await self.task

    def callback_handle(self, future: asyncio.Future):
        exception = future.exception()
        if exception:
            if isinstance(exception, asyncio.CancelledError):
                logger.info(f"Scheduled task {self.task_name} explicitly cancelled and stopped.")
            else:
                logger.info(f"Scheduled task {self.task_name} failed with unhandled exception: {exception}")
        else:
            logger.info(f"Scheduled task {self.task_name} finished (unexpected stop).")

    def start(self):
        if self.task is not None and not self.task.done():
            logger.info(f"{self.task_name} is scheduled.")
            return

        logger.info(f"Start Scheduling {self.task_name}")
        self.task = asyncio.create_task(self.start_scheduling())
        self.task.add_done_callback(self.callback_handle)        
        logger.info(f"Scheduling {self.task_name} started.")
        return self.task
    
    async def start_scheduling(self):
        await self.init_work()
        if self.pre_wait:
            logger.info(f"{self.task_name} will start after {self.sleep_interval} seconds")
            await asyncio.sleep(self.sleep_interval)
        self.task = asyncio.create_task(self.single_run_and_schedule())
        self.task.add_done_callback(self.callback_handle)
        await self.task