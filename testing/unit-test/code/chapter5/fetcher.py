import requests


def fetch_title(url: str) -> str:
    """Fetch a URL and return the HTML title or raise RuntimeError on bad status."""
    resp = requests.get(url, timeout=5)
    if resp.status_code != 200:
        raise RuntimeError(f"Bad status: {resp.status_code}")
    text = resp.text
    # naive title extraction
    start = text.find("<title>")
    end = text.find("</title>")
    if start != -1 and end != -1:
        return text[start + 7:end].strip()
    return ""
