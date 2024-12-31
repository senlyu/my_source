import json
import os
import datetime
from telethon import TelegramClient
from storage.save_to_file import SaveToFile
from connections.listener import Listener

class TelegramListener(Listener):
    def __init__(self, app_id, app_hash, client_name, storage_path, channel_name, query_time=60*5):
        self.query_time = query_time
        self.client = TelegramClient(client_name, app_id, app_hash)
        self.storage_path = storage_path
        self.channel_name = channel_name

    def get_query_time(self):
        return self.query_time

    async def init_work(self):
        pass

    async def main(self):
        while not self.client.is_connected():
            try:
                await self.client.connect()
                print('connected')
            except Exception as e:
                print(e)
                await asyncio.sleep(60)

        all, previous_messages = await self.query()
        filtered = self.filter(all, previous_messages)
        for message in filtered:
            self.save(message[0], message[1])
        print("finished one job")

    async def query_by_date(self, date):
        yesterday = date - datetime.timedelta(days=1)
        message = await self.client.get_messages(entity = self.channel_name, offset_date=yesterday)
        min_id = message.id
        return await self.query_min_id(min_id)

    async def query_min_id(self, min_id):
        all = []
        async for message in self.client.iter_messages(entity = self.channel_name, min_id=int(min_id), limit=1000):
            all.append((message.id, message.text))
        return all

    async def query_some(self):
        all = []
        async for message in self.client.iter_messages(entity = self.channel_name, limit=1000):
            all.append((message.id, message.text))
        return all

    async def query(self):
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(self.storage_path, date+".txt")
        if not os.path.exists(path):
            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday_path = os.path.join(self.storage_path, yesterday+".txt")
            if os.path.exists(yesterday_path):
                path = yesterday_path

        file_storage = SaveToFile(path)
        previous_messages = file_storage.load()

        all = []
        if len(previous_messages) > 0:
            sorted_messages = sorted(previous_messages, key=lambda x: x[0], reverse=True)
            max_id = sorted_messages[0][0]
            print('query by max_id')
            all = await self.query_min_id(max_id)
        else:
            print('query some')
            all = await self.query_some()

        print("finished one query")
        return all, previous_messages

    def filter(self, all, previous_messages):
        filtered_all_by_channel = self.filter_by_channel_type(self.channel_name, all)

        all_set = set()
        all_self_dedup = []
        for message in filtered_all_by_channel:
            msg = message[1]
            hash_str = str(hash(msg))
            if hash_str not in all_set:
                all_set.add(hash_str)
                all_self_dedup.append(message)

        previous_messages_id = [x[0] for x in previous_messages]
        all_filtered_from_previous = list(filter(lambda x: x[0] not in previous_messages_id, all_self_dedup))
        return sorted(all_filtered_from_previous, key=lambda x: x[0])

    def save(self, id, data):
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(self.storage_path, date+".txt")
        save_to_file = SaveToFile(path)
        save_to_file.save(id, data)

    def filter_by_channel_type(self, channel, messages):
        if channel == '@fnnew':
            filtered = []
            # start with date or #重要
            for message in messages:
                text_content = message[1].lstrip()

                if text_content.startswith('#重要'):
                    text_content = text_content[3:].lstrip()

                try:
                    date = datetime.datetime.strptime(text_content[:5], '%m-%d')
                    date = date.replace(year=datetime.datetime.now().year)
                    date = date.date()
                    today = datetime.datetime.today().date()
                    if date >= today:
                        filtered.append(message)

                except Exception as e:
                    print(e)
                    filtered.append(message)

            return filtered
        else:
            raise Exception('not implemented')

                
