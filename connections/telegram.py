import json
import os
import datetime
from telethon import TelegramClient
from storage.save_to_file import SaveToFile
from connections.listener import Listener

class TelegramListener(Listener):
    def __init__(self, app_id, app_hash, client_name, storage_path, query_time=60*5):
        self.query_time = query_time
        self.client = TelegramClient(client_name, app_id, app_hash)
        self.storage_path = storage_path

    def get_query_time(self):
        return self.query_time

    async def init_work(self):
        #check history
        #if history is empty, read by date
        #else read by max id
        pass

    def check_should_keep(self, message):
        # check if id exist
        # check if message is dup
        return True

    async def main(self):
        while not self.client.is_connected():
            try:
                await self.client.connect()
                print('connected')
            except Exception as e:
                print(e)

        await self.query()

    async def query(self):
        async for message in self.client.iter_messages('@fnnew', limit=5):
            should_keep = self.check_should_keep(message)
            if should_keep:
                self.save(message.id, message.text)

    def save(self, id, data):
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(self.storage_path, date+".txt")
        save_to_file = SaveToFile(path)
        save_to_file.save(id, data)



