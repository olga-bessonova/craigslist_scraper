from typing import Dict, Tuple, List, Optional
from bs4 import BeautifulSoup
from .legacy_v1.clean_text import clean_text

def absolute_url(base_url: str, href: str) -> Optional[str]:
    if not href:
        return None
    href = href.strip()
    if href.startswith("/"):
        return f"{base_url}{href}"
    if href.startswith("http://") or href.startswith("https://"):
        return href
    # relative path like 'lss/...' -> ensure single slash join
    return f"{base_url}/{href.lstrip('/')}"


def parse_listings(html: str, base_url: str) -> List[Tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    items: List[Tuple[str, str]] = []

    for a in soup.select('a[href*="/lss/"]'):
        # Prefer visible text; fallback to title attr
        title = (a.get_text(strip=True) or a.get("title") or "").strip()
        title = clean_text(title)
        href = a.get("href")
        abs_link = absolute_url(base_url, href)
        if title and abs_link:
            items.append((title, abs_link))

    # De-duplicate by normalized title (like original)
    seen = set()
    unique_items: List[Tuple[str, str]] = []
    for title, link in items:
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_items.append((title, link))

    return unique_items

if __name__ == "__main__":
    main()


