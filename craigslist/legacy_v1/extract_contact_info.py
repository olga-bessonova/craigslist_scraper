import re
import logging
import os
import requests
from typing import Dict, Tuple, List, Optional
from ..config import HF_NER_ENDPOINT
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

def extract_contact_info(text: str) -> Dict[str, str]:

    # Debug token prefix (as in original)
    if HF_TOKEN:
        logging.info(f"Loaded token prefix: {HF_TOKEN[:10]}")
    else:
        logging.info("HF_TOKEN not set (continuing without it).")

    # Try HF call (not strictly needed for regex extraction, but kept for parity)
    try:
        if HF_TOKEN:
            r = requests.post(
                HF_NER_ENDPOINT,
                json={"inputs": text[:400]},
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                timeout=10,
            )
            _ = r.json()  # entities = _.get('0', [])  # not used, like original
    except Exception as e:
        logging.error(f"Error with Hugging Face API: {e}")

    email = "NO EMAIL"
    phone = "NO PHONE"
    website = "NO WEBSITE"

    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}\b", text, re.I)
    phone_match = re.search(r"(\+?\d{1,3})?[\s\-.(]*\d{3}[\s\-.)]*\d{3}[\s\-]*\d{4}", text)
    url_match = re.search(r"\bhttps?://[^\s<>'\"]+", text, re.I)

    if email_match:
        email = email_match.group(0)
    if phone_match:
        phone = phone_match.group(0)
    if url_match:
        website = url_match.group(0)

    return {"email": email, "phone": phone, "website": website}
