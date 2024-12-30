
from daily_jobs.daily_job import DailyJob
import pytz
from datetime import datetime

class ReportJob(DailyJob):
    def __init__(self, job_name, target_time, exporter):
        self.job_name = job_name
        self.target_time = target_time
        self.exporter = exporter

    async def job(self):
        pst = pytz.timezone('US/Pacific')
        now = datetime.now(pst).strftime("%m-%d-%H:%M:%S")
        self.exporter.export(f"{now} my source daily job start")