from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import csv, time, os
from craigslist.get_listings import get_listings  
from craigslist.logger import get_logger

logger = get_logger()

OUTFILE = "database/craigslist_title_link.csv"
FIELDS = ["city", "title", "link"]

def scrape_craigslist(city, base_url):
    logger.info(f"Working on city: {city}, base_url: {base_url}") 
    
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    all_rows = []
    start = 0
    while True:
        url = f"{base_url}search/lss?s={start}"
        logger.info(f"Fetching page: {url}")
        driver.get(url)
        time.sleep(2)  # small pause for JS

        listings_data = get_listings(driver.page_source, base_url)
        if not listings_data:
            break  # No more results

        page_rows = [{"city": city, "title": t, "link": l} for t, l in listings_data]
        all_rows.extend(page_rows)

        # Craigslist usually shows ~120 per page, so jump to next
        if len(listings_data) < 120:
            break
        start += 120

    driver.quit()

    if not all_rows:
        logger.info(f"No listings found for {city}")
        return

    os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
    file_exists = os.path.exists(OUTFILE)
    is_empty = (not file_exists) or os.path.getsize(OUTFILE) == 0

    # Collect existing links to avoid duplicates
    existing_links = set()
    if file_exists and not is_empty:
        with open(OUTFILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                existing_links.add((r.get("city", ""), r.get("link", "")))

    # Filter out duplicates
    new_rows = [r for r in all_rows if (r["city"], r["link"]) not in existing_links]

    if not new_rows:
        logger.info(f"No new listings for {city}")
        return

    # Append to CSV
    with open(OUTFILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_empty:
            writer.writeheader()
        writer.writerows(new_rows)

    logger.info(f"Appended {len(new_rows)} listings for {city}")
