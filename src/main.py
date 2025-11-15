import asyncio
from .util.tasks import run_tasks, gen_listeners, gen_reporters
from .util.logging_standard import DefaultLogger as Logging
from .util.sys_env import get_mode, get_is_dev_mode

CONFIG_FILE = 'config.json'

async def main():
    await run_tasks(CONFIG_FILE, [gen_listeners, gen_reporters])

async def dev_on_listener():
    await run_tasks(CONFIG_FILE, [gen_listeners])

async def dev_on_reporter():
    await run_tasks(CONFIG_FILE, [gen_reporters])

if __name__ == "__main__":
    Logging.clean()
    mode = get_mode()
    
    logger = Logging.getLogger("main")
    logger.info("-"*100)
    logger.info("my source start with mode: " + mode)
    logger.info("-"*100)
    modes_mapping = {
        "dev_listener": dev_on_listener,
        "dev_reporter": dev_on_reporter,
        "dev_model": dev_on_reporter,
        "dev": main,
        "prod": main,
    }
    
    run_func = modes_mapping.get(mode, main)
    asyncio.run(run_func())