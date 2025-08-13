import re

def extract_phonenumbers(text):
    # Remove URLs to avoid false positives
    text = re.sub(r'https?://\S+', '', text)

    # Match U.S. phone numbers with space, dash, or parentheses, but NOT raw 10-digit numbers
    matches = re.findall(
        r'(?:\+1\s*)?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{4}', 
        text
    )

    # Clean up and deduplicate
    seen = set()
    numbers = []
    for match in matches:
        number = re.sub(r'\D', '', match)  # Remove non-digits
        if number.startswith('1') and len(number) == 11:
            number = number[1:]
        if number not in seen:
            seen.add(number)
            numbers.append(number)

    return numbers if numbers else ["NOT FOUND"]
