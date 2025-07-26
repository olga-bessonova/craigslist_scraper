import undetected_chromedriver as uc
import random
import time
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_craigslist_tutors():
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

        # Определяем общее количество объявлений
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.visible-counts span"))
        )
        counts = driver.find_elements(By.CSS_SELECTOR, "div.visible-counts span")
        for i, c in enumerate(counts):
            print(f"{i}: '{c.text}'")

        total = None
        for c in counts:
            if "of" in c.text:
                try:
                    total = int(c.text.split("of")[-1].strip())
                    break
                except ValueError:
                    continue

        if total is None:
            print("❌ Не удалось найти общее количество объявлений.")
            for i, c in enumerate(counts):
                print(f"{i}: '{c.text}'")
            return

        print("💡 Total expected listings:", total)

        last_count = 0
        scroll_pause = 2.5

        # Скроллим страницу до конца
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)

            listings = driver.find_elements(By.CSS_SELECTOR, "div[data-pid]")
            print(f"📦 Currently loaded: {len(listings)}")

            if len(listings) == last_count:
                print("⚠️ No new listings loaded, stopping...")
                break

            if len(listings) >= total:
                print("✅ Loaded all listings")
                break

            last_count = len(listings)

        # Удаляем дубликаты по title и сохраняем
        listings = driver.find_elements(By.CSS_SELECTOR, "div[data-pid]")
        print(f"{len(listings)} listings found")

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
            except:
                continue

        # Сохраняем результат в CSV
        with open("craigslist_tutors.csv", "w", newline="", encoding="utf-8") as f:
            fieldnames = ["title", "link"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(tutors)

        print(f"✅ Saved {len(tutors)} unique listings to craigslist_tutors.csv")

if __name__ == "__main__":
    scrape_craigslist_tutors()
