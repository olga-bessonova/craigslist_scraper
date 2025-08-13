from typing import Dict, Tuple, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .clean_text import clean_text

def absolute_url(base_url: str, href: str) -> Optional[str]:
    if not href:
        return None
    href = href.strip()
    if href.startswith("/"):
        return f"{base_url}{href}"
    if href.startswith("http://") or href.startswith("https://"):
        return href
    print("address: ", f"{base_url}/{href.lstrip('/')}")
    return f"{base_url}/{href.lstrip('/')}"


def get_listings(html: str, base_url: str) -> List[Tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    listings: List[Tuple[str, str]] = []

    # Extract domain, e.g., "akroncanton.craigslist.org"
    base_domain = urlparse(base_url).netloc

    for a in soup.select('a[href*="/lss/"]'):
        # Prefer visible text; fallback to title attr
        title = (a.get_text(strip=True) or a.get("title") or "").strip()
        title = clean_text(title)
        href = a.get("href")
        # if href has base_url part in it proceed with code otherwise contine
        abs_link = absolute_url(base_url, href)

        # Check that there is a title, abs_link and the listing is in the right city
        if title and abs_link and base_domain in abs_link:
            listings.append((title, abs_link))

    # De-duplicate by normalized title (like original)
    seen = set()
    unique_listings: List[Tuple[str, str]] = []
    for title, link in listings:
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_listings.append((title, link))

    return unique_listings

if __name__ == "__main__":
    main()


