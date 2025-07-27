from craigslist.scraper import scrape_listings
from craigslist.descriptions import get_posting_bodies
from craigslist.extract_phones import extract_phone_number
from craigslist.extract_emails import extract_emails

def main():
    scrape_listings()

if __name__ == "__main__":
    main()
