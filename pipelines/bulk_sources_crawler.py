import os, time, requests, sys
from bs4 import BeautifulSoup
from pathlib import Path
try:
    from pipelines.source_crawler import fetch_and_strip
    from pipelines.Errors import HTMLFetchError, InvalidURLError
    from pipelines import Util
except ModuleNotFoundError:
    from source_crawler import fetch_and_strip
    from Errors import HTMLFetchError, InvalidURLError
    import Util
from langchain_community.document_loaders import PyPDFLoader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from open_config import load_config

config = load_config()

cwd = os.getcwd()
OUT_DIR = os.path.join(cwd, config["raw_data_path"])
if (not os.path.exists(OUT_DIR)):
    os.makedirs(OUT_DIR)
strip=[5,9]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

SOURCES = config["sources"]

def get_key_from_val(d, val):
    for k, v in d.items():
        if v == val:
            return k
    return None

def save_text(cur_url, text):
    out_path = os.path.join(OUT_DIR, cur_url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "-") + ".txt")
    if os.path.exists(out_path):
        return
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

def recursive_fetch(base_url, max_depth=2, visited=set()):
    text, links = fetch_and_strip(base_url, strip_from_top=strip[0], strip_from_bottom=strip[1], headers=HEADERS)
    cur_urls = set(links.values())
    save_text(base_url, text)
    new_urls = set()
    for _ in range(max_depth):
        for url in cur_urls:
            if url not in visited:
                new_urls.add(url)
                visited.add(url)
        cur_urls = new_urls
        new_urls = set()
        for url in cur_urls:
            try:
                txt, lnks = fetch_and_strip(url, headers=HEADERS, strip_from_top=strip[0], strip_from_bottom=strip[1])
                save_text(url, txt)
                new_urls.update(lnks.values())
            except HTMLFetchError:
                pass
            except InvalidURLError:
                pass
            except Exception as e:
                print(f"Unexpected error fetching {url}: {e}")
    return visited

def main():
    visited_so_far = set()
    visited_so_far.add("")
    visited_so_far.update(SOURCES)
    for url in SOURCES:
        # print(url)
        visited_so_far = recursive_fetch(url, visited=visited_so_far)

def fetch_all(sources=SOURCES):
    visited_so_far = set()
    visited_so_far.add("")
    visited_so_far.update(sources)
    for url in sources:
        visited_so_far = recursive_fetch(url, visited=visited_so_far, max_depth=config["recursive_depth"])

if __name__ == "__main__":
    Util.time_execution(main)