
import asyncio
from src.data_io.data_loader import DataLoader
from src.util.sys_env import get_mode
from ..scheduler.target_time_job import TargetTimeJob
import pytz
from datetime import datetime, time
from ..util.logging_to_file import session_logger
from ..ai_utils.prompts.gemini_prompt import FinancePromptFirstPart, FinancePromptSecondPart, FinancePromptThirdPart, FinancePromptFourthPart, FinancePromptFifthPart

Logging = session_logger

class ReportJob(TargetTimeJob):
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

        model_requests = []
        for prompt in [FinancePromptFirstPart, FinancePromptSecondPart, FinancePromptThirdPart, FinancePromptFourthPart, FinancePromptFifthPart]:
            model_res = self.analyzer.get_standard_result_from_model(prompt(), [all_msgs], data_configs)
            model_requests.append(model_res)

        prompts_results = await asyncio.gather(*model_requests)

        if get_mode() != 'dev_model':
            self.exporter.export("\n\n\n".join(prompts_results)) # process model results only
            self.link_share_exporter.export("daily updated doc here: " + self.exporter.get_new_post_link())
            
        now = datetime.now(pst).strftime("%m-%d-%H:%M:%S")
        Logging.log(f"{now} my source daily job end")