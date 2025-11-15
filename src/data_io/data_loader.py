import os
from datetime import datetime, timedelta
from src.data_io.save_to_file import SaveToFileWithIDInDefaultTS
from ..util.logging_standard import DefaultLogger as Logging

logger = Logging.getLogger(__name__)

class DataLoader:

    @staticmethod
    def get_msg_and_config_from_multiple_path_filtering_by_ts_range(storage_path, start_ts, end_ts):
        all_msgs = DataLoader.get_msgs_from_multiple_path_filtering_by_ts_range(storage_path, start_ts, end_ts)
        data_configs = {
            "total_size": len(all_msgs),
            "start_ts": start_ts,
            "end_ts": end_ts,
        }
        return all_msgs, data_configs

    @staticmethod
    def get_msgs_from_multiple_path_filtering_by_ts_range(storage_path, start_ts, end_ts):
        all_path = DataLoader.get_all_paths(storage_path, start_ts, end_ts)
        logger.info(f"all path found: {all_path}")

        all_msgs = []
        for data_path in all_path:
            file_storage = SaveToFileWithIDInDefaultTS(data_path)
            messages_for_one_data_path = file_storage.load_by_ts_in_range_only_row_data(start_ts, end_ts)
            all_msgs.extend(messages_for_one_data_path)
        return all_msgs

    @staticmethod
    def find_direct_folders_os(root_dir):
        full_paths_for_sub_folders = []

        for name in os.listdir(root_dir):
            full_path = os.path.join(root_dir, name)
            if os.path.isdir(full_path):
                full_paths_for_sub_folders.append(full_path)
                
        return full_paths_for_sub_folders

    @staticmethod
    def get_all_dates(start_ts, end_ts):
        start_date_obj = datetime.fromtimestamp(start_ts).date()
        end_date_obj = datetime.fromtimestamp(end_ts).date()
        date_diff = (end_date_obj - start_date_obj).days
        # Add + 1 to the range length
        all_dates = [
            start_date_obj + timedelta(days=i) 
            for i in range(date_diff + 1)
        ]
        return [ date_obj.strftime('%Y-%m-%d')+".txt" for date_obj in all_dates ]
    
    @staticmethod
    def get_all_paths(storage_path, start_ts, end_ts):
        # full_paths_for_sub_folders = [os.path.join(storage_path, '@fnnew')] # token too large if contains all channels
        full_paths_for_sub_folders = DataLoader.find_direct_folders_os(storage_path)
        all_record_file_names = DataLoader.get_all_dates(start_ts, end_ts)

        res = []
        for p in full_paths_for_sub_folders:
            for date_file_name in all_record_file_names:
                date_file_path = os.path.join(p, date_file_name)
                if os.path.exists(date_file_path):
                    res.append(date_file_path)
        return res