import schedule
import os
import time
import threading
from . import apriori

def job():
    print("Running job...")
    apriori.main()
    print("Job done!")

def RunScheduleExec():
    schedule.every(1).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(5)

runScheduleExecThread = threading.Thread(target=RunScheduleExec, name="Reconstruct rules - executing", daemon=True)
runScheduleExecThread.start()