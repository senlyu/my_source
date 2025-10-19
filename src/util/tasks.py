import asyncio
from .config import Config
from .components_factory import ComponentsFactory

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

async def run_tasks(config_file, tasks_generators):
    config = Config(config_file)
    all_tasks = []
    for generator in tasks_generators:
        all_tasks.extend(await generator(config))
    await asyncio.gather(*all_tasks)