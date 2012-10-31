import time
from itertools import count

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

WAIT_FOR_ELEMENT_SECS = 60

HANGOUT_BASE_URL = 'https://plus.google.com/hangouts/_'
LOGIN_URL = 'https://accounts.google.com/Login'

LOGIN_FIELDS = {
    'username': 'Email',
    'password': 'Passwd'
}
JOIN_BUTTON_TEXT = 'Join'

# TODO move to config.py
USERNAME = 'telepresent001'
PASSWORD = 'selenium'

class HangoutSession(object):
    def __init__(self, hangout_url, username=USERNAME, password=PASSWORD):
        self.hangout_url = hangout_url
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(WAIT_FOR_ELEMENT_SECS)
        if not self._is_logged_in:
            self._login(username, password)
        self._join_hangout(hangout_url)

    def _join_hangout(self, url):
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
