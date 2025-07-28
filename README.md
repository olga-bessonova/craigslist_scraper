# Craigslist Scraper

Python-based scraper to create a database of listings from Craigslist.  
Extracts titles, links, descriptions, email addresses, and phone numbers; saves everything to structured CSV files.

---

## Features

- Headless browsing with Selenium & **undetected‑chromedriver**  
- Dynamic infinite scrolling to load *all* listings  
- Eliminate duplicates by title  
- Normalize and extract:
  - Emails (including obfuscated formats like `name (at) domain dot com`)
  - Phone numbers (U.S. formats, strip leading `+1` if present)
- Centralized logging setup via **`logger.py`**  
- Output CSVs saved under `database/` folder

---

## Project Layout
![Screenshot](misc/structure.jpg)
<!-- craigslist_scraper/
│
├── craigslist/ ← Python modules
│ ├── scrape_craigslist.py ← Scrapes listings: title + link
│ ├── get_description.py ← Fetches listing description (postingbody)
│ ├── extract_emails.py ← Email extraction utility
│ ├── extract_phonenumbers.py ← Phone extraction utility
│ └── logger.py ← Logging setup
│
├── database/ ← CSV output data
│ ├── craigslist_t_l.csv ← Titles + Links
│ ├── craigslist_t_l_d.csv ← With Descriptions
│ └── craigslist_t_l_d_contacts.csv ← With Email & Phone columns
│
├── output/ ← Log files
│ └── craigslist_scraper.log
│
├── main.py ← Orchestration: run scraping, descriptions, contact info
├── requirements.txt ← Python dependencies
└── README.md ← This file -->

## Running this app
- Clone the repository 
```
git clone https://github.com/olga-bessonova/craigslist_scraper.git
cd craigslist_scraper
```
- Create and activate a virtualenv
```
python3 -m venv venv
source venv/bin/activate
```
- Run the full pipeline
```
python main.py
```

This runs:

scrape_craigslist() → generates craigslist_t_l.csv
get_description() → generates craigslist_t_l_d.csv
get_contact_info() → final craigslist_t_l_d_contacts.csv
## Logging
- Logging handled centrally via craigslist/logger.py
- Logs are written to output/craigslist_scraper.log
- Use logger.info(), logger.warning(), logger.error() instead of print()

