from modules.WebDriverInstaller import *
from modules.BitdefenderTools import *
from modules.SharedTools import *
from modules.EmailAPIs import *
from modules.MBCI import *

import traceback
import colorama
import platform
import datetime
import argparse
import time
import sys
import os
import re

VERSION = ['v1.0.0.0', 1000]
LOGO = fr"""
    ____   _  __       __       ____                        
   / __ ) (_)/ /_ ____/ /___   / __/___   ____   ___   _____
  / __  |/ // __// __  // _ \ / /_ / _ \ / __ \ / _ \ / ___/
 / /_/ // // /_ / /_/ //  __// __//  __// / / //  __// /    
/_____//_/ \__/ \__,_/ \___//_/   \___//_/ /_/ \___//_/     
   ______                                                   
  / ____/___   ____                                         
 / / __ / _ \ / __ \                                        
/ /_/ //  __// / / /                                        
\____/ \___//_/ /_/     
                        Project Version: {VERSION[0]}
                        Project Devs: rzc0d3r
"""

# -- Quick settings [for Developers to quickly change behavior without changing all files] --
DEFAULT_EMAIL_API = 'developermail'
AVAILABLE_EMAIL_APIS = ['1secmail', '10minutemail', 'developermail']
WEB_WRAPPER_EMAIL_APIS = ['10minutemail', 'hi2in', 'tempmail', 'guerrillamail']
EMAIL_API_CLASSES = {
    'guerrillamail': GuerRillaMailAPI,
    '10minutemail': TenMinuteMailAPI,
    'hi2in': Hi2inAPI,                  
    'tempmail': TempMailAPI,
    '1secmail': OneSecEmailAPI,
    'developermail': DeveloperMailAPI,
}

args = {
    'chrome': True,
    'firefox': False,
    'edge': False,

    'skip_webdriver_menu': False,
    'no_headless': True,
    'custom_browser_location': '',
    'email_api': DEFAULT_EMAIL_API,
    'custom_email_api': False
}

def RunMenu():
    MainMenu = ViewMenu(LOGO+'\n---- Main Menu ----')

    SettingMenu = ViewMenu(LOGO+'\n---- Settings Menu ----')
    SettingMenu.add_item(
        OptionAction(
            args=args,
            title='Browsers',
            action='store_true',
            args_names=['chrome', 'firefox', 'edge'],
            default_value='chrome'
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args=args,
            title='Email APIs',
            action='choice',
            args_names='email-api',
            choices=AVAILABLE_EMAIL_APIS,
            default_value=DEFAULT_EMAIL_API
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args=args,
            title='--skip-webdriver-menu',
            action='bool_switch',
            args_names='skip-webdriver-menu'
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args=args,
            title='--no-headless',
            action='bool_switch',
            args_names='no-headless'
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args=args,
            title='--custom-browser-location',
            action='manual_input',
            args_names='custom-browser-location',
            default_value=''
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args=args,
            title='--custom-email-api',
            action='bool_switch',
            args_names='custom-email-api'
        )
    )
    SettingMenu.add_item(MenuAction('Back', MainMenu))
    MainMenu.add_item(MenuAction('Settings', SettingMenu))
    MainMenu.add_item(MenuAction(f'{colorama.Fore.LIGHTWHITE_EX}Do it, damn it!{colorama.Fore.RESET}', main))
    MainMenu.add_item(MenuAction('Exit', sys.exit))
    MainMenu.view()

def parse_argv():
    print(LOGO)
    if len(sys.argv) == 1: # Menu
        RunMenu()
    else: # CLI
        args_parser = argparse.ArgumentParser()
        # Required
        ## Browsers
        args_browsers = args_parser.add_mutually_exclusive_group(required=('--update' not in sys.argv))
        args_browsers.add_argument('--chrome', action='store_true', help='Launching the project via Google Chrome browser')
        args_browsers.add_argument('--firefox', action='store_true', help='Launching the project via Mozilla Firefox browser')
        args_browsers.add_argument('--edge', action='store_true', help='Launching the project via Microsoft Edge browser')
        # Optional
        args_parser.add_argument('--skip-webdriver-menu', action='store_true', help='Skips installation/upgrade webdrivers through the my custom wrapper (The built-in selenium-manager will be used)')
        args_parser.add_argument('--no-headless', action='store_true', default=True, help='Shows the browser at runtime (The browser is hidden by default, but on Windows 7 this option is enabled by itself)')
        args_parser.add_argument('--custom-browser-location', type=str, default='', help='Set path to the custom browser (to the binary file, useful when using non-standard releases, for example, Firefox Developer Edition)')
        args_parser.add_argument('--email-api', choices=AVAILABLE_EMAIL_APIS, default=DEFAULT_EMAIL_API, help='Specify which api to use for mail')
        args_parser.add_argument('--custom-email-api', action='store_true', help='Allows you to manually specify any email, and all work will go through it. But you will also have to manually read inbox and do what is described in the documentation for this argument')
        try:
            global args
            args = vars(args_parser.parse_args())
        except:
            time.sleep(3)
            sys.exit(-1)

