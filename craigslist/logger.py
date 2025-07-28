import logging
import os

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a handler to write into a file
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'craigslist_scraper.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)

     # Console handler (immediate flush)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Prevent duplicated log handlers
    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger