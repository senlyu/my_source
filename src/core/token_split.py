import math

from ..util.logging_to_file import Logging

SPLIT_TOKEN_SIZE = 100000

class TokenSplit:
    @staticmethod
    def get_split_msgs(all_msgs, data_configs):
        all_msg_str = "".join(all_msgs)
        total_size = len(all_msg_str)
        batch_count = math.ceil(total_size / SPLIT_TOKEN_SIZE)

        if batch_count > 10:
            Logging.log(f"too mang information, only can handle less than 10 batchs.... but we have {batch_count}")
            batch_count = 10

        req_set = []
        current_set = []
        current_count = 0
        for msg in all_msgs:
            current_count += len(msg)
            current_set.append(msg)
            if current_count > SPLIT_TOKEN_SIZE:
                batch_config = data_configs.copy()
                batch_config['batch'] = len(req_set)
                req_set.append(([current_set.copy()], batch_config))

                current_set = []
                current_count = 0

                if len(req_set) == 9:
                    break

        if len(req_set) != 9:
            batch_config = data_configs.copy()
            batch_config['batch'] = len(req_set)
            req_set.append(([current_set.copy()], batch_config))

        return req_set