

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

    storage_path = config.get('storage').get('path').get('telegram')
    pathlib.Path(storage_path).mkdir(parents=True, exist_ok=True) 

    return TelegramListener(telegram_app_id, telegram_app_hash, telegram_client_name, storage_path, 10)

async def main():
    telegram_listener = init_telegram_listener_from_config()
    telegram_task = telegram_listener.start()

    await asyncio.gather(telegram_task)

if __name__ == "__main__":
    asyncio.run(main())