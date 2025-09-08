
from daily_jobs.daily_job import DailyJob
import pytz
from datetime import datetime, timedelta
import os
from logging_to_file import Logging

class ReportJob(DailyJob):
    def __init__(self, job_name, target_time, exporter, analyzer, storage_path):
        self.job_name = job_name
        self.target_time = target_time
        self.exporter = exporter
        self.analyzer = analyzer
        self.storage_path = storage_path


    async def job(self):
        pst = pytz.timezone('US/Pacific')
        now = datetime.now(pst).strftime("%m-%d-%H:%M:%S")
        self.exporter.export(f"{now} my source daily job start")

        today = datetime.now().strftime('%Y-%m-%d')
        today_path = os.path.join(self.storage_path, today+".txt")
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_path = os.path.join(self.storage_path, yesterday+".txt")

        all_path = list(filter(lambda path: os.path.exists(path), [today_path, yesterday_path]))

        response = self.analyzer.get_result_from_models(all_path)
        Logging.log(response)

        msg = response.text
        res = self.exporter.export(f"{msg}")
        self.exporter.export(f"{response.usage_metadata}")
        self.exporter.export(f"{now} my source daily job end")