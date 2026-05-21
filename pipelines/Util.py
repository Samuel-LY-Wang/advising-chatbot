import time
import json
import logging

logging.basicConfig(level=logging.INFO, filename="logs/timing.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def time_execution(func, out="Execution time: "):
    start_time = time.time()
    result = func()
    end_time = time.time()
    logger.info(f"{out}{end_time - start_time} seconds")
    return result

def clean_url(url):
    # converts URL to safe filename (by removing the header and replacing problematic characters)
    return url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "-")

def save_json(path, data):
    logger.info(f"Saving JSON to {path}")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info("Finished saving JSON.")