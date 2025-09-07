import asyncio

class Listener:
    def __init__(self):
        pass

    def get_query_time(self):
        pass

    async def start(self):
        await self.init_work()
        self.task = asyncio.create_task(self.runner())
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


