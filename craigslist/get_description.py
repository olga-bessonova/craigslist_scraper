import csv
from bs4 import BeautifulSoup
from craigslist.http_session import create_session, fetch_with_retry
from craigslist.logger import get_logger

logger = get_logger()

def get_body(html: str, url: str) -> str:
    try:
        soup = BeautifulSoup(html, "html.parser")
        body_elem = soup.find("section", id="postingbody")

        if not body_elem:
            logger.warning(f"No postingbody found in {url}")
            return "NOT FOUND"

        # Delete div with QR code if it exists
        qr_div = body_elem.find("div", class_="print-information")
        if qr_div:
            qr_div.decompose()

        text = body_elem.get_text(separator="\n", strip=True)
        return ' '.join(text.split()) 

    except Exception as e:
        logger.error(f"Error parsing HTML for {url}: {e}")
        return "NOT FOUND"



def get_date_and_time(html: str, url: str) -> str:
    try:
        soup = BeautifulSoup(html, "html.parser")
        time_elem = soup.select_one("#display-date time[datetime]")
        if time_elem and time_elem.has_attr("datetime"):
            return time_elem["datetime"]
        else:
            logger.warning(f"No posting date found in {url}")
            return "NOT FOUND"
    except Exception as e:
        logger.error(f"Error extracting date from {url}: {e}")
        return "NOT FOUND"


def get_description():
    input_file  = "database/craigslist_title_link.csv"
    output_file = "database/craigslist_title_link_date_description.csv"

    session = create_session()

    with open(input_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        listings = list(reader)

    for i, row in enumerate(listings):
        url = row.get("link")
        logger.info(f"[{i+1}/{len(listings)}] Fetching: {url}")

        try:
            html = fetch_with_retry(session, url)
            description = get_body(html, url)
            date_and_time = get_date_and_time(html, url)
        except Exception as e:
            logger.error(f"Failed to fetch or parse from {url}: {e}")
            description = "NOT FOUND"
            date_and_time   = "NOT FOUND"

        row['description'] = description
        row['date_and_time'] = date_and_time
        row['date'] = date_and_time.split("T")[0]
        logger.info(f"Description length: {len(description)} chars | Date: {date_and_time}")

    with open(output_file, "w", newline='', encoding="utf-8") as f:
        fieldnames = ["city", "title", "link","date_and_time", "date", "description"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(listings)

    logger.info(f"Done: descriptions and dates saved to {output_file}")


if __name__ == "__main__":
    get_description()
