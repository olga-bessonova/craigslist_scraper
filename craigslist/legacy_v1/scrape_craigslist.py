import logging
import sys
import csv
import random
import csv
import os
import datetime as dt
from ..http_session import create_session, fetch_with_retry, delay, random_delay, STOP_REQUESTED
from ..parse_listings import parse_listings
from .parse_body import parse_body
from .extract_contact_info import extract_contact_info


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

def scrape_craigslist(city: str = "charlotte") -> None:
    global STOP_REQUESTED

    base_url = f"https://{city}.craigslist.org"
    search_url = f"{base_url}/search/lss?cc=gb"

    logging.info(f"Navigating to: {search_url}")

    session = create_session()

    try:
        html = fetch_with_retry(session, search_url)
        # Wait for 3s + jitter
        delay(3000 + random.random() * 2000)

        listings = parse_listings(html, base_url)
        logging.info(f"Found {len(listings)} unique listings")

        detailed_rows = []
        total = len(listings)

        for idx, (title, link) in enumerate(listings, start=1):
            if STOP_REQUESTED:
                logging.info("Stop requested. Exiting scrape loop.")
                break

            logging.info(f"Scraping {idx}/{total}: {title}")
            try:
                detail_html = fetch_with_retry(session, link)
                random_delay(1500, 3000)

                body = parse_body(detail_html)
                contact = extract_contact_info(f"{title} {body}")

                detailed_rows.append(
                    {
                        "Title": title,
                        "Link": link,
                        "Body": body if body else "NO BODY",
                        "Email": contact["email"],
                        "Phone": contact["phone"],
                        "Website": contact["website"],
                    }
                )
            except Exception as e:
                logging.error(f"Error scraping {link}: {e}")
                detailed_rows.append(
                    {
                        "Title": title,
                        "Link": link,
                        "Body": "Error retrieving body",
                        "Email": "ERROR",
                        "Phone": "ERROR",
                        "Website": "ERROR",
                    }
                )

            random_delay(2000, 4000)

        # --- Write CSV ---
        today = dt.date.today().isoformat()
        filename = f"craigslist_{city}_full_{today}.csv"
        folder = "database"
        os.makedirs(folder, exist_ok=True) 
        
        filename_path = os.path.join(folder, filename)
        with open(filename_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["Title", "Link", "Body", "Email", "Phone", "Website"]
            )
            writer.writeheader()
            for row in detailed_rows:
                writer.writerow(row)

        logging.info(f"Done. Data saved to {filename_path}")
        logging.info(f"Total listings scraped: {len(detailed_rows)}")

    except KeyboardInterrupt:
        logging.info("Interrupted by user. Shutting down gracefully.")
    except Exception as e:
        logging.error(f"Critical error: {e}")

def main():
    city = sys.argv[1] if len(sys.argv) > 1 else "charlotte"
    scrape_craigslist(city)

if __name__ == "__main__":
    main()
