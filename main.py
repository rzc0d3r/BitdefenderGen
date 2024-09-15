from modules.WebDriverInstaller import *
from modules.BitdefenderTools import *
from modules.SharedTools import *
from modules.EmailAPIs import *
from modules.Updater import get_assets_from_version, parse_update_json, updater_main
from modules.MBCI import *

import traceback
import colorama
import platform
import datetime
import argparse
import time
import sys
import re

VERSION = ['v1.0.1.0', 1010]
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
if '--no-logo' in sys.argv:
    LOGO = f"ESET KeyGen {VERSION[0]} by rzc0d3r\n"
if datetime.datetime.now().day == 6 and datetime.datetime.now().month == 8: # Birthday of rzc0d3r
    colored_logo = ''
    colors = [getattr(Fore, attr) for attr in dir(Fore) if not attr.startswith('__')]
    colors.remove(Fore.BLACK)
    colors.remove(Fore.WHITE)
    colors.remove(Fore.LIGHTWHITE_EX)
    for line in LOGO.split('\n'):
        for ch in line:
            color = random.choice(colors)
            colored_logo += (color+ch+Fore.RESET)
        colored_logo += '\n'
    colored_logo += f'{Fore.GREEN}rzc0d3r{Fore.RESET} celebrates his {Fore.LIGHTRED_EX}birthday{Fore.RESET} today!!! :)\n'
    LOGO = colored_logo

# -- Quick settings [for Developers to quickly change behavior without changing all files] --
DEFAULT_EMAIL_API = 'mailticking'
AVAILABLE_EMAIL_APIS = ['10minutemail', 'mailticking']
WEB_WRAPPER_EMAIL_APIS = ['10minutemail', 'mailticking']
EMAIL_API_CLASSES = {
    '10minutemail': TenMinuteMailAPI,           
    'mailticking': MailTickingAPI
}

args = {
    'chrome': True,
    'firefox': False,
    'edge': False,
        
    'account': False,
    'only_webdriver_update': False,
    'update': False,
    
    'skip_webdriver_menu': False,
    'no_headless': True,
    'custom_browser_location': '',
    'email_api': DEFAULT_EMAIL_API,
    'custom_email_api': False,
    'skip_update_check': False,
    'no_logo': False,
    'disable_progress_bar': False
}

