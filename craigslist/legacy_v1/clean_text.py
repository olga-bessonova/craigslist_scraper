import re

def clean_text(s: str) -> str:
    return re.sub(r"[\n\r\t]", " ", s).replace(",", ";").strip()

if __name__ == "__main__":
    main()
