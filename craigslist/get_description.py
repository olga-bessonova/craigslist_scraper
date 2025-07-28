import csv
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from craigslist.logger import get_logger

logger = get_logger()

def get_postingbody(driver, url):
    try:
        driver.get(url)
        time.sleep(random.uniform(2, 4))  # Random delay for human-like behavior

        # Wait for postingbody to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "postingbody"))
        )

        body_element = driver.find_element(By.ID, "postingbody")
        body_text = body_element.text.strip()
        return ' '.join(body_text.split())  # Remove excessive whitespace
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Couldn't get a postingbody from {url}: {e}")
        return "NOT FOUND"


def get_description():
    input_file = "database/craigslist_t_l.csv"
    output_file = "database/craigslist_t_l_d.csv"

    options = uc.ChromeOptions()
    options.headless = False

    with uc.Chrome(options=options) as driver:
        with open(input_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            listings = list(reader)

        for i, row in enumerate(listings):
            logger.info(f"[{i+1}/{len(listings)}] Getting postingbody from: {row['link']}")
            description = get_postingbody(driver, row['link'])
            row['description'] = description
            logger.info(f"Description length: {len(description)} chars")

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["title", "link", "description"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(listings)

    logger.info(f"Done: descriptions saved to {output_file}")


if __name__ == "__main__":
    get_description()
