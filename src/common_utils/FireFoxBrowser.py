import logging
import time

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options

import settings

log = logging.getLogger(__name__)


class FireFoxBrowser:
    def __init__(self):
        log.info("Creating firefox instance.")
        if settings.ads_block:
            firefox_profile = FirefoxProfile(settings.firefox_profile_rich_config)
        else:
            firefox_profile = FirefoxProfile(settings.firefox_profile_blank)
        log.info("Current firefox profile: {}".format(str(firefox_profile)))
        firefox_option = Options()
        firefox_option.headless = settings.headless
        firefox_option.binary = settings.firefox_binary_path
        log.info("Current firefox headless status: {}, binary path: {}".
                      format(settings.headless, firefox_option.binary_location))
        self.browser = webdriver.Firefox(firefox_profile=firefox_profile, options=firefox_option)
        self.browser.maximize_window()
        self.browser.delete_all_cookies()
        self.browser.get(settings.initial_website)
        log.info("Open initial website: {}".format(settings.initial_website))
        self.SHORT_WAIT = 5
        time.sleep(self.SHORT_WAIT)

    def __enter__(self):
        log.info("Created firefox browser instance.")
        return self.browser

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.quit()
            log.info("Closed firefox browser instance.")
