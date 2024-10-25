from datetime import datetime
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerService:
    scheduler = AsyncIOScheduler()
    
    @classmethod
    def add_date_job(cls, task: Callable, run_date: datetime, **kwargs):
        cls.scheduler.add_job(
            task,
            'date',
            run_date=run_date,
            kwargs=kwargs
        )
