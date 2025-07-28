import csv
from craigslist.extract_emails import extract_emails
from craigslist.extract_phonenumbers import extract_phonenumbers
from craigslist.logger import get_logger

logger = get_logger()

def get_contact_info():
  input_file = "database/craigslist_t_l_d.csv"
  output_file = "database/craigslist_t_l_d_contacts.csv"

  with open(input_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        listings = list(reader)

  for i, row in enumerate(listings):
      description = row.get("description", "")
      email = extract_emails(description)
      phone = extract_phonenumbers(description)
      row["email"] = email
      row["phone_number"] = phone
      logger.info(f"[{i+1}/{len(listings)}] Extracted email: {email}, phone: {phone}")

  with open(output_file, "w", newline="", encoding="utf-8") as f:
      fieldnames = ["title", "link", "description", "email", "phone_number"]
      writer = csv.DictWriter(f, fieldnames=fieldnames)
      writer.writeheader()
      writer.writerows(listings)

  logger.info(f"Done: contact info saved to {output_file}")


if __name__ == "__main__":
  get_contact_info()
