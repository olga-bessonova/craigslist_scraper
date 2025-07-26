import re

def extract_emails(text):
    # Normalize common email obfuscations
    text = text.lower()
    # Replace at with @
    text = re.sub(r'\s*\[\s*at\s*\]|\s*\(\s*at\s*\)|\s+at\s+', '@', text)
    # Replace dot with "."
    text = re.sub(r'\s*\[\s*dot\s*\]|\s*\(\s*dot\s*\)|\s+dot\s+', '.', text)
    text = text.replace(' ', '')

    # Extract all valid emails
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)

    return emails if emails else ["NOT FOUND"]
