import requests
import logging
import time
import random
import signal
from .config import USER_AGENTS, DEFAULT_HEADERS_BASE
from craigslist.logger import get_logger

logger = get_logger()


# SIGINT handler to stop between requests
STOP_REQUESTED = False

# ---------- Signal Handling ----------

def handle_sigint(signum, frame):
    global STOP_REQUESTED
    logging.info("Received SIGINT. Will stop after current step...")
    STOP_REQUESTED = True

signal.signal(signal.SIGINT, handle_sigint)

def delay(ms: int) -> None:
    """Synchronous sleep in milliseconds."""
    time.sleep(ms / 1000.0)


def random_delay(min_ms: int = 1000, max_ms: int = 3000) -> int:
    ms = random.randint(min_ms, max_ms)
    delay(ms)
    return ms


def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)

def create_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update(DEFAULT_HEADERS_BASE)
    sess.headers["User-Agent"] = get_random_user_agent()
    return sess


def fetch_with_retry(session: requests.Session, url: str, max_retries: int = 3, timeout: int = 30) -> str:
    """
    Fetch a URL with basic retry and randomized waits between attempts.
    Returns the response text or raises an exception on final failure.
    """
    for attempt in range(1, max_retries + 1):
        if STOP_REQUESTED:
            raise KeyboardInterrupt("Stop requested, aborting fetch.")
        try:
            resp = session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logging.warning(f"Navigation attempt {attempt} failed for {url}: {e}")
            if attempt == max_retries:
                raise
            random_delay(2000, 5000)
    # Should never get here
    raise RuntimeError(f"Failed to fetch {url}")

