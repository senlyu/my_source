
from daily_jobs.daily_job import DailyJob
import pytz
from datetime import datetime, timedelta
import os
from util.logging_to_file import Logging

class ReportJob(DailyJob):
    def __init__(self, job_name, target_time, exporter, analyzer, storage_path):
        super().__init__(job_name, target_time)
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

        all_path = [path for path in [today_path, yesterday_path] if os.path.exists(path)]

        (result, req) = self.analyzer.get_result_from_models(all_path)
        Logging.log(req)
        Logging.log(result)

        self.exporter.export(f"{req["model"]}")
        msg = result["txt"]
        res = self.exporter.export_by_model(f"{msg}", self.analyzer) # process model results only
        for r in res: 
            Logging.log(r)
            
        self.exporter.export(f"{result["usage_metadata"]}")
        self.exporter.export(f"{now} my source daily job end")