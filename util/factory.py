from connections.telegram import TelegramListener
from connections.gemini import GeminiConnect
from daily_jobs.report_job import ReportJob
from export.discord import DiscordExporter
from export.hexo import HexoExporter
from promots.gemini_promot import GeminiPromotNoFormat, GeminiPromotWithSP
from util.config import Config
import pathlib
from datetime import datetime, timedelta
from util.sys_env import get_is_dev_mode

class ServiceFactory:
    def __init__(self, config: Config):
        self.config = config

    def create_telegram_listeners(self) -> list[TelegramListener]:
        (telegram_app_id, telegram_app_hash, telegram_client_name, telegram_channels) = self.config.get_telegram_config()
        storage_path = self.config.get_storage_path_telegram()

        pathlib.Path(storage_path).mkdir(parents=True, exist_ok=True) 

        return [TelegramListener(telegram_app_id, telegram_app_hash, telegram_client_name, storage_path, channel, 60) for channel in telegram_channels]

    def create_discord_exporter(self) -> DiscordExporter:
        discord_channel_url = self.config.get_discord_config()
        return DiscordExporter(discord_channel_url)

    def create_hexo_exporter(self) -> HexoExporter:
        (path, post_path, url_domain) = self.config.get_hexo_config()
        return HexoExporter(path, post_path, url_domain, self.create_discord_exporter())

    def create_gemini_connect_with_sp(self) -> GeminiConnect:
        gemini_api_key = self.config.get_gemini_config()
        return GeminiConnect(gemini_api_key, GeminiPromotWithSP())

    def create_gemini_connect_no_format(self) -> GeminiConnect:
        gemini_api_key = self.config.get_gemini_config()
        return GeminiConnect(gemini_api_key, GeminiPromotNoFormat())

    def create_report_job_to_discord(self) -> ReportJob:
        storage_path = self.config.get_storage_path_telegram()
        report_time = (datetime.now()+timedelta(seconds=10)).strftime("%H:%M:%S") if get_is_dev_mode() else "18:00:00"
        return ReportJob("discord report", report_time, self.create_discord_exporter(), self.create_gemini_connect_with_sp(), storage_path)

    def create_report_job_to_hexo(self) -> ReportJob:
        storage_path = self.config.get_storage_path_telegram()
        report_time = (datetime.now()+timedelta(seconds=10)).strftime("%H:%M:%S") if get_is_dev_mode() else "18:00:00"
        return ReportJob("hexo report", report_time, self.create_hexo_exporter(), self.create_gemini_connect_no_format(), storage_path)
