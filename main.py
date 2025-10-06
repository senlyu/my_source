import asyncio
import pathlib
from datetime import datetime, timedelta
from connections.telegram import TelegramListener
from connections.gemini import GeminiConnect
from daily_jobs.report_job import ReportJob
from export.discord import DiscordExporter
from util.logging_to_file import Logging
from util.sys_env import get_mode, get_is_dev_mode
from util.config import Config


def init_telegram_listener_from_config(config):
    (telegram_app_id, telegram_app_hash, telegram_client_name, telegram_channels) = config.get_telegram_config()
    storage_path = config.get_storage_path_telegram()

    pathlib.Path(storage_path).mkdir(parents=True, exist_ok=True) 

    return [TelegramListener(telegram_app_id, telegram_app_hash, telegram_client_name, storage_path, channel, 60) for channel in telegram_channels]

def init_discord_exporter_from_config(config):
    discord_channel_url = config.get_discord_config()
    return DiscordExporter(discord_channel_url)

def init_gemini_connect_from_config(config):
    gemini_api_key = config.get_gemini_config()
    return GeminiConnect(gemini_api_key, 'sp')

def init_main_job_from_config(config):
    storage_path = config.get_storage_path_telegram()
    report_time = (datetime.now()+timedelta(seconds=10)).strftime("%H:%M:%S") if get_is_dev_mode() else "18:00:00"
    return ReportJob("main report", report_time, init_discord_exporter_from_config(config), init_gemini_connect_from_config(config), storage_path)

async def main():
    config = Config('config.json')
    telegram_listeners = init_telegram_listener_from_config(config)
    telegram_tasks = [telegram_listener.start() for telegram_listener in telegram_listeners]

    # upload task
    main_job = init_main_job_from_config(config)

    # all_tasks = telegram_tasks
    all_tasks = telegram_tasks + [main_job.start()]

    await asyncio.gather(*all_tasks)

if __name__ == "__main__":
    Logging.clean()
    Logging.log(get_mode())
    asyncio.run(main())