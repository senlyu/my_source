import json

class SaveToFile:
    def __init__(self, file_name):
        self.file_name = file_name

    def save(self, id, data):
        with open(self.file_name, 'a', encoding="utf-8") as f:
            f.write(f'{id}|{json.dumps(data, ensure_ascii=False)} \n')
            f.close()

    def load(self):
        with open(self.file_name, 'r', encoding="utf-8") as f:
            lines = [(id, json.loads(data)) for id, data in [line.split('|') for line in f.readlines()]]
            f.close()
        return lines