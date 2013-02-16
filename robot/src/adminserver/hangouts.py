import os
import time
import urllib2
from itertools import count

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

import config
from session import Session as RobotSession

WAIT_FOR_ELEMENT_SECS = 60

HANGOUT_BASE_URL = 'https://plus.google.com/hangouts/_'
LOGIN_URL = 'https://accounts.google.com/Login'

LOGIN_FIELDS = {
    'username': 'Email',
    'password': 'Passwd'
}
JOIN_BUTTON_TEXT = 'Join'

# TODO move to config.py, and then to somewhere better
USERNAME = 'telepresent001'
PASSWORD = 'selenium'

def start_hangout(url, robot_sid):
    """Start google hangout in a selenium chromebrowser instance."""
    #
    # TODO if we have no network at this point, we fail, then never get a
    #  control port and can't close the selenium hangout
    #
    hangout = HangoutSession()
    robot_session = RobotSession(robot_sid)
    robot_session.set('hangout_control_port', hangout.driver.service.port)
    hangout.join_hangout(url)


def stop_hangout(control_port):
    """Stop the active google hangout session."""
    try:
        # shutdown chromedriver
        urllib2.urlopen("http://127.0.0.1:%s/shutdown" % control_port)
    except urllib2.URLError:
        # TODO handle
        raise


class HangoutSession(object):
    def __init__(self, username=USERNAME, password=PASSWORD):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(WAIT_FOR_ELEMENT_SECS)
        if not self._is_logged_in:
            self._login(username, password)

    def join_hangout(self, url):
        # TODO commented-out until we settle on a url format...
        #if HANGOUT_BASE_URL not in url:
        #    raise ValueError("Invalid google hangout URL.")
        self.driver.get(url)
        # TODO this is silly and slow as hell.
        time.sleep(30)
        for i in count():
            if i > 10:
                raise NoSuchElementException("Could not locate the join-hangout button after 10 tries.")
            try:
                buttons = self.driver.find_elements_by_css_selector('div[role="button"]')
            except NoSuchElementException:
                time.sleep(2)
                continue
            try:
                button = [b for b in buttons if JOIN_BUTTON_TEXT in b.text][0]
                break
            except IndexError:
                pass

        button.click()

    def _login(self, username, password):
        self.driver.get(LOGIN_URL)
        self.driver.find_element_by_id(LOGIN_FIELDS['username']).send_keys(username)
        el = self.driver.find_element_by_id(LOGIN_FIELDS['password'])
        el.send_keys(password)
        el.submit()

    @property
    def _is_logged_in(self):
        cookies = [(c['domain'], c['name']) for c in self.driver.get_cookies()]
        if ('.google.com', 'SSID') in cookies:
            return True
        else:
            return False
