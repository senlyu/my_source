import asyncio
import pathlib
from datetime import datetime, timedelta
from connections.telegram import TelegramListener
from connections.gemini import GeminiConnect
from daily_jobs.report_job import ReportJob
from export.discord import DiscordExporter
from export.hexo import HexoExporter
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

def init_hexo_exporter_from_config(config):
    (path, post_path, url_domain, upload_command, command_path) = config.get_hexo_config()
    return HexoExporter(path, post_path, url_domain, upload_command, command_path)

def init_gemini_connect_from_config_format(config):
    (gemini_api_key, gemini_history) = config.get_gemini_config()
    return GeminiConnect(gemini_api_key, gemini_history)

def init_gemini_connect_from_config_no_format(config):
    (gemini_api_key, gemini_history) = config.get_gemini_config()
    return GeminiConnect(gemini_api_key, gemini_history)

# def init_report_job_to_discord(config):
#     storage_path = config.get_storage_path_telegram()
#     report_time = (datetime.now()+timedelta(seconds=10)).strftime("%H:%M:%S") if get_is_dev_mode() else "18:00:00"
#     return ReportJob("discord report", report_time, init_discord_exporter_from_config(config), init_gemini_connect_from_config_format(config), storage_path)

def init_report_job_to_hexo(config):
    storage_path = config.get_storage_path_telegram()
    report_time = (datetime.now()+timedelta(seconds=10)).strftime("%H:%M:%S") if get_is_dev_mode() else "18:00:00"
    return ReportJob(
        "hexo report", 
        report_time, 
        init_hexo_exporter_from_config(config), 
        init_gemini_connect_from_config_no_format(config), 
        storage_path, 
        init_discord_exporter_from_config(config)
    )

async def main():
    config = Config('config.json')
    telegram_listeners = init_telegram_listener_from_config(config)
    telegram_tasks = [
        await telegram_listener.start() for telegram_listener in telegram_listeners
    ]

    # upload task
    # discord_job = init_report_job_to_discord(config)
    hexo_job = init_report_job_to_hexo(config)

    # all_tasks = telegram_tasks
    all_tasks = telegram_tasks + [
        # discord_job.start(), 
        await hexo_job.start()
    ]

    await asyncio.gather(*all_tasks)

async def dev_on_listener():
    config = Config('config.json')
    telegram_listeners = init_telegram_listener_from_config(config)
    telegram_tasks = [
        await telegram_listener.start() for telegram_listener in telegram_listeners
    ]

    all_tasks = telegram_tasks

    await asyncio.gather(*all_tasks)

async def dev_on_reporter():
    config = Config('config.json')
    hexo_job = init_report_job_to_hexo(config)

    all_tasks = [await hexo_job.start()]

    await asyncio.gather(*all_tasks)

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
    elif mode == "prod":
        asyncio.run(main())