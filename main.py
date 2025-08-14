import sys
from craigslist.scrape_craigslist import scrape_craigslist
from craigslist.get_description import get_description
from craigslist.get_contact_info import get_contact_info

from craigslist.city_list import city_list 


if __name__ == "__main__":
    # for city, base_url in city_list[297:]:
        # city, base_url = city_list[241] # example for new york
        # scrape_craigslist(city, base_url)
    get_description()
    get_contact_info()


