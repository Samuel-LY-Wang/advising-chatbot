import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
try:
    from pipelines.Errors import HTMLFetchError, InvalidURLError
except ModuleNotFoundError:
    from Errors import HTMLFetchError, InvalidURLError
from urllib.parse import urljoin, urlparse
import logging
logging.getLogger("pypdf").setLevel(logging.ERROR) # silence all warnings about invalid markers or wrong-pointing objects (common but completely irrelevant)

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from open_config import load_config
config = load_config()

ignore_domains = set(config["ignore_domains"])

def is_valid_url(url):
    """Check if URL is valid."""
    for dom in ignore_domains:
        if dom in url:
            return False
    return True

def fetch_and_strip(url, headers, remove_selectors=None, remove_tag_names=None, strip_from_top=0, strip_from_bottom=0, timeout=20):
    """Fetch a web page and remove likely header/footer elements.

    Strategy:
    - Remove common semantic tags by name (header, footer, nav)
    - Remove elements matching common header/footer selectors (ids/classes)
    - Optionally trim N non-empty lines from top/bottom

    Returns the cleaned text.
    """
    if not is_valid_url(url):
        raise InvalidURLError(f"Invalid URL: {url}")
    url_parsed = urlparse(url).path.lower()
    if ("pdf" in url) or url_parsed.endswith(".pdf"):
        # print(url)
        try:
            # first try fetching as PDF
            loader = PyPDFLoader(url)
            documents = loader.load()
            full_text = "\n".join([doc.page_content for doc in documents])
            return full_text, {}
        except Exception as e:
            # if any issues arise just HTML fetch (search for "pdf" results in false positives)
            if url_parsed.endswith(".pdf"):
                raise HTMLFetchError(f"Error fetching PDF from {url}: {e}")
            # print(f"Error loading PDF from {url}: {e}")
            # fallback to HTML fetch
    resp = requests.get(url, headers=headers, timeout=timeout)
    if not resp.ok:
        raise HTMLFetchError(f"Error fetching {url}: Status code {resp.status_code}")
    # resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove by tag names first (semantic tags)
    tag_names = remove_tag_names or ["header", "footer", "nav"]
    for tag in tag_names:
        for el in soup.find_all(tag):
            el.decompose()

    # Remove by common header/footer ids/classes
    selectors = remove_selectors or [
        "#header",
        ".header",
        ".site-header",
        "#masthead",
        "#footer",
        ".footer",
        ".site-footer",
    ]
    for sel in selectors:
        for el in soup.select(sel):
            el.decompose()

    text = soup.get_text("\n", strip=True)
    links = {}
    for a in soup.find_all("a", href=True):
        links[a.get_text(strip=True)] = urljoin(url, a["href"])

    if strip_from_top > 0 or strip_from_bottom > 0:
        lines = [l for l in text.splitlines() if l.strip()]
        if len(lines) > strip_from_top + strip_from_bottom:
            lines = lines[strip_from_top:-strip_from_bottom] if strip_from_bottom > 0 else lines[strip_from_top:]
        text = "\n".join(lines)

    return text, links


if __name__ == "__main__":
    url = "https://openreview.net/pdf?id=4R0pugRyN5"
    # tweak strip_lines_from_edges if header/footer are not removed by selectors
    headers = config["header"]
    cleaned, links = fetch_and_strip(url, headers=headers, strip_from_top=5, strip_from_bottom=9)

    with open("test/test_output.txt", "w") as f:
        f.write(cleaned)