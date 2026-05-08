import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from open_config import load_config

try:
    from pipelines.source_crawler import fetch_and_strip
    from pipelines.Errors import HTMLFetchError, InvalidURLError
    from pipelines import Util
except ModuleNotFoundError:
    from source_crawler import fetch_and_strip
    from Errors import HTMLFetchError, InvalidURLError
    import Util

config = load_config()

OUT_DIR = os.path.join(config["cwd"], config["raw_data_path"])
if (not os.path.exists(OUT_DIR)):
    os.makedirs(OUT_DIR)
MAPPING_PATH = os.path.join(config["cwd"], config["mappings_path"])
if (not os.path.exists(MAPPING_PATH)):
    os.makedirs(MAPPING_PATH)
MAPPING_FILE = os.path.join(MAPPING_PATH, config["doc_mapping_file"])
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
    # saves text to file and returns file path
    out_path = os.path.join(OUT_DIR, Util.clean_url(cur_url) + ".txt")
    if os.path.exists(out_path):
        return out_path
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    return out_path

def recursive_fetch(base_url, mapping = {}, max_depth=2, visited=set()):
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
                path = save_text(url, txt)
                new_urls.update(lnks.values())
                mapping[path] = url # Maps from filename to cleaned URL
                # print(len(visited), " ", len(mapping), " ", url)
            except HTMLFetchError:
                pass
            except InvalidURLError:
                pass
            except Exception as e:
                print(f"Unexpected error fetching {url}: {e}")
    return visited, mapping

def main():
    fetch_all()

def fetch_all(sources=SOURCES):
    mapping = {}
    visited_so_far = set()
    visited_so_far.add("")
    visited_so_far.update(sources)
    for url in sources:
        # print(url)
        visited_so_far, mapping = recursive_fetch(url, mapping=mapping, visited=visited_so_far, max_depth=config["recursive_depth"])
    Util.save_json(MAPPING_FILE, mapping)
    print(f"Visited {len(visited_so_far)} URLs.")

if __name__ == "__main__":
    Util.time_execution(main)