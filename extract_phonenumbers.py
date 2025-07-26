import re

def extract_phonenumbers(text):
    match = re.search(r'(?:\+1\s*)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}', text)
    if match:
        number = re.sub(r'\D', '', match.group())  # Remove non-digit characters
        if number.startswith('1'):
            number = number[1:]  # Remove leading '1'
        return number
    return "NOT FOUND"