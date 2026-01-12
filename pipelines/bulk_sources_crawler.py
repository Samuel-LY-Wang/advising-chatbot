import os, time, requests
from bs4 import BeautifulSoup
from pathlib import Path
from source_crawler import fetch_and_strip
from langchain_community.document_loaders import PyPDFLoader

OUT_DIR = Path("data/raw/bulk")
OUT_DIR.mkdir(parents=True, exist_ok=True)
strip=[5,9]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

SOURCES = {
    "Spring_2026_Course_Descriptions": "https://content.cs.umass.edu/content/spring-2026-course-descriptions",
    "Fall_2025_Course_Descriptions": "https://content.cs.umass.edu/content/fall-2025-course-description",
    "Spring_2025_Course_Descriptions": "https://content.cs.umass.edu/content/spring-2025-course-descriptions",
    "Fall_2024_Course_Descriptions": "https://content.cs.umass.edu/content/fall-2024-course-descriptions",
    "CICS_Prereq_Changes": "https://www.cics.umass.edu/academics/courses/prerequisite-catalog-and-credit-changes"
}

def recursive_fetch(base_url, max_depth=1):
    text, links = fetch_and_strip(base_url, strip_from_top=strip[0], strip_from_bottom=strip[1])
    cur_urls = set(links.values())
    all_text = text + "\n"
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
                txt, lnks = fetch_and_strip(url, strip_from_top=strip[0], strip_from_bottom=strip[1])
                all_text += txt + "\n"
                new_urls.update(lnks.values())
            except Exception as e:
                # print(f"Error fetching {url}: {e}")
                pass
    return all_text

def main():
    for name, url in SOURCES.items():
        print(name)
        try:
            text = recursive_fetch(url)
            with open(OUT_DIR / f"{name}.txt", "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            print(f"Error occured when trying to save {name}: {e}")

if __name__ == "__main__":
    main()
