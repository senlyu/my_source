import asyncio
from datetime import datetime, timedelta
import pytz

class DailyJob:

    def get_job_name(self):
        return self.job_name or ""

    def get_target_time(self):
        return self.target_time or "13:00:00"

    async def job(self):
        pass

    async def run_task_daily(self, target_time):
        pst = pytz.timezone('US/Pacific')
        while True:
            now = datetime.now(pst)
            target_hour, target_minute, target_second = map(int, target_time.split(":"))
            
            # Compute the target time for today
            target_datetime = now.replace(hour=target_hour, minute=target_minute, second=target_second, microsecond=0)
            
            # If the target time has already passed today, schedule for tomorrow
            if target_datetime <= now:
                target_datetime += timedelta(days=1)

            delay = (target_datetime - now).total_seconds()
            print(f"{self.get_job_name()} Task scheduled for: {target_datetime}. Delay: {delay} seconds.")
            
            await asyncio.sleep(delay)  # Wait until the target time
            await self.job()             # Run the task

    def start(self):
        self.task = asyncio.create_task(self.run_task_daily(self.get_target_time()))
        return self.task