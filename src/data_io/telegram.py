import os
import datetime
import re
from .save_to_file import SaveToFileWithID
from ..scheduler.recursive_scheduler import RecursiveScheduler
from ..util.logging_to_file import session_logger

Logging = session_logger

class TelegramListener(RecursiveScheduler):
    def __init__(self, client, storage_path, channel_name, query_time=60*5):
        super().__init__('telegram_listener'+channel_name, query_time)
        self.client = client
        self.storage_path = os.path.join(storage_path, channel_name)
        self.channel_name = channel_name

    async def init_work(self):
        self.clean()
        await self.connect()

    async def main(self):
        await self.connect()
        all_msg, previous_messages = await self.query()
        filtered = self.filter(all_msg, previous_messages)
        for message in filtered:
            self.save(message[0], message[1])
        Logging.log(f"finished one job, saved {len(filtered)} messages")
        
    async def connect(self):
        if not self.client.is_connected():
            await self.client.start()
            Logging.log('connected')

    async def query_by_date(self, date):
        yesterday = date - datetime.timedelta(days=1)
        message = await self.client.get_messages(entity = self.channel_name, offset_date=yesterday)
        min_id = message.id
        return await self.query_min_id(min_id)

    async def query_min_id(self, min_id):
        all_msgs = []
        async for message in self.client.iter_messages(entity = self.channel_name, min_id=int(min_id), limit=1000):
            all_msgs.append((message.id, message.text))
        return all_msgs

    async def query_some(self):
        all_msgs = []
        async for message in self.client.iter_messages(entity = self.channel_name, limit=1000):
            all_msgs.append((message.id, message.text))
        return all_msgs

    async def query(self):
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(self.storage_path, date+".txt")
        if not os.path.exists(path):
            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday_path = os.path.join(self.storage_path, yesterday+".txt")
            if os.path.exists(yesterday_path):
                path = yesterday_path

        file_storage = SaveToFileWithID(path)
        previous_messages = file_storage.load_with_id()

        all_msgs = []
        if len(previous_messages) > 0:
            sorted_messages = sorted(previous_messages, key=lambda x: x[0], reverse=True)
            max_id = sorted_messages[0][0]
            Logging.log('query by max_id')
            all_msgs = await self.query_min_id(max_id)
        else:
            Logging.log('query some')
            all_msgs = await self.query_some()

        Logging.log("finished one query")
        return all_msgs, previous_messages

    def filter(self, all_msgs, previous_messages):
        filtered_all_by_channel = self.filter_by_channel_type(self.channel_name, all_msgs)

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

    def save(self, msg_id, data):
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        path = os.path.join(self.storage_path, now_date+".txt")
        save_to_file = SaveToFileWithID(path)
        save_to_file.save_with_id(msg_id, data)

    def clean(self):
        all_file_names = []
        for root, _, files in os.walk(self.storage_path):
            for file in files:
                if file.lower().endswith('.txt'):  # Case-insensitive check
                    full_path = os.path.join(root, file)
                    if os.path.isfile(full_path):
                        all_file_names.append([file, full_path])
        delete_targets = []
        for item in all_file_names:
            file_name = item[0]
            date_in_file = file_name.split('.')[0]
            try:
                date_obj_file = datetime.datetime.strptime(date_in_file, '%Y-%m-%d')
            except Exception as e:
                Logging.log(e)
                continue
            
            if date_obj_file + datetime.timedelta(days=30) < datetime.datetime.now():
                delete_targets.append(item[1])
        for full_path in delete_targets:
            os.remove(full_path)
            Logging.log(f"remove file: {full_path}")

    def filter_by_channel_type(self, channel, messages):
        if channel == "@fnnew":
            return self.fnnew_channel_handle(messages)
        elif channel == "@Financial_Express":
            return self.Financial_Express_channel_handle(messages)
        elif channel == "@wublock":
            return self.wublock_channel_handle(messages)
        else:
            raise NotImplementedError()

    def fnnew_channel_handle(self, messages):
        filtered = []
        # start with date or #重要
        for message in messages:
            text_content = message[1].lstrip()

            if text_content.startswith('#重要'):
                text_content = text_content[3:].lstrip()
            message_list = list(message)
            message_list[1] = text_content
            message = tuple(message_list)

            try:
                msg_date = datetime.datetime.strptime(text_content[:5], '%m-%d')
                msg_date = msg_date.replace(year=datetime.datetime.now().year)
                msg_date = msg_date.date()
                today = datetime.datetime.today().date()
                if msg_date >= today:
                    filtered.append(message)

            except Exception as e:
                Logging.log(e)
                filtered.append(message)

        return filtered
    
    def Financial_Express_channel_handle(self, messages):
        filtered = []
        
        for message in messages:
            text_content = message[1].lstrip()
            text_content = re.sub(r"\n", "", text_content) # remove \n
            text_content = re.sub(r"\*\*", "", text_content) # remove **
            text_content = re.sub(r"\|", "", text_content) # remove |
            text_content = re.sub(r"https?\:\/\/[^\s]+", "", text_content) # remove link

            message_list = list(message)
            message_list[1] = text_content
            message = tuple(message_list)

            filtered.append(message)

        return filtered
                
    def wublock_channel_handle(self, messages):
        filtered = []
        
        for message in messages:
            text_content = message[1].lstrip()

            text_content = re.sub(r"吴说", "", text_content) # remove 吴说
            text_content = re.sub(r"\n", "", text_content) # remove \n
            text_content = re.sub(r"\|", "", text_content) # remove |
            text_content = re.sub(r"\[\s*[—一]*\s*(link)*\]\(([^)]+)\)", "", text_content) # remove link
            message_list = list(message)
            message_list[1] = text_content
            message = tuple(message_list)

            filtered.append(message)

        return filtered
