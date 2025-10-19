
import asyncio
from ..scheduler.target_time_job import TargetTimeJob
import pytz
from datetime import datetime, timedelta
import os
from ..util.logging_to_file import Logging
from ..ai_utils.prompts.gemini_prompt import FinancePromptFirstPart, FinancePromptSecondPart, FinancePromptThirdPart, FinancePromptFourthPart, FinancePromptFifthPart

async def get_standard_result_from_model(analyzer, prompt, data_paths):
    (result, req) = await analyzer.get_result_from_models(prompt, data_paths)
    Logging.log(req)
    Logging.log(result)
    Logging.log(f"{req["model"]}")
    Logging.log(f"{result["usage_metadata"]}")

    return prompt.header() + prompt.get_formated_result(result["txt"])

def find_direct_folders_os(root_dir):
    full_paths_for_sub_folders = []

    for name in os.listdir(root_dir):
        full_path = os.path.join(root_dir, name)
        if os.path.isdir(full_path):
            full_paths_for_sub_folders.append(full_path)
            
    return full_paths_for_sub_folders

def get_all_paths(storage_path):
    full_paths_for_sub_folders = [os.path.join(storage_path, '@fnnew')] # token too large if contains all channels
    res = []
    for p in full_paths_for_sub_folders:
        today = datetime.now().strftime('%Y-%m-%d')
        today_path = os.path.join(p, today+".txt")
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_path = os.path.join(p, yesterday+".txt")
        res.extend([path for path in [today_path, yesterday_path] if os.path.exists(path)])
    return res

class ReportJob(TargetTimeJob):
    def __init__(self, job_name, target_time, main_exporter, analyzer, storage_path, link_share_exporter):
        super().__init__(job_name, target_time)
        self.exporter = main_exporter
        self.analyzer = analyzer
        self.storage_path = storage_path
        self.link_share_exporter = link_share_exporter

    async def init_work(self):
        pass

    async def main(self):
        pst = pytz.timezone('US/Pacific')
        now = datetime.now(pst).strftime("%m-%d-%H:%M:%S")
        Logging.log(f"{now} my source daily job start")

        all_path = get_all_paths(self.storage_path)
        Logging.log(f"all path found: {all_path}")
        model_requests = []
        model_requests.append(get_standard_result_from_model(self.analyzer, FinancePromptFirstPart(), all_path))
        model_requests.append(get_standard_result_from_model(self.analyzer, FinancePromptSecondPart(), all_path))
        model_requests.append(get_standard_result_from_model(self.analyzer, FinancePromptThirdPart(), all_path))
        model_requests.append(get_standard_result_from_model(self.analyzer, FinancePromptFourthPart(), all_path))
        model_requests.append(get_standard_result_from_model(self.analyzer, FinancePromptFifthPart(), all_path))

        prompts_results = await asyncio.gather(*model_requests)

        self.exporter.export("\n\n\n".join(prompts_results)) # process model results only
        self.link_share_exporter.export("daily updated doc here: " + self.exporter.get_new_post_link())
            
        now = datetime.now(pst).strftime("%m-%d-%H:%M:%S")
        Logging.log(f"{now} my source daily job end")