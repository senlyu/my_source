import asyncio
from util.logging_to_file import Logging
from util.sys_env import get_mode
from util.config import Config
from util.factory import ServiceFactory

async def main():
    config = Config('config.json')
    factory = ServiceFactory(config)

    exporter = factory.create_hexo_exporter()
    gemini_connect = factory.create_gemini_connect_no_format()
    
    exporter.export_by_model('test', gemini_connect)


if __name__ == "__main__":
    Logging.clean()
    Logging.log(get_mode())
    asyncio.run(main())