def main():
    if len(sys.argv) == 1: # for Menu
        print()
    try:
        # initialization and configuration of everything necessary for work
        webdriver_installer = WebDriverInstaller()
        # changing input arguments for special cases
        if platform.release() == '7' and sys.platform.startswith('win'): # fix for Windows 7
            args['no_headless'] = True
        driver = None
        webdriver_path = None
        browser_name = 'chrome'
        if args['firefox']:
            browser_name = 'firefox'
        if args['edge']:
            browser_name = 'edge'
        if not args['skip_webdriver_menu']: # updating or installing webdriver
            webdriver_path = webdriver_installer.webdriver_installer_menu(args['edge'], args['firefox'])
            if webdriver_path is not None:
                os.chmod(webdriver_path, 0o777)
        if not args.get('only_webdriver_update', False):
            driver = initSeleniumWebDriver(browser_name, webdriver_path, args['custom_browser_location'], (not args['no_headless']))
            if driver is None:
                raise RuntimeError(f'Initialization {browser_name}-webdriver error!')
        else:
            sys.exit(0)

        # main part of the programd
        if not args['custom_email_api']:  
            console_log(f'\n[{args["email_api"]}] Mail registration...', INFO)
            if args['email_api'] in WEB_WRAPPER_EMAIL_APIS: # WebWrapper API, need to pass the selenium object to the class initialization
                email_obj = EMAIL_API_CLASSES[args['email_api']](driver)
            else: # real APIs without the need for a browser
                email_obj = EMAIL_API_CLASSES[args['email_api']]()
            email_obj.init()
            console_log('Mail registration completed successfully!', OK)
        else:
            email_obj = CustomEmailAPI()
            while True:
                email = input(f'\n[  {colorama.Fore.YELLOW}INPT{colorama.Fore.RESET}  ] {colorama.Fore.CYAN}Enter the email address you have access to: {colorama.Fore.RESET}').strip()
                try:
                    matched_email = re.match(r"[-a-z0-9+]+@[a-z]+\.[a-z]{2,3}", email).group()
                    if matched_email == email:
                        email_obj.email = matched_email
                        console_log('Mail has the correct syntax!', OK)
                        break
                    else:
                        raise RuntimeError
                except:
                    console_log('Invalid email syntax!!!', ERROR)
        
        # generator
        bitdefender_password = dataGenerator(10)
        BitdefenderOPT_object = BitdefenderOPT(email_obj, bitdefender_password, driver)
        
        output_filename = 'BITDEFENDER ACCOUNTS.txt'
        if BitdefenderOPT_object.createAccount():
            output_line = '\n'.join([
                '',
                '----------90-Day Account----------',
                f'Account Email: {email_obj.email}',
                f'Account Password: {bitdefender_password}',
                '----------------------------------',
                ''
            ])
        # end
        console_log(output_line)
        date = datetime.datetime.now()
        f = open(f"{str(date.day)}.{str(date.month)}.{str(date.year)} - "+output_filename, 'a')
        f.write(output_line)
        f.close()
        driver.quit()
    
    except Exception as E:
        traceback_string = traceback.format_exc()
        if str(type(E)).find('selenium') and traceback_string.find('Stacktrace:') != -1: # disabling stacktrace output
            traceback_string = traceback_string.split('Stacktrace:', 1)[0]
        console_log(traceback_string, ERROR)
    if len(sys.argv) == 1:
        input('Press Enter to exit...')
    else:
        time.sleep(3) # exit-delay
    sys.exit()

if __name__ == '__main__':
    parse_argv() # if Menu, the main function will be called in automatic mode
    if len(sys.argv) > 1: # CLI
        main()