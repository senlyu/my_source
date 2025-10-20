import json
import os
import hashlib
from ..util.logging_to_file import session_logger
Logging = session_logger

class SaveToFile:
    def __init__(self, file_name):
        self.file_name = file_name

    def save(self, data):
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w+', encoding="utf-8") as f:
                f.write(f'{data}')
                f.close()
        else:
            with open(self.file_name, 'a', encoding="utf-8") as f:
                f.write(f'{data}')
                f.close()

    def load(self):
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w+', encoding="utf-8") as f:
                f.write('')
                f.close()
        try:
            with open(self.file_name, 'r', encoding="utf-8") as f:
                data = f.read()
                f.close()
        except Exception as e:
            Logging.log(e)
            data = ""
        return data

    def load_by_line(self):
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w+', encoding="utf-8") as f:
                f.write('')
                f.close()
        try:
            with open(self.file_name, 'r', encoding="utf-8") as f:
                lines = f.readlines()
                f.close()
        except Exception as e:
            Logging.log(e)
            lines = []
        return lines

class SaveToFileWithID(SaveToFile):
    def save_with_id(self, id, data):
        self.save(f'{id}|{json.dumps(data, ensure_ascii=False)} \n')

    def load_with_id(self):
        return [(id, json.loads(data)) for id, data in [line.split('|') for line in self.load_by_line()]]

def hash_data_40_chars(data):
    canonical_bytes = json.dumps(
        data,
        sort_keys=True,
        separators=(',', ':')
    ).encode('utf-8')
    return hashlib.sha1(canonical_bytes).hexdigest() # 40 chars