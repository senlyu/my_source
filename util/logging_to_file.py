"""
Import secondly, be aware adding any dependency
"""

import os
from datetime import datetime, timedelta
from util.sys_env import get_is_dev_mode

class Logging:

    @staticmethod
    def clean():
        is_dev_mode = get_is_dev_mode()
        if is_dev_mode:
            file_name = os.path.join("./log.txt")
            if os.path.isfile(file_name):
                os.remove(file_name)
            return

        storage_path = os.path.join("./log")
        date = datetime.now().strftime('%Y-%m-%d')
        all_file_names = []
        for root, dirs, files in os.walk(storage_path):
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
                date_obj_file = datetime.strptime(date_in_file, '%Y-%m-%d')
            except Exception as e:
                Logging.log(e)
                continue
            
            if date_obj_file + timedelta(days=30) < datetime.now():
                delete_targets.append(item[1])
        for full_path in delete_targets:
            os.remove(full_path)
            Logging.log(f"remove file: {full_path}")

    @staticmethod
    def log(*args, **kwargs):
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_dev_mode = get_is_dev_mode()

        file_name = os.path.join("./log", date + ".txt") if not is_dev_mode else os.path.join("./log.txt")
        if not os.path.exists(file_name):
            with open(file_name, 'w+', encoding="utf-8") as f:
                s = time + ": " + (" ").join(str(arg) for arg in args)
                s = s + (" ").join(str(f"{k}: {v}") for k, v in kwargs.items())
                f.write(s)
                f.write("\n")
                f.close()
        else:
            with open(file_name, 'a', encoding="utf-8") as f:
                s = time + ": " + (" ").join(str(arg) for arg in args)
                s = s + (" ").join(str(f"{k}: {v}") for k, v in kwargs.items())
                f.write(s)
                f.write("\n")
                f.close()
