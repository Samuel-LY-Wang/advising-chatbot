import time
import json
import logging

def time_execution(func, logger=logging.getLogger(__name__), out="Execution time: "):
    start_time = time.time()
    result = func()
    end_time = time.time()
    logger.info(f"{out}{end_time - start_time} seconds")
    return result

def clean_url(url):
    # converts URL to safe filename (by removing the header and replacing problematic characters)
    return url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "-")

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)