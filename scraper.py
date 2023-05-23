from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class PickScraper():
    def __init__(self):
        driver = webdriver.Chrome()
        driver.get("https://app.prizepicks.com/board")
        time.sleep(2)
