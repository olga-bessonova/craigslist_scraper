from bs4 import BeautifulSoup
import logging
from .clean_text import clean_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

def parse_body(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    body_el = soup.select_one("#postingbody")
    if not body_el:
        body_el = soup.select_one(".userbody") or soup.select_one("section.body")
    if not body_el:
        return ""
    return clean_text(body_el.get_text(" ", strip=True))