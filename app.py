from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pytz import timezone, utc
import requests
import argparse
from pyvirtualdisplay import Display
import logger
import traceback


LOGIN_PAGE = "https://www.su.rhul.ac.uk//sso/login.ashx?ReturnUrl=/"
MAX_WAIT = 15
LOCAL_TIME_ZONE = "Europe/London"


def main():
    args = get_login_details()

    chromedriver_autoinstaller.install()

    browser = webdriver.Chrome()

    login(browser, args)
    browser.close()


def get_login_details():
    start_time = datetime.now().date()

    parser = argparse.ArgumentParser(description="Mark attendance for RHUL")

    parser.add_argument("-u", "--username",
                        help="Full username for RHUL", required=True)

    parser.add_argument("-p", "--password",
                        help="Password for RHUL", required=True)

    parser.add_argument("-s", "--start-date",
                        help="Date to start searching from", type=datetime.fromisoformat, default=start_time)

    return vars(parser.parse_args())


def login(browser, args):
    # Navigate to Login page
    browser.get(LOGIN_PAGE)

    # Login
    browser.find_element(By.ID, "userNameInput").send_keys(args["username"])
    browser.find_element(By.ID, "passwordInput").send_keys(args["password"])
    browser.find_element(By.ID, "submitButton").click()

    return browser.current_url == "https://su.rhul.ac.uk/"



if __name__ == "__main__":
    try:
        main()
    except:
        err = traceback.format_exc()
        logger.logError(err)
