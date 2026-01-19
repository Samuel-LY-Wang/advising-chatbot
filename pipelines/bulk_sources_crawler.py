import os, time, requests
from bs4 import BeautifulSoup
from pathlib import Path
from source_crawler import fetch_and_strip
from langchain_community.document_loaders import PyPDFLoader
from Errors import HTMLFetchError, InvalidURLError
import Util

OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)
strip=[5,9]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

SOURCES = [
    "https://content.cs.umass.edu/content/spring-2026-course-descriptions",
    "https://content.cs.umass.edu/content/fall-2025-course-description",
    "https://content.cs.umass.edu/content/spring-2025-course-descriptions",
    "https://content.cs.umass.edu/content/fall-2024-course-descriptions",
    "https://www.cics.umass.edu/academics/courses/prerequisite-catalog-and-credit-changes"
]

def get_key_from_val(d, val):
    for k, v in d.items():
        if v == val:
            return k
    return None

def save_text(cur_url, text):
    out_path = OUT_DIR / (cur_url.replace("https://", "").replace("http://", "").replace("/", "_").replace(".", "-") + ".txt")
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
        visited_so_far = recursive_fetch(url, visited=visited_so_far)

if __name__ == "__main__":
    Util.time_execution(main)