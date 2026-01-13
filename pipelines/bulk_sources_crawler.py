import os, time, requests
from bs4 import BeautifulSoup
from pathlib import Path
from source_crawler import fetch_and_strip
from langchain_community.document_loaders import PyPDFLoader

OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)
strip=[5,9]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

SOURCES = {
    "Spring_2026_Course_Descriptions": "https://content.cs.umass.edu/content/spring-2026-course-descriptions",
    "Fall_2025_Course_Descriptions": "https://content.cs.umass.edu/content/fall-2025-course-description",
    "Spring_2025_Course_Descriptions": "https://content.cs.umass.edu/content/spring-2025-course-descriptions",
    "Fall_2024_Course_Descriptions": "https://content.cs.umass.edu/content/fall-2024-course-descriptions",
    "CICS_Prereq_Changes": "https://www.cics.umass.edu/academics/courses/prerequisite-catalog-and-credit-changes"
}

def get_key_from_val(d, val):
    for k, v in d.items():
        if v == val:
            return k
    return None

def save_text(base_url, cur_url, text):
    out_folder = get_key_from_val(SOURCES, base_url)
    if out_folder is None:
        raise ValueError(f"Base URL {base_url} not found in SOURCES.")
    out_path = OUT_DIR / out_folder / (cur_url.replace("https://", "").replace("http://", "").replace("/", "_") + ".txt")
    if os.path.exists(out_path):
        return
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

def recursive_fetch(base_url, max_depth=1):
    text, links = fetch_and_strip(base_url, strip_from_top=strip[0], strip_from_bottom=strip[1], headers=HEADERS)
    cur_urls = set(links.values())
    save_text(base_url, base_url, text)
    visited = set()
    visited.add(base_url)
    visited.add('') # to avoid searching empty links
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
                save_text(base_url, url, txt)
                new_urls.update(lnks.values())
            except ValueError:
                # print(f"Error fetching {url}: {e}")
                pass
            except Exception as e:
                print(f"Unexpected error fetching {url}: {e}")

def main():
    for name, url in SOURCES.items():
        if (not os.path.exists(OUT_DIR / name)):
            os.makedirs(OUT_DIR / name)
        print(name)
        recursive_fetch(url)

if __name__ == "__main__":
    main()
