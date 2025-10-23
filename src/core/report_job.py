
import asyncio
from src.ai_utils.prompts.combine_prompt import CombinePrompt
from src.core.token_split import TokenSplit
from src.data_io.data_loader import DataLoader
from src.util.sys_env import get_mode
from ..scheduler.target_time_job import TargetTimeJob
import pytz
from datetime import datetime, time
from ..util.logging_to_file import create_session_id, reset_session_id, session_logger
from ..ai_utils.prompts.gemini_prompt import FinancePromptFirstPart, FinancePromptSecondPart, FinancePromptThirdPart, FinancePromptFourthPart, FinancePromptFifthPart

Logging = session_logger

class ReportJob(TargetTimeJob):
    COMBINE_PROMOT = CombinePrompt()
    
    def __init__(self, job_name, target_time, main_exporter, analyzer, storage_path, link_share_exporter, start_ts=None, end_ts=None):
        super().__init__(job_name, target_time)
        self.exporter = main_exporter
        self.analyzer = analyzer
        self.storage_path = storage_path
        self.link_share_exporter = link_share_exporter

        today_midnight_ts, target_time_ts = self.get_time_defaults(target_time)
        self.start_ts = start_ts if start_ts is not None else today_midnight_ts
        self.end_ts = end_ts if end_ts is not None else target_time_ts
        
    @staticmethod
    def get_time_defaults(target_time):
        pst = pytz.timezone('US/Pacific')
        today_day = datetime.now(pst).date()
        today_midnight_ts = datetime.combine(datetime.now(pst), time.min).timestamp()

        target_time_hms = datetime.strptime(target_time, "%H:%M:%S").time()
        target_time_ts = pst.localize(datetime.combine(today_day, target_time_hms)).timestamp()
        return today_midnight_ts, target_time_ts

    async def init_work(self):
        pass

    async def main(self):
        pst = pytz.timezone('US/Pacific')
        now = datetime.now(pst).strftime("%m-%d-%H:%M:%S")
        Logging.log(f"{now} my source daily job start")

        all_msgs, data_configs = DataLoader.get_msg_and_config_from_multiple_path_filtering_by_ts_range(self.storage_path, self.start_ts, self.end_ts)
        Logging.log(all_msgs)

        result = await ReportJob.get_token_split_for_model(self.analyzer, all_msgs, data_configs)
        
        if get_mode() != 'dev_model':
            self.exporter.export(result) # process model results only
            self.link_share_exporter.export("daily updated doc here: " + self.exporter.get_new_post_link())
            
        now = datetime.now(pst).strftime("%m-%d-%H:%M:%S")
        Logging.log(f"{now} my source daily job end")

    @staticmethod
    async def standard_msg_process(analyzer, all_msgs, data_configs):
        token = create_session_id()
        try:
            model_requests = []
            for prompt in [FinancePromptFirstPart, FinancePromptSecondPart, FinancePromptThirdPart, FinancePromptFourthPart, FinancePromptFifthPart]:
                model_res = analyzer.get_standard_result_from_model(prompt(), all_msgs, data_configs)
                model_requests.append(model_res)

            prompts_results = await asyncio.gather(*model_requests)
            final_result = "\n\n\n".join(prompts_results)
        finally:
            reset_session_id(token)

        return final_result

    @staticmethod
    async def get_token_split_for_model(analyzer, all_msgs, data_configs):
        req_sets = TokenSplit.get_split_msgs(all_msgs, data_configs)
        Logging.log(f"{len(req_sets)} batches we need to process here")

        requests = [ ReportJob.standard_msg_process(analyzer, one_set[0], one_set[1]) for one_set in req_sets ]
        all_results = await asyncio.gather(*requests)

        all_data = "\n".join(all_results)

        final_result = await analyzer.get_standard_result_from_model(ReportJob.COMBINE_PROMOT, [all_data], data_configs)

        return final_result