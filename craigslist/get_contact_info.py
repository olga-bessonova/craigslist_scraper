import csv
from craigslist.get_emails import extract_emails
from craigslist.get_phonenumbers import extract_phonenumbers
from craigslist.get_websites import extract_websites
from craigslist.logger import get_logger

logger = get_logger()

def get_contact_info():
  input_file  = "database/craigslist_title_link_date_description.csv"
  output_file = "database/craigslist_title_link_date_description_contacts.csv"

  with open(input_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        listings = list(reader)

  for i, row in enumerate(listings):
      description = row.get("description", "")
      email = extract_emails(description)
      phone = extract_phonenumbers(description)
      website = extract_websites(description)
      row["email"] = email
      row["phone_number"] = phone
      row["website"] = website
      logger.info(f"[{i+1}/{len(listings)}] Extracted email: {email}, phone: {phone}, website: {website}")

  with open(output_file, "w", newline="", encoding="utf-8") as f:
      fieldnames = ["city", "title", "link", "date_and_time", "date", "description", "email", "phone_number", "website"]
      writer = csv.DictWriter(f, fieldnames=fieldnames)
      writer.writeheader()
      writer.writerows(listings)

  logger.info(f"Done: contact info saved to {output_file}")


if __name__ == "__main__":
  get_contact_info()
