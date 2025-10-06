import asyncio
from util.logging_to_file import Logging
from util.sys_env import get_mode
from util.config import Config
from util.factory import ServiceFactory

async def main():
    config = Config('config.json')
    factory = ServiceFactory(config)

    telegram_listeners = factory.create_telegram_listeners()
    telegram_tasks = [listener.start() for listener in telegram_listeners]

    # upload task
    # discord_job = factory.create_report_job_to_discord()
    hexo_job = factory.create_report_job_to_hexo()

    # all_tasks = telegram_tasks
    all_tasks = telegram_tasks + [
        # discord_job.start(),
        hexo_job.start()
    ]

    await asyncio.gather(*all_tasks)

if __name__ == "__main__":
    Logging.clean()
    Logging.log("-"*100)
    Logging.log("my source start with mode: " + "prod" if get_mode() is None else get_mode())
    Logging.log("-"*100)
    asyncio.run(main())