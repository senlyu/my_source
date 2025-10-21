import json
import os
import hashlib
import time
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
    
class SaveToFileWithIDInDefaultTS(SaveToFileWithID):
    def save_with_id(self, id, data):
        current_ts = time.time()
        self.save(f'{id}|{current_ts}|{json.dumps(data, ensure_ascii=False)} \n')

    def load_with_id(self):
        split_result_array = [line.split('|') for line in self.load_by_line()]
        res = []
        for each_line in split_result_array:
            if len(each_line) == 2:
                id, row_data = each_line[0], json.loads(each_line[1])
                ts = None
            elif len(each_line) == 3:
                id, ts, row_data = each_line[0], float(each_line[1]), json.loads(each_line[2])
            else:
                raise ValueError('row data cannot format back')
            res.append((id, ts, row_data))
        return res
    
    def load_by_ts_in_range(self, start_ts, end_ts):
        if start_ts == None:
            start_ts = 0
        if end_ts == None:
            end_ts = time.time()

        split_result_array = [line.split('|') for line in self.load_by_line()]
        res = []
        for each_line in split_result_array:
            if len(each_line) == 2:
                id, row_data = each_line[0], json.loads(each_line[1])
                ts = None
            elif len(each_line) == 3:
                id, ts, row_data = each_line[0], float(each_line[1]), json.loads(each_line[2])
            else:
                raise ValueError('row data cannot format back')
            
            if ts == None or start_ts <= ts <= end_ts:
                res.append((id, ts, row_data))
        return res
    
    def load_by_ts_in_range_only_row_data(self, start_ts, end_ts):
        return [ one_row[2] for one_row in self.load_by_ts_in_range(start_ts, end_ts) ]
        

def hash_data_40_chars(data):
    canonical_bytes = json.dumps(
        data,
        sort_keys=True,
        separators=(',', ':')
    ).encode('utf-8')
    return hashlib.sha1(canonical_bytes).hexdigest() # 40 chars