

import json
import pathlib
import asyncio
from connections.telegram import TelegramListener


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

    return [TelegramListener(telegram_app_id, telegram_app_hash, telegram_client_name, storage_path, channel, 10) for channel in telegram_channels]

async def main():
    telegram_listeners = init_telegram_listener_from_config()
    telegram_tasks = [telegram_listener.start() for telegram_listener in telegram_listeners]

    # upload task

    all_tasks = telegram_tasks

    await asyncio.gather(*all_tasks)

if __name__ == "__main__":
    asyncio.run(main())