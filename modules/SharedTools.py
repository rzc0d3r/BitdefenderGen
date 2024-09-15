from selenium.webdriver import Chrome, ChromeOptions, ChromeService
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxService
from selenium.webdriver import Edge, EdgeOptions, EdgeService

import logging

logger = logging.getLogger('selenium')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('selenium-logs.txt')
logger.addHandler(handler)
logging.getLogger('selenium.webdriver.remote').setLevel(logging.WARN)
logging.getLogger('selenium.webdriver.common').setLevel(logging.DEBUG)

import traceback
import colorama
import random
import string
import time
import sys
import os
import re

DEFAULT_MAX_ITER = 30
DEFAULT_DELAY = 1
GET_EBCN = 'document.getElementsByClassName'
GET_EBID = 'document.getElementById'
GET_EBTN = 'document.getElementByTagName'
GET_EBAV = 'getElementByAttrValue'
CLICK_WITH_BOOL = 'clickWithBool'
DEFINE_GET_EBAV_FUNCTION = """
function getElementByAttrValue(tagName, attrName, attrValue) {
    for (let element of document.getElementsByTagName(tagName)) {
        if(element.getAttribute(attrName) === attrValue)
            return element } }"""
DEFINE_CLICK_WITH_BOOL_FUNCTION = """
function clickWithBool(object) {
    try {
        object.click()
        return true }
    catch {
        return false } }"""

colorama.init()

class LoggerType:
    def __init__(self, sborder, eborder, title, color, fill_text):
        self.sborder = sborder
        self.eborder = eborder
        self.title = title
        self.color = color
        self.fill_text = fill_text

    @property
    def data(self):
        return self.sborder + self.color + self.title + colorama.Style.RESET_ALL + self.eborder

ERROR = LoggerType('[ ', ' ]', 'FAILED', colorama.Fore.RED, True)
OK = LoggerType('[   ', '   ]', 'OK', colorama.Fore.GREEN, False)
INFO = LoggerType('[  ', '  ]', 'INFO', colorama.Fore.LIGHTBLACK_EX, True)
DEVINFO = LoggerType('[ ', ' ]', 'DEBUG', colorama.Fore.CYAN, True)
WARN = LoggerType('[  ', '  ]', 'WARN', colorama.Fore.YELLOW, False)

def console_log(text='', logger_type=None, fill_text=None):
    if isinstance(logger_type, LoggerType):
        ni = 0
        for i in range(0, len(text)):
            if text[i] != '\n':
                ni = i
                break
            print()
        if fill_text is None:
            fill_text = logger_type.fill_text
        if fill_text:
            print(logger_type.data + ' ' + logger_type.color + text[ni:] + colorama.Style.RESET_ALL)
        else:
            print(logger_type.data + ' ' + text[ni:])
    else:
        print(text)

from .WebDriverInstaller import GOOGLE_CHROME, MICROSOFT_EDGE, MOZILLA_FIREFOX

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def untilConditionExecute(driver_obj, js: str, delay=DEFAULT_DELAY, max_iter=DEFAULT_MAX_ITER, positive_result=True, raise_exception_if_failed=True, return_js_result=False):
    driver_obj.execute_script(f'window.{GET_EBAV} = {DEFINE_GET_EBAV_FUNCTION}')
    driver_obj.execute_script(f'window.{CLICK_WITH_BOOL} = {DEFINE_CLICK_WITH_BOOL_FUNCTION}')
    pre_js = [
        DEFINE_GET_EBAV_FUNCTION,
        DEFINE_CLICK_WITH_BOOL_FUNCTION
    ]
    js = '\n'.join(pre_js+[js])
    for _ in range(max_iter):
        try:
            result = driver_obj.execute_script(js)
            if return_js_result and result is not None:
                return result
            elif result == positive_result:
                return True
        except Exception as E:
            pass
        time.sleep(delay)
    if raise_exception_if_failed:
        raise RuntimeError('untilConditionExecute: the code did not return the desired value! TRY VPN!')

def dataGenerator(length, only_numbers=False, only_letters=False):
    """generates a password by default. If only_numbers=True - phone number"""
    data = []
    if only_letters:
        data = [random.choice(string.ascii_letters) for _ in range(length)]
    elif only_numbers: # phone number
        data = [random.choice(string.digits) for _ in range(length)]
    else: # password
        length += random.randint(1, 10)
        data = [ # 1 uppercase & lowercase letter, 1 number, 1 special character
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")
        ]
        characters = string.ascii_letters + string.digits + string.punctuation
        data += [random.choice(characters) for _ in range(length-3)]
        random.shuffle(data)
    return ''.join(data)

