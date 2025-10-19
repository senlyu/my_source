import asyncio
from .util.logging_to_file import Logging
from .util.sys_env import get_mode
from .util.config import Config
from .util.components_factory import ComponentsFactory

async def gen_listeners(config):
    factory = ComponentsFactory(config)
    telegram_listeners = factory.init_telegram_listener_from_config()
    return [
        await telegram_listener.start() for telegram_listener in telegram_listeners
    ]

async def gen_reporters(config):
    factory = ComponentsFactory(config)
    # upload task
    # discord_job = factory.init_report_job_to_discord()
    hexo_job = factory.init_report_job_to_hexo()
    return [
        # await discord_job.start(), 
        await hexo_job.start(),
    ]

async def main():
    config = Config('config.json')
    all_tasks = []
    all_tasks.extend(await gen_listeners(config))
    all_tasks.extend(await gen_reporters(config))
    await asyncio.gather(*all_tasks)

async def dev_on_listener():
    config = Config('config.json')
    await asyncio.gather(*(await gen_listeners(config)))

async def dev_on_reporter():
    config = Config('config.json')
    await asyncio.gather(*(await gen_reporters(config)))

if __name__ == "__main__":
    Logging.clean()
    Logging.log("-"*100)
    mode = get_mode()
    Logging.log("my source start with mode: " + mode)
    Logging.log("-"*100)

    if mode == "dev_listener":
        asyncio.run(dev_on_listener())
    elif mode == "dev_reporter":
        asyncio.run(dev_on_reporter())
    elif mode == "dev":
        asyncio.run(main())
    else:
        asyncio.run(main())