def RunMenu():
    MainMenu = ViewMenu(LOGO+'\n---- Main Menu ----')

    SettingMenu = ViewMenu(LOGO+'\n---- Settings Menu ----')
    SettingMenu.add_item(
        OptionAction(
            args,
            title='Browsers',
            action='store_true',
            args_names=['chrome', 'firefox', 'edge'],
            default_value='chrome'
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args,
            title='Modes of operation',
            action='store_true',
            args_names=['account', 'only-webdriver-update', 'update'],
            default_value='account'
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args,
            title='Email APIs',
            action='choice',
            args_names='email-api',
            choices=AVAILABLE_EMAIL_APIS,
            default_value=DEFAULT_EMAIL_API
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args,
            title='--skip-webdriver-menu',
            action='bool_switch',
            args_names='skip-webdriver-menu'
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args,
            title='--no-headless',
            action='bool_switch',
            args_names='no-headless'
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args,
            title='--custom-browser-location',
            action='manual_input',
            args_names='custom-browser-location',
            default_value=''
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args,
            title='--custom-email-api',
            action='bool_switch',
            args_names='custom-email-api'
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args,
            title='--skip-update-check',
            action='bool_switch',
            args_names='skip_update_check'
        )
    )
    SettingMenu.add_item(
        OptionAction(
            args,
            title='--disable-progress-bar',
            action='bool_switch',
            args_names='disable_progress_bar'
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
        #global MENU_EXECUTION
        #MENU_EXECUTION = True
        RunMenu()
    else: # CLI
        args_parser = argparse.ArgumentParser()
        # Required
        ## Browsers
        args_browsers = args_parser.add_mutually_exclusive_group(required=('--update' not in sys.argv))
        args_browsers.add_argument('--chrome', action='store_true', help='Launching the project via Google Chrome browser')
        args_browsers.add_argument('--firefox', action='store_true', help='Launching the project via Mozilla Firefox browser')
        args_browsers.add_argument('--edge', action='store_true', help='Launching the project via Microsoft Edge browser')
        ## Modes of operation
        args_modes = args_parser.add_mutually_exclusive_group(required=True)
        args_modes.add_argument('--account', action='store_true', help='Creating a Bitdefender Account (90 days license)')
        args_modes.add_argument('--only-webdriver-update', action='store_true', help='Updates/installs webdrivers and browsers without generating account')
        args_modes.add_argument('--update', action='store_true', help='Switching to program update mode - Overrides all arguments that are available!!!')
        # Optional
        args_parser.add_argument('--skip-webdriver-menu', action='store_true', help='Skips installation/upgrade webdrivers through the my custom wrapper (The built-in selenium-manager will be used)')
        args_parser.add_argument('--no-headless', action='store_true', default=True, help='Shows the browser at runtime (The browser is hidden by default, but on Windows 7 this option is enabled by itself)')
        args_parser.add_argument('--custom-browser-location', type=str, default='', help='Set path to the custom browser (to the binary file, useful when using non-standard releases, for example, Firefox Developer Edition)')
        args_parser.add_argument('--email-api', choices=AVAILABLE_EMAIL_APIS, default=DEFAULT_EMAIL_API, help='Specify which api to use for mail')
        args_parser.add_argument('--custom-email-api', action='store_true', help='Allows you to manually specify any email, and all work will go through it. But you will also have to manually read inbox and do what is described in the documentation for this argument')
        args_parser.add_argument('--disable-progress-bar', action='store_true', help='Disables the webdriver download progress bar')
        args_parser.add_argument('--no-logo', action='store_true', help='Replaces ASCII-Art with plain text')
        args_parser.add_argument('--skip-update-check', action='store_true', help='Skips checking for program updates')
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
        # changing input arguments for special cases
        if platform.release() == '7' and sys.platform.startswith('win'): # fix for Windows 7
            args['no_headless'] = True
        # check program updates
        if args['update']:
            print(f'{Fore.LIGHTMAGENTA_EX}-- Updater --{Fore.RESET}\n')
            updater_main(from_main=True) # from_main - changes the behavior in Updater so that everything works correctly from under main.py
            if len(sys.argv) == 1:
                input('\nPress Enter to exit...')
            else:
                time.sleep(3) # exit-delay
            sys.exit(0)
        if not args['skip_update_check'] and not args['update']:
            try:
                if parse_update_json(from_main=True) is not None:
                    print(f'{Fore.LIGHTMAGENTA_EX}-- Updater --{Fore.RESET}\n')
                    latest_cloud_version = get_assets_from_version(parse_update_json(from_main=True), 'latest')['version']
                    latest_cloud_version_int = latest_cloud_version[1:].split('.')
                    latest_cloud_version_int = int(''.join(latest_cloud_version_int[:-1])+latest_cloud_version_int[-1][0])
                    if VERSION[1] > latest_cloud_version_int:
                        console_log(f'The project has an unreleased version, maybe you are using a build from the developer?\n', WARN, True)
                    elif latest_cloud_version_int > VERSION[1]:
                        console_log(f'Project update is available up to version: {colorama.Fore.GREEN}{latest_cloud_version}{colorama.Fore.RESET}', WARN)
                        console_log('If you want to download the update run this file with --update argument\n', WARN)
                    else:
                        console_log('Project up to date!!!\n', OK)
            except:
                pass
        # initialization and configuration of everything necessary for work            
        driver = None
        webdriver_path = None
        browser_name = GOOGLE_CHROME
        if args['firefox']:
            browser_name = MOZILLA_FIREFOX
        if args['edge']:
            browser_name = MICROSOFT_EDGE
        if not args['skip_webdriver_menu']: # updating or installing webdriver
            if args['custom_browser_location'] != '':
                webdriver_installer = WebDriverInstaller(browser_name, args['custom_browser_location'])
            else:
                webdriver_installer = WebDriverInstaller(browser_name)
            webdriver_path, args['custom_browser_location'] = webdriver_installer.menu(args['disable_progress_bar'])
        if not args['only_webdriver_update']:
            driver = initSeleniumWebDriver(browser_name, webdriver_path, args['custom_browser_location'], (not args['no_headless']))
            if driver is None:
                raise RuntimeError(f'{browser_name} initialization error!')
        else:
            sys.exit(0)

        # main part of the program
        console_log(f'\n{Fore.LIGHTMAGENTA_EX}-- Generator --{Fore.RESET}\n')
        if not args['custom_email_api']:  
            console_log(f'[{args["email_api"]}] Mail registration...', INFO)
            if args['email_api'] in WEB_WRAPPER_EMAIL_APIS: # WebWrapper API, need to pass the selenium object to the class initialization
                email_obj = EMAIL_API_CLASSES[args['email_api']](driver)
            else: # real APIs without the need for a browser
                email_obj = EMAIL_API_CLASSES[args['email_api']]()
            try:
                email_obj.init()
                console_log('Mail registration completed successfully!', OK)
            except:
                pass
        else:
            email_obj = CustomEmailAPI()
            while True:
                email = input(f'[  {colorama.Fore.YELLOW}INPT{colorama.Fore.RESET}  ] {colorama.Fore.CYAN}Enter the email address you have access to: {colorama.Fore.RESET}').strip()
                try:
                    matched_email = re.match(r'[-a-z0-9+.]+@[a-z]+(\.[a-z]+)+', email).group()
                    if matched_email == email:
                        email_obj.email = matched_email
                        console_log('Mail has the correct syntax!', OK)
                        break
                    else:
                        raise RuntimeError
                except:
                    console_log('Invalid email syntax!!!', ERROR)
        
        # Generator
        bitdefender_password = dataGenerator(12)
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
    if globals().get('driver', None) is not None:
        driver.quit()
    sys.exit()

if __name__ == '__main__':
    parse_argv() # if Menu, the main function will be called in automatic mode
    if len(sys.argv) > 1: # CLI
        main()