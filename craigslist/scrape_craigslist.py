import undetected_chromedriver as uc
import random
import time
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from craigslist.logger import get_logger

def scrape_craigslist():
    logger = get_logger()

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    ]

    options = uc.ChromeOptions()
    options.headless = False
    options.add_argument(f'user-agent={random.choice(user_agents)}')

    with uc.Chrome(options=options) as driver:
        url = "https://newyork.craigslist.org/search/lss#search=2~thumb~0"
        driver.get(url)
        time.sleep(5)

        # Find total number of listings in this category
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.visible-counts span"))
        )
        counts = driver.find_elements(By.CSS_SELECTOR, "div.visible-counts span")
        logger.info(f"Total counts in span element {counts}")

        total = None
        for c in counts:
            if "of" in c.text:
                try:
                    total = int(c.text.split("of")[-1].strip())
                    break
                except ValueError:
                    continue

        if total is None:
            logger.error("Couldn't find total number of listings")

        logger.info(f"Total number of listings: {total}")
        
        listings = driver.find_elements(By.CSS_SELECTOR, "div[data-pid]")
        logger.info(f"{len(listings)} listings found")

        # Remove duplicates
        seen_titles = set()
        tutors = []

        for listing in listings:
            try:
                a_elem = listing.find_element(By.CSS_SELECTOR, "a[href].cl-search-anchor")
                title = a_elem.text.strip()
                link = a_elem.get_attribute("href")

                if title in seen_titles:
                    continue

                seen_titles.add(title)
                tutors.append({
                    "title": title,
                    "link": link
                })
            except Exception as e:
                logger.warning(f"Skipping a listing due to an error: {e}")
                continue

        logger.info(f"{len(seen_titles)} unique listings found")
        
        # Save titles and link to craigslist_t_l.csv
        with open("database/craigslist_t_l.csv", "w", newline="", encoding="utf-8") as f:
            fieldnames = ["title", "link"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tutors)

        logger.info(f"Saved {len(tutors)} unique listings to craigslist_t_l.csv")

if __name__ == "__main__":
    scrape_craigslist()
