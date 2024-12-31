import json
import os
from logging_to_file import Logging

class SaveToFile:
    def __init__(self, file_name):
        self.file_name = file_name

    def save(self, id, data):
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w+', encoding="utf-8") as f:
                f.write(f'{id}|{json.dumps(data, ensure_ascii=False)} \n')
                f.close()
        else:
            with open(self.file_name, 'a', encoding="utf-8") as f:
                f.write(f'{id}|{json.dumps(data, ensure_ascii=False)} \n')
                f.close()

    def load(self):
        try:
            with open(self.file_name, 'r', encoding="utf-8") as f:
                lines = [(id, json.loads(data)) for id, data in [line.split('|') for line in f.readlines()]]
                f.close()
        except Exception as e:
            Logging.log(e)
            lines = []
        return lines