

import pathlib
from datetime import datetime, timedelta
import pytz
from telethon import TelegramClient
from src.ai_utils.key_manager import KeyManager
from src.ai_utils.token_split_gemini import TokenSplitGemini
from ..data_io.telegram import TelegramListener
from ..ai_utils.gemini import GeminiConnect
from ..core.report_job import ReportJob
from ..data_io.discord import DiscordExporter
from ..data_io.hexo import HexoExporter
from ..util.sys_env import get_is_dev_mode

class ComponentsFactory:
    def __init__(self, config):
        self.config = config
    
    def init_telegram_listener_from_config(self):
        config = self.config
        (telegram_app_id, telegram_app_hash, telegram_client_name, telegram_channels) = config.get_telegram_config()
        storage_path = config.get_storage_path_telegram()

        pathlib.Path(storage_path).mkdir(parents=True, exist_ok=True) 
        common_telegram_client = TelegramClient(telegram_client_name, telegram_app_id, telegram_app_hash)

        return [TelegramListener(common_telegram_client, storage_path, channel, 5*60 if not get_is_dev_mode() else 10) for channel in telegram_channels]

    def init_discord_exporter_from_config(self):
        config = self.config
        discord_channel_url = config.get_discord_config()
        return DiscordExporter(discord_channel_url)

    def init_hexo_exporter_from_config(self, report_title=None, tag=None):
        config = self.config
        (path, post_path, url_domain, upload_command, command_path) = config.get_hexo_config()
        return HexoExporter(path, post_path, url_domain, upload_command, command_path, report_title, tag)

    def init_gemini_connect_key_manager_from_config(self, key_manager):
        config = self.config
        (_, gemini_history) = config.get_gemini_config()
        return TokenSplitGemini(key_manager, gemini_history)

    def init_gemini_key_manager_from_config(self):
        config = self.config
        gemini_keys = config.get_gemini_key_manager()
        return KeyManager(gemini_keys, 1) # use one because token size limit

    def init_report_job_to_hexo(self, key_manager, report_title=None, report_time="18:00:00", start_ts=None, end_ts=None, tag=None):
        config = self.config
        storage_path = config.get_storage_path_telegram()
        trigger_time = (datetime.now()+timedelta(seconds=10)).strftime("%H:%M:%S") if get_is_dev_mode() else report_time

        pst = pytz.timezone('US/Pacific')
        today_day = datetime.now(pst).date()
        target_time_hms = datetime.strptime(report_time, "%H:%M:%S").time()
        target_time_ts = pst.localize(datetime.combine(today_day, target_time_hms)).timestamp()
        end_ts = target_time_ts if end_ts is None else end_ts
        return ReportJob(
            "hexo report: " + report_title if report_title is not None else "", 
            trigger_time, 
            self.init_hexo_exporter_from_config(report_title, tag), 
            self.init_gemini_connect_key_manager_from_config(key_manager), 
            storage_path, 
            self.init_discord_exporter_from_config(),
            start_ts,
            end_ts,
        )