import re

def to_html_link(url: str, text: str) -> str:
    return f'<a href="{url}">{text}</a>'

def get_citations(answer: str) -> list[int]:
    # extract all numbers in square brackets from the answer and return as a list of ints
    citations = re.findall(r'\[(\d+)\]', answer)
    return [int(citation) for citation in citations]