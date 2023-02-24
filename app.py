from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from pyvirtualdisplay import Display

import chromedriver_autoinstaller
import logger
import time
import traceback
import re
import json
import sys
import requests
import argparse

LOGIN_PAGE = "https://www.su.rhul.ac.uk/sso/login.ashx?ReturnUrl=/organisation/memberlist/7306/"
MEMBER_PAGE = "https://www.su.rhul.ac.uk/organisation/memberlist/7306/"
MAX_WAIT = 15
LOCAL_TIME_ZONE = "Europe/London"
TEST = False
SAVE_FULL_DATA = False

JSON_NAME_TAG = "name"
JSON_STUDENT_ID_TAG = "student-id"

WEBHOOK_MESSAGE = "yooo, {}"


def main():
    if not TEST:
        display = Display(visible=0, size=(1080, 1920))
        display.start()
    args = get_login_details()
    chromedriver_autoinstaller.install()
    browser = webdriver.Chrome()

    login(browser, args)
    member_json = get_members(browser)
    f = open("members.json", "w")
    f.write(member_json)
    f.close()

    logger.logInfo(f"Sending member data to {args['url']}")
    res = requests.post(args["url"], headers={
                        "X-Auth-Token": args["auth"]}, data=member_json)
    logger.logInfo(f"Status: {res.status_code}")
    logger.logInfo(f"Body: {res.content.decode('utf-8')}")

    browser.close()
    display.stop()

    result = res.content.decode('utf-8')

    # So we don't spam a discord channel
    if not "Added role to 0 members, removed role from 0 members" in result:
        requests.post(args["webhook"], data={
                      'username': args["webhook_name"], 'content': WEBHOOK_MESSAGE.format(result)})

    if res.status_code != 200:
        logger.logError("Non-200 response")
        sys.exit(1)


def get_login_details():
    start_time = datetime.now().date()

    parser = argparse.ArgumentParser(
        description="Scrape registered members of the Computing Society")

    parser.add_argument(
        "-u", "--username", help="Full username for RHUL", required=True
    )

    parser.add_argument("-p", "--password",
                        help="Password for RHUL", required=True)
    parser.add_argument("-l", "--url", help="Compsoc bot URL", required=True)
    parser.add_argument(
        "-a", "--auth", help="CompSoc Bot Authentication Header", required=True)
    parser.add_argument(
        "-w", "--webhook", help="Webhook for reporting status after run", required=False)
    parser.add_argument("-n", "--webhook-name",
                        help="Name of the Webhook", required=False)

    return vars(parser.parse_args())


def login(browser, args):
    logger.logInfo("Logging in")

    # Navigate to Login page
    browser.get(LOGIN_PAGE)

    # Login
    browser.find_element(By.ID, "userNameInput").send_keys(args["username"])
    browser.find_element(By.ID, "passwordInput").send_keys(args["password"])
    browser.find_element(By.ID, "submitButton").click()

    logger.logInfo("Waiting for browser redirect")

    return browser.current_url == "https://su.rhul.ac.uk/"


def get_members(browser):
    logger.logInfo("Getting members")

    # Navigate to member page
    browser.get(MEMBER_PAGE)

    # Display ALL members per page
    drop = Select(browser.find_element(By.ID, "ctl00_Main_ddPageSize"))
    drop.select_by_value("0")

    logger.logInfo("Waiting for members to update")
    time.sleep(4)

    logger.logInfo("Parsing member data")
    table = browser.find_element(By.ID, "ctl00_Main_gvMembers")
    outerhtml = table.get_attribute("outerHTML").replace("\n", "")

    # Parse the HTML table
    # rowRegex = re.compile('<tr class="msl_(alt)?row">(.*)</tr>', re.IGNORECASE)
    rowRegex = re.compile(
        '(<td><a href="\\/profile\\/\\d*\\/">[,. a-zA-Z-]*<\\/a><\\/td><td>\\d*<\\/td>)',
        re.IGNORECASE,
    )
    nameRegex = re.compile(
        '\\/profile\\/\\d*/?">([,. a-zA-Z-]*)<\\/a>', re.IGNORECASE)
    idRegex = re.compile("<\\/a><\\/td><td>(\\d*)<\\/td>", re.IGNORECASE)

    rows = []
    while 1:
        match = rowRegex.search(outerhtml)
        if match is None:
            break

        outerhtml = outerhtml[match.end(0):]
        rows.append(match.group(0))

    logger.logInfo(f"Found {len(rows)} members")

    jsonstruct = []
    for i in range(len(rows)):
        # Don't even @ me for this abomination
        name = nameRegex.search(rows[i]).groups(0)[0]
        id = idRegex.search(rows[i]).groups(0)[0]

        if SAVE_FULL_DATA:
            tmp = dict()
            tmp[JSON_NAME_TAG] = name
            tmp[JSON_STUDENT_ID_TAG] = id
        else:
            tmp = id
        jsonstruct.append(tmp)

    ret = json.dumps({"ids": jsonstruct})
    return ret


if __name__ == "__main__":
    try:
        main()
    except:
        err = traceback.format_exc()
        logger.logError(err)
        sys.exit(1)
