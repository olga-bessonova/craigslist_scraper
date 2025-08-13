import re

def extract_websites(text):
    text = text.lower()

    # Unmask common obfuscations
    text = re.sub(r'\[\s*dot\s*\]|\(\s*dot\s*\)|\bdot\b', '.', text)
    text = re.sub(r'\[\s*slash\s*\]|\(\s*slash\s*\)|\bslash\b', '/', text)
    text = re.sub(r'\[\s*colon\s*\]|\(\s*colon\s*\)|\bcolon\b', ':', text)
    text = re.sub(r'\s+', '', text)  # remove all whitespace

    # Match URLs with or without protocol
    url_pattern = re.compile(
        r'(https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?|www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)'
    )

    raw_urls = re.findall(url_pattern, text)

    # Clean duplicates while preserving order
    seen = set()
    websites = []
    for url in raw_urls:
        if url not in seen:
            seen.add(url)
            websites.append(url)

    return websites if websites else ["NOT FOUND"]