def initSeleniumWebDriver(browser_name: str, webdriver_path = None, browser_path = '', headless=True):
    if browser_path is None:
        browser_path = ''
    console_log(f'{colorama.Fore.LIGHTMAGENTA_EX}-- Browsers Initializer --{colorama.Fore.RESET}\n')
    if os.name == 'posix': # For Linux
        if sys.platform.startswith('linux'):
            console_log(f'Initializing {browser_name} for Linux', INFO)
        elif sys.platform == "darwin":
            console_log(f'Initializing {browser_name} for macOS', INFO)
    elif os.name == 'nt':
        console_log(f'Initializing {browser_name} for Windows', INFO)
    driver_options = None
    driver = None
    if browser_name == GOOGLE_CHROME:
        driver_options = ChromeOptions()
        driver_options.binary_location = browser_path
        driver_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver_options.add_argument("--log-level=3")
        driver_options.add_argument("--lang=en-US")
        if headless:
            driver_options.add_argument('--headless')
        if os.name == 'posix': # For Linux
            driver_options.add_argument('--no-sandbox')
            driver_options.add_argument('--disable-dev-shm-usage')
        try:
            driver = Chrome(options=driver_options, service=ChromeService(executable_path=webdriver_path))
        except Exception as e:
            if traceback.format_exc().find('only supports') != -1: # Fix for downloaded chrome update
                browser_path = traceback.format_exc().split('path')[-1].split('Stacktrace')[0].strip()
                if 'new_chrome.exe' in os.listdir(browser_path[:-10]):
                    console_log('Downloaded Google Chrome update is detected! Using new chrome executable file!', INFO)
                    browser_path = browser_path[:-10]+'new_chrome.exe'
                    driver_options.binary_location = browser_path
                    driver = Chrome(options=driver_options, service=ChromeService(executable_path=webdriver_path))
            else:
                raise e
    elif browser_name == MICROSOFT_EDGE:
        driver_options = EdgeOptions()
        driver_options.use_chromium = True
        driver_options.binary_location = browser_path
        driver_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver_options.add_argument("--log-level=3")
        driver_options.add_argument("--lang=en-US")
        if headless:
            driver_options.add_argument('--headless')
        if os.name == 'posix': # For Linux
            driver_options.add_argument('--no-sandbox')
            driver_options.add_argument('--disable-dev-shm-usage')
        driver = Edge(options=driver_options, service=EdgeService(executable_path=webdriver_path))
    elif browser_name == MOZILLA_FIREFOX:
        driver_options = FirefoxOptions()
        if browser_path.strip() != '':
            driver_options.binary_location = browser_path
        driver_options.set_preference('intl.accept_languages', 'en-US')
        if headless:
            driver_options.add_argument('--headless')
        if os.name == 'posix': # For Linux
            driver_options.add_argument('--no-sandbox')
            driver_options.add_argument("--disable-dev-shm-usage")
        # Fix for: Your firefox profile cannot be loaded. it may be missing or inaccessible
        try:
            os.makedirs('firefox_tmp')
        except:
            pass
        os.environ['TMPDIR'] = (os.getcwd()+'/firefox_tmp').replace('\\', '/')
        driver = Firefox(options=driver_options, service=FirefoxService(executable_path=webdriver_path))
    return driver

def parseToken(email_obj, driver=None, delay=DEFAULT_DELAY, max_iter=DEFAULT_MAX_ITER):
    activated_href = None
    if email_obj.class_name == 'custom':
        while True:
            activated_href = input(f'\n[  {colorama.Fore.YELLOW}INPT{colorama.Fore.RESET}  ] {colorama.Fore.CYAN}Enter the link to activate your account, it will come to the email address you provide: {colorama.Fore.RESET}').strip()
            if activated_href is not None:
                match = re.search(r'user_token=[a-zA-Z0-9._-]+&redirect_url=[a-zA-Z0-9._%-]+&check_pass=false', activated_href)
                if match is not None:
                    token = match.group()
                    if len(token) > 400:
                        return token
            console_log('Incorrect link syntax', ERROR)
    for _ in range(max_iter):
        if email_obj.class_name == '1secmail':
            json = email_obj.read_email()
            if json != []:
                message = json[-1]
                if message['subject'].find('Confirm') != -1:
                    activated_href = email_obj.get_message(message['id'])['body']
        elif email_obj.class_name == 'developermail':
            messages = email_obj.get_messages()
            if messages is not None:
                message = messages[-1]
                if message['subject'].find('Confirm') != -1:
                    activated_href = message['body']
        elif email_obj.class_name == 'hi2in':
            email_obj.open_inbox()
            try:
                activated_href = driver.find_element('xpath', "//a[starts-with(@href, 'https://login.bitdefender.com/validate?')]").get_attribute('href')
            except:
                pass
        elif email_obj.class_name in ['guerrillamail', '10minutemail', 'mailticking']:
            inbox = email_obj.parse_inbox()
            for mail in inbox:
                mail_id, mail_from, mail_subject = mail
                if mail_from.find('info.bitdefender.com') != -1 or mail_subject.find('Confirm') != -1:
                    email_obj.open_mail(mail_id)
                    if email_obj.class_name == 'mailticking':
                        time.sleep(1.5)
                    try:
                        activated_href = driver.find_element('xpath', "//a[starts-with(@href, 'https://login.bitdefender.com/validate?')]").get_attribute('href')
                    except:
                        pass
        if activated_href is not None:
            match = re.search(r'user_token=[a-zA-Z0-9._-]+&redirect_url=[a-zA-Z0-9._%-]+&check_pass=false', activated_href)
            if match is not None:
                token = match.group()
                return token
        time.sleep(delay)
    raise RuntimeError('Token retrieval error!!!')
