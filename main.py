

import json
import pathlib
import asyncio
from connections.telegram import TelegramListener
from daily_jobs.report_job import ReportJob
from export.discord import DiscordExporter


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
    discord_channel_url = discord_config.get('url')

    return DiscordExporter(discord_channel_url)
    
async def main():
    # telegram_listeners = init_telegram_listener_from_config()
    # telegram_tasks = [telegram_listener.start() for telegram_listener in telegram_listeners]

    # upload task
    main_job = ReportJob("main report", "12:34:00", init_discord_exporter_from_config())

    # all_tasks = telegram_tasks
    all_tasks = [main_job.start()]

    await asyncio.gather(*all_tasks)

if __name__ == "__main__":
    asyncio.run(main())