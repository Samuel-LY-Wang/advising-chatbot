import time
import json

def time_execution(func):
    start_time = time.time()
    out = func()
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")
    return out

def clean_url(url):
    # converts URL to safe filename (by removing the header and replacing problematic characters)
    return url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "-")

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)