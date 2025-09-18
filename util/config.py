import json
from util.sys_env import get_is_dev_mode

# pylint: disable=W0105
"""
config file example
{
    "telegram": {
        "app_id": "",
        "app_hash": "",
        "client_name": "",
        "channels": [""]
    },
    "storage": {
        "path": {
            "telegram": ""
        }
    },
    "discord": {
        "url_dev": "",
        "url_prod": ""
    },
    "gemini": {
        "api_key": ""
    }
}
"""

class Config:
    def __init__(self, file):
        self.file = file
        with open('config.json', 'r') as f:
            self.config = json.load(f)

    def get_storage_path_telegram(self):
        return self.config.get('storage').get('path').get('telegram')

    def get_telegram_config(self):
        telegram_config = self.config.get('telegram')
        telegram_app_id = telegram_config.get('app_id')
        telegram_app_hash = telegram_config.get('app_hash')
        telegram_client_name = telegram_config.get('client_name')
        telegram_channels = telegram_config.get('channels')
        return (telegram_app_id, telegram_app_hash, telegram_client_name, telegram_channels)

    def get_discord_config(self):
        discord_config = self.config.get('discord')
        return discord_config.get('url_dev') if get_is_dev_mode() else discord_config.get('url_prod')

    def get_gemini_config(self):
        gemini_config = self.config.get('gemini')
        return gemini_config.get('api_key')

