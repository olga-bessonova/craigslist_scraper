from craigslist.scrape_craigslist import scrape_craigslist
from craigslist.get_description import get_description
from craigslist.get_contact_info import get_contact_info
import sys

if __name__ == "__main__":
    city = sys.argv[1] if len(sys.argv) > 1 else "charlotte"
    scrape_craigslist(city)
    get_description()
    get_contact_info()

