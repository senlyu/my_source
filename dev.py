import asyncio

from export.hexo import HexoExporter
from util.logging_to_file import Logging
from util.sys_env import get_mode
from util.config import Config

async def main():
    config = Config('config.json')
    (path, post_path) = config.get_hexo_config()
    exporter = HexoExporter(path, post_path)
    exporter.export('test')


if __name__ == "__main__":
    Logging.clean()
    Logging.log(get_mode())
    asyncio.run(main())