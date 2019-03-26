from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
import Settings


binary = FirefoxBinary(Settings.firefox_binary_path)
fp = webdriver.FirefoxProfile()
fp.add_extension(Settings.ad_block_path)

browser = webdriver.Firefox(firefox_profile=fp, firefox_binary=binary)

browser.get('https://www.youtube.com/watch?v=4_7bPNQxp1o')
time.sleep(15)

browser.close()