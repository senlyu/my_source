import asyncio
import time
from typing import Dict, Any, List

from src.util.logging_standard import DefaultLogger as Logging
logger = Logging.getLogger(__name__)

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
            # only one call could run the search
            async with self.manager_lock:
                for _ in range(len(self.keys_list)):
                    key_name = self.keys_list[self.current_key_index]["name"]
                    status = self.key_status[key_name]

                    # if locked try next
                    if status['lock'].locked():
                        self.current_key_index = (self.current_key_index + 1) % len(self.keys_list)
                        continue

                    logger.debug("try to get a key")
                    # try get the key, if concurrent case happened will hold
                    # but should not happen since "async with self.manager_lock" above
                    await status['lock'].acquire()
                    try:
                        # get the wait time for this key
                        next_allowed_time = status['last_request_time'] + self.request_interval
                        current_time = time.time()
                        
                        wait_time = next_allowed_time - current_time

                        if wait_time <= 0:
                            # if key could be use right now
                            logger.debug(f"{key_name} could be use right now, {wait_time} seconds")
                            status['last_request_time'] = current_time
                            self.current_key_index = (self.current_key_index + 1) % len(self.keys_list)
                            return status['value']
                        else:
                            # if key could not be use right now
                            logger.debug(f"{key_name} could not be use right now, {wait_time} seconds")
                            status['lock'].release()
                            self.current_key_index = (self.current_key_index + 1) % len(self.keys_list)
                            continue

                    except Exception:
                        if status['lock'].locked():
                            status['lock'].release()
                        raise
                
                earliest_reset_time = float('inf')
                for _, status in self.key_status.items():
                    if not status['lock'].locked():
                        earliest_reset_time = min(
                            earliest_reset_time, 
                            status['last_request_time'] + self.request_interval
                        )

                current_time = time.time()
                wait_duration = min(earliest_reset_time - current_time, 60) # no need to wait more than 60s if all keys are using
                
            if wait_duration > 0:
                logger.debug(f"all keys are not available waiting {wait_duration:.2f} second for next key")
                await asyncio.sleep(wait_duration)
            else:
                # if somehow key is available, start again
                await asyncio.sleep(1)

    def release_key(self, key: str):
        lock = None
        for name, status in self.key_status.items():
            if status['value'] == key:
                lock = status['lock']
                logger.debug(f"work done key released {name}")
                break
        if lock and lock.locked():
            lock.release()