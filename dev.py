import asyncio

from export.hexo import HexoExporter
from export.discord import DiscordExporter
from connections.gemini import GeminiConnect
from promots.gemini_promot import GeminiPromotNoFormat
from util.logging_to_file import Logging
from util.sys_env import get_mode
from util.config import Config

async def main():
    config = Config('config.json')

    discord_channel_url = config.get_discord_config()

    (path, post_path, url_domain, upload_command, command_path) = config.get_hexo_config()
    exporter = HexoExporter(path, post_path, url_domain, DiscordExporter(discord_channel_url), upload_command, command_path)

    gemini_api_key = config.get_gemini_config()
    
    exporter.export_by_model('test', GeminiConnect(gemini_api_key, GeminiPromotNoFormat()))


if __name__ == "__main__":
    Logging.clean()
    Logging.log(get_mode())
    asyncio.run(main())