#Imports
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import http.cookiejar as cookielib
import modules.config as config

#Get session
def get_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504, 104),
    session=None,
):
    """Get a session, and retry in case of an error"""
    session = session or requests.Session()
    if config.cookies is not None:  # add cookies if present
        cookies = cookielib.MozillaCookieJar(config.cookies)
        cookies.load()
        session.cookies = cookies
    session.headers.update({"User-Agent": config.user_agent})
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


import logging
class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
