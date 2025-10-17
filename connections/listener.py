import asyncio
from util.logging_to_file import Logging

def callback_handle(task):
    Logging.log("callback triggered")
    try:
        task.result()  # Re-raises the exception if one occurred
    except asyncio.CancelledError:
        # Cancellation is not an error
        Logging.log("Task was cancelled.")
    except Exception as e:
        Logging.log("Task finished with exception: %r", e, exc_info=True)

class Listener:
    def __init__(self):
        pass

    def get_query_time(self):
        return 0

    async def start(self):
        await self.init_work()
        self.task = asyncio.create_task(self.runner())
        self.task.add_done_callback(callback_handle)
        return self.task

    async def runner(self):
        while True:
            try:
                await self.main()
                await asyncio.sleep(self.get_query_time())  
            except Exception as e:
                self.error_handle(e)

    async def init_work(self):
        pass

    async def main(self):
        pass

    def error_handle(self, e):
        pass


