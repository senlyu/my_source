from datetime import datetime, timedelta
import pytz
from .recursive_scheduler import RecursiveScheduler

class TargetTimeJob(RecursiveScheduler):
    def __init__(self, job_name, target_time):
        self.job_name = job_name
        self.target_time = target_time
        super().__init__(job_name, self.update_sleep_interval(), True)
        
    async def init_work(self):
        raise NotImplementedError()
        
    async def main(self):
        raise NotImplementedError()
    
    def update_sleep_interval(self):
        return self.get_seconds_after_to_trigger_next_job()

    def get_job_name(self):
        return self.job_name or ""

    def get_target_time(self):
        return self.target_time or "13:00:00"

    def get_seconds_after_to_trigger_next_job(self):
        pst = pytz.timezone('US/Pacific')
        now = datetime.now(pst)
        target_hour, target_minute, target_second = map(int, self.target_time.split(":"))
        
        # Compute the target time for today
        target_datetime = now.replace(hour=target_hour, minute=target_minute, second=target_second, microsecond=0)
        
        # If the target time has already passed today, schedule for tomorrow
        if target_datetime <= now:
            target_datetime += timedelta(days=1)

        return (target_datetime - now).total_seconds()