import asyncio
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class KeyManager:
    def __init__(self, api_keys: List[Dict[str, Any]], rpm: int):
        self.rpm = rpm
        self.request_interval = 60.0 / rpm

        self.key_status: Dict[str, Dict[str, Any]] = {
            key["name"]: {
                'value': key["value"],
                'last_request_time': 0.0,
                'lock': asyncio.Lock() # one lock per key
            }
            for key in api_keys
        }

        self.manager_lock = asyncio.Lock() # lock for action to get a key
        self.keys_list = api_keys
        self.current_key_index = 0

    async def get_key_and_wait(self) -> str:
        while True:
            async with self.manager_lock:
                for _ in range(len(self.keys_list)):
                    key_name = self.keys_list[self.current_key_index]["name"]
                    status = self.key_status[key_name]

                    if status['lock'].locked():
                        self.current_key_index = (self.current_key_index + 1) % len(self.keys_list)
                        continue

                    logger.debug(f"Trying to get key: {key_name}")
                    await status['lock'].acquire()
                    try:
                        next_allowed_time = status['last_request_time'] + self.request_interval
                        current_time = time.time()
                        
                        wait_time = next_allowed_time - current_time

                        if wait_time <= 0:
                            logger.info(f"Key {key_name} available now.")
                            status['last_request_time'] = current_time
                            self.current_key_index = (self.current_key_index + 1) % len(self.keys_list)
                            return status['value']
                        else:
                            logger.debug(f"Key {key_name} needs to wait {wait_time:.2f}s.")
                            status['lock'].release()
                            self.current_key_index = (self.current_key_index + 1) % len(self.keys_list)
                            continue

                    except Exception:
                        if status['lock'].locked():
                            status['lock'].release()
                        raise
                
                # If no key is immediately available, calculate shortest wait time
                earliest_reset_time = float('inf')
                for _, status in self.key_status.items():
                    if not status['lock'].locked():
                        earliest_reset_time = min(
                            earliest_reset_time, 
                            status['last_request_time'] + self.request_interval
                        )

                current_time = time.time()
                wait_duration = min(earliest_reset_time - current_time, 60)
                
            if wait_duration > 0:
                logger.info(f"All keys busy, waiting {wait_duration:.2f}s...")
                await asyncio.sleep(wait_duration)
            else:
                await asyncio.sleep(1)

    def release_key(self, key_value: str):
        for name, status in self.key_status.items():
            if status['value'] == key_value:
                if status['lock'].locked():
                    status['lock'].release()
                    logger.info(f"Released key: {name}")
                return
        logger.warning("Attempted to release unknown key.")
