import csv
import datetime as dt
import logging
from craigslist.http_session import create_session, fetch_with_retry, delay, random_delay
from craigslist.parse_listings import parse_listings
from craigslist.logger import get_logger

logger = get_logger()

def scrape_craigslist(city: str = "newyork"):

    base_url = f"https://{city}.craigslist.org"
    search_url = f"{base_url}/search/lss?cc=gb"

    logger.info(f"Navigating to: {search_url}")

    session = create_session()

    try:
        html = fetch_with_retry(session, search_url)
        delay(3000 + random_delay())  # optional wait after load

        listings = parse_listings(html, base_url)
        logger.info(f"Found {len(listings)} unique listings")

        # Save titles and link to craigslist_t_l.csv
        today = dt.date.today().isoformat()
        filename = f"database/craigslist_t_l.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["title", "link"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for title, link in listings:
                writer.writerow({"title": title, "link": link})

        logger.info(f"Saved {len(listings)} unique listings to {filename}")

    except Exception as e:
        logger.error(f"Error while scraping: {e}")

if __name__ == "__main__":
    scrape_craigslist()
