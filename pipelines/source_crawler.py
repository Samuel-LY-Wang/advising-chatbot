import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from Errors import HTMLFetchError, InvalidURLError
from urllib.parse import urljoin, urlparse

ignored_status_codes = set([404, 401, 403, 406])
ignore_domains = set(["mailto:", "tel:", "youtube.com", "youtu.be", "twitter.com", "facebook.com", "linkedin.com", "arxiv.org"])

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
    if (url[-4:].lower() == ".pdf"):
        # print(url)
        loader = PyPDFLoader(url)
        documents = loader.load()
        full_text = "\n".join([doc.page_content for doc in documents])
        return full_text, {}
    resp = requests.get(url, headers=headers, timeout=timeout)
    if (resp.status_code in ignored_status_codes):
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
    url = "https://content.cs.umass.edu/content/fall-2025-course-description"
    # tweak strip_lines_from_edges if header/footer are not removed by selectors
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    cleaned, links = fetch_and_strip(url, headers=headers, strip_from_top=5, strip_from_bottom=9)


    with open("test/test_output.txt", "w") as f:
        f.write(cleaned)