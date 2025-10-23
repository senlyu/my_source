import asyncio
import math

from src.ai_utils.gemini import GeminiConnect
from src.ai_utils.prompts.combine_prompt import CombinePrompt
from ..util.logging_to_file import create_session_id, reset_session_id, session_logger

Logging = session_logger


class TokenSplitGemini(GeminiConnect):
    SPLIT_TOKEN_SIZE = 100000
    COMBINE_PROMOT = CombinePrompt()

    def get_split_msgs(self, all_msgs, data_configs):
        all_msg_str = "".join(all_msgs)
        total_size = len(all_msg_str)
        batch_count = math.ceil(total_size / self.SPLIT_TOKEN_SIZE)

        if batch_count > 10:
            Logging.log(f"too mang information, only can handle less than 10 batchs.... but we have {batch_count}")
            batch_count = 10

        req_set = []
        current_set = []
        current_count = 0
        for msg in all_msgs:
            current_count += len(msg)
            current_set.append(msg)
            if current_count > self.SPLIT_TOKEN_SIZE:
                batch_config = data_configs.copy()
                batch_config['batch'] = len(req_set)
                req_set.append(([current_set.copy()], batch_config))

                current_set = []
                current_count = 0

                if len(req_set) == 9:
                    break

        return req_set

    async def get_standard_result_from_model(self, prompt, all_msgs, data_configs):
        token = create_session_id()
        try:
            req_sets = self.get_split_msgs(all_msgs, data_configs)

            requests = [ super().get_standard_result_from_model(prompt, one_set[0], one_set[1]) for one_set in req_sets ]
            all_results = await asyncio.gather(*requests)
            all_results_txt_list = [ result["txt"] for result in all_results ]

            final_result = await super().get_standard_result_from_model(self.COMBINE_PROMOT, all_results_txt_list, data_configs)
            result = self.COMBINE_PROMOT.get_formated_result(final_result["txt"])
        finally:
            reset_session_id(token)
        return result
