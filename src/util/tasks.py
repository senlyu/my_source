import asyncio
from datetime import datetime, timedelta

import pytz
from .config import Config
from .components_factory import ComponentsFactory

def find_time_helper():
    pst = pytz.timezone('US/Pacific')
    today_day = datetime.now(pst).date()
    yst_day = today_day - timedelta(days=1)
    yst_3pm_ts = pst.localize(datetime.combine(yst_day, datetime.strptime("15:00:00", "%H:%M:%S").time())).timestamp()
    t_8am_ts = pst.localize(datetime.combine(today_day, datetime.strptime("08:00:00", "%H:%M:%S").time())).timestamp()
    return yst_3pm_ts, t_8am_ts

async def gen_listeners(config):
    factory = ComponentsFactory(config)
    telegram_listeners = factory.init_telegram_listener_from_config()
    return [
        telegram_listener.start() for telegram_listener in telegram_listeners
    ]

async def gen_reporters(config):
    factory = ComponentsFactory(config)
    # upload task
    # discord_job = factory.init_report_job_to_discord()
    yst_3pm_ts, t_8am_ts = find_time_helper()
    # from 3pm - 9am
    hexo_market_open_report = factory.init_report_job_to_hexo("Daily_Financial_Market_Open_Report", "09:00:00", yst_3pm_ts, None, "MarketOpen")
    # from 8am - 4PM
    hexo_market_close_report = factory.init_report_job_to_hexo("Daily_Financial_Market_Close_Report", "16:00:00", t_8am_ts, None, "MarketClose")
    return [
        # await discord_job.start(), 
        hexo_market_open_report.start(),
        hexo_market_close_report.start(),
    ]

async def run_tasks(config_file, tasks_generators):
    config = Config(config_file)
    all_tasks = []
    for generator in tasks_generators:
        all_tasks.extend(await generator(config))
    await asyncio.gather(*all_tasks)