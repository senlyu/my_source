

import json
import pathlib
import asyncio
from connections.telegram import TelegramListener
from daily_jobs.report_job import ReportJob
from export.discord import DiscordExporter
from connections.gemini import GeminiConnect
from logging_to_file import Logging

def init_telegram_listener_from_config():
    with open('config.json', 'r') as f:
        config = json.load(f)

    telegram_config = config.get('telegram')
    telegram_app_id = telegram_config.get('app_id')     
    telegram_app_hash = telegram_config.get('app_hash') 
    telegram_client_name = telegram_config.get('client_name') 
    telegram_channels = telegram_config.get('channels') 

    storage_path = config.get('storage').get('path').get('telegram')
    pathlib.Path(storage_path).mkdir(parents=True, exist_ok=True) 

    return [TelegramListener(telegram_app_id, telegram_app_hash, telegram_client_name, storage_path, channel, 60) for channel in telegram_channels]

def init_discord_exporter_from_config():
    with open('config.json', 'r') as f:
        config = json.load(f)

    discord_config = config.get('discord')
    discord_channel_url = discord_config.get('url_prod')

    return DiscordExporter(discord_channel_url)

def init_gemini_connect_from_config():
    with open('config.json', 'r') as f:
        config = json.load(f)

    gemini_config = config.get('gemini')
    gemini_api_key = gemini_config.get('api_key')

    return GeminiConnect(gemini_api_key)

def init_main_job_from_config():
    with open('config.json', 'r') as f:
        config = json.load(f)

    storage_path = config.get('storage').get('path').get('telegram')

    return ReportJob("main report", "18:00:00", init_discord_exporter_from_config(), init_gemini_connect_from_config(), storage_path)

    
async def main():
    telegram_listeners = init_telegram_listener_from_config()
    telegram_tasks = [telegram_listener.start() for telegram_listener in telegram_listeners]

    # upload task
    main_job = init_main_job_from_config()

    # all_tasks = telegram_tasks
    all_tasks = telegram_tasks + [main_job.start()]

    await asyncio.gather(*all_tasks)

if __name__ == "__main__":
    Logging.clean()
    asyncio.run(main())