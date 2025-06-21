
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from .services import fetch_vehicle_data #fetch_car_vin_data
import threading
import os
import time  


LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "livelogfile.log")

def log_message(msg):
    # Ensure the directory exists
    log_dir = os.path.dirname(LOG_FILE_PATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    print(msg)  # still shows in terminal
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")

scheduler = BackgroundScheduler(timezone="CET")
job_state = {"enabled": True}
job_timestamps = {
    "start": None,
    "end": None
}

last_job_filters = {}


def is_scheduler_enabled():
    return job_state["enabled"]

def set_scheduler_state(state: bool):
    job_state["enabled"] = state

def get_job_timestamps():
    return job_timestamps.copy()


def run_daily_fetch():
    if not job_state["enabled"]:
        print("[!] Scheduler is disabled. Skipping fetch job.")
        log_message("[!] Scheduler is disabled. Skipping fetch job.")
        return

    job_timestamps["start"] = datetime.now().date()  # Track job start
    job_timestamps["end"] = None

    print("[🚀] Starting daily vehicle fetch job...")    
    log_message("[🚀] Starting daily vehicle fetch job...")

    yesterday = (datetime.now() - timedelta(days=1)).date()
    filters = {
        "auction_date_from": str(yesterday),
        "auction_date_to": str(yesterday),
        "per_page": 50,
        "page": 1,
        "api_token": os.getenv("API_TOKEN") or "6394dc91ece3542af402645dc9f2aa1b2c2dec923b24cf3d249373228a019684"
    }
    global last_job_filters
    last_job_filters = filters.copy()

    while True:
        if not job_state["enabled"]:
            print("[!] Scheduler DISABLED DURING FETCH. Aborting job immediately.")
            break

        print(f"[🔄] Fetching page {filters['page']}...")
        log_message(f"[🔄] Fetching page {filters['page']}...")

        response_data, result_summary = fetch_vehicle_data(filters)

        if response_data.get("error"):
            error_line = f"[API ERROR] {response_data['error']}"
            print(error_line)
            return

        count = response_data.get("pagination", {}).get("count", 0)
        stat_line = f"[✓] Page {filters['page']} — Saved: {result_summary['saved']}, Skipped: {result_summary['duplicates']}"
        print(stat_line)
        log_message(stat_line)

        last_job_filters['page'] = filters['page']

        if count < 50:
            info_line = f"[INFO] Page {filters['page']} had only {count} results. Stopping fetch."
            print(info_line)
            break

        # Move to next page
        filters["page"] += 1

        # Optional delay
        print("[⏳] Waiting 1 seconds before next page...")
        time.sleep(1)

    job_timestamps["end"] = datetime.now().date()  # Track job end

    # print("[⚙️] Starting VIN enrichment (get-car-vin)...")
    # log_message("[⚙️] Starting VIN enrichment (get-car-vin)...")
    # # fetch_car_vin_data()

    

def get_last_job_filters():
    global last_job_filters
    return last_job_filters.copy()


def start_scheduler():
    if not scheduler.get_jobs():
        scheduler.add_job(run_daily_fetch, 'cron', hour=0, minute=0)
        threading.Thread(target=scheduler.start, daemon=True).start()
        log_message("[✅] APScheduler started: daily vehicle job running ")
        print("[✅] APScheduler started: daily vehicle job running ")
