import logging

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a handler to write into a file
    file_handler = logging.FileHandler("output/craigslist_scraper.log",
                                       encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)

    # Prevent duplicated log handlers
    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger