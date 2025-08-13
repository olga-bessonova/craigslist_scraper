from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv, time, os
from craigslist.get_listings import get_listings  
from craigslist.logger import get_logger

logger = get_logger()

OUTFILE = "database/craigslist_title_link.csv"
FIELDS = ["city", "title", "link"]

def scrape_craigslist(city, base_url):
    logger.info(f"Working on city: {city}, base_url: , {base_url}") 
    url = f"{base_url}search/lss"
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(3)  # small pause for JS

    listings_data = get_listings(driver.page_source, base_url)
    driver.quit()

    # Transform to dicts 
    rows = [{"city": city, "title": t, "link": l} for t, l in listings_data]

    # Append new listings
    os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
    file_exists = os.path.exists(OUTFILE)
    is_empty = (not file_exists) or os.path.getsize(OUTFILE) == 0
    if not os.path.exists(OUTFILE):
        os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
        with open(OUTFILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()

    # Remove duplicates
    existing_links = set()
    if file_exists and not is_empty:
        with open(OUTFILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                existing_links.add((r.get("city",""), r.get("link","")))

    # Filter out duplicates (same city+link)
    new_rows = [r for r in rows if (r["city"], r["link"]) not in existing_links]
    if not new_rows:
        
        logger.info(f"No new listings for {city}")
        return

    with open(OUTFILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_empty:
            writer.writeheader()
        writer.writerows(new_rows)

    logger.info(f"Appended {len(new_rows)} listings for {city}")
