import re

def extract_emails(text):
    text = text.lower()

    # Temporarily mask "at www." so it doesn't turn into an email
    text = re.sub(r'(?:\[\s*at\s*\]|\(\s*at\s*\)|\bat\b)\s+(?=www\.)', '__BLOCK_AT__', text)

    # Replace obfuscated "at" and "dot"
    text = re.sub(r'\[\s*at\s*\]|\(\s*at\s*\)|\bat\b', '@', text)
    text = re.sub(r'\[\s*dot\s*\]|\(\s*dot\s*\)|\bdot\b', '.', text)

    # Restore "at www." that was intentionally masked
    text = text.replace('__BLOCK_AT__', 'at www.')

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Extract email addresses
    raw_emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)

    # Remove duplicates while preserving order
    seen = set()
    emails = []
    for email in raw_emails:
        if email not in seen:
            seen.add(email)
            emails.append(email)

    return emails if emails else ["NOT FOUND"]
