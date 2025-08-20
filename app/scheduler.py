import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pipeline import run_etl
import pytz
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
TZ = os.getenv("TZ", "Asia/Seoul")
CRON = os.getenv("SCHEDULE_CRON", "0 9 * * *")  # 매일 09:00
ROWS = int(os.getenv("ETL_ROWS", "300"))

def job():
    logging.info(f"Run ETL start rows={ROWS}")
    run_etl(rows=ROWS, use_postgres=True)
    logging.info("Run ETL done")

if __name__ == "__main__":
    tz = pytz.timezone(TZ)
    sched = BlockingScheduler(timezone=tz)
    # 최초 1회 즉시 실행(데이터 초기화 목적)
    job()
    # 이후 cron 스케줄
    minute, hour, dom, month, dow = CRON.split()
    trig = CronTrigger(minute=minute, hour=hour, day=dom, month=month, day_of_week=dow, timezone=tz)
    sched.add_job(job, trig, id="daily_etl", replace_existing=True)
    logging.info(f"Scheduler started with CRON='{CRON}' TZ='{TZ}'")
    sched.start()

