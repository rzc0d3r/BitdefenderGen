from .EmailAPIs import *

import colorama
import platform
import string
import random
import time
import sys

class BitdefenderOPT(object):
    def __init__(self, registered_email_obj, bitdefender_password, driver: Chrome):
        self.driver = driver
        self.email_obj = registered_email_obj
        self.bitdefender_password = bitdefender_password
        self.window_handle = None

    def createAccount(self):
        exec_js = self.driver.execute_script
        uCE = untilConditionExecute

        console_log('\n[FreeTS-Ukraine2022-OPT] Page loading...', INFO)
        if isinstance(self.email_obj, (Hi2inAPI, TenMinuteMailAPI, TempMailAPI, GuerRillaMailAPI)):
            self.driver.switch_to.new_window('Bitdefender')
            self.window_handle = self.driver.current_window_handle
        self.driver.get('https://www.bitdefender.com/media/html/consumer/new/Free-TS-Ukraine2022-opt/')
        uCE(self.driver, f'return {GET_EBAV}("iframe", "title", "reCAPTCHA") != null')
        console_log('[FreeTS-Ukraine2022-OPT] Page is loaded!', OK)

        self.driver.find_element('id', 'email').send_keys(self.email_obj.email)
        console_log('\nInitializing reCAPTCHA...', INFO)
        recaptcha_iframe = exec_js(f'return {GET_EBAV}("iframe", "title", "reCAPTCHA")')
        self.driver.switch_to.frame(recaptcha_iframe)
        exec_js(f'{GET_EBID}("rc-anchor-alert").click()')
        time.sleep(1)
        solved = False
        for i in range(DEFAULT_MAX_ITER*2):
            if i == 1:
                print(f'[  {colorama.Fore.YELLOW}INPT{colorama.Fore.RESET}  ] {colorama.Fore.CYAN}Please solve the reCAPTCHA!!!{colorama.Fore.RESET}')
            try:
                if self.driver.find_element('id', 'recaptcha-anchor').get_attribute('aria-checked') == 'true':
                    console_log('ReCAPTCHA was successfully solved!!!', OK)
                    self.driver.switch_to.default_content()
                    exec_js(f'return {GET_EBID}("btnBuy")').click()
                    solved = True
                    break
            except:
                pass
            time.sleep(DEFAULT_DELAY)
        if not solved:
            raise RuntimeError('Waiting time for reCAPTCHA solution has been exceeded or another error has occurred!!!')
        
        console_log('\n[Register] Page loading...', INFO)
        uCE(self.driver, f'return {GET_EBID}("first_name_input") != null')
        console_log('[Register] Page is loaded!\n', OK)
        console_log('Data filling...', INFO)
        exec_js(f'return {GET_EBID}("first_name_input")').send_keys(''.join([random.choice(string.ascii_letters) for _ in range(random.randint(10, 20))]))
        exec_js(f'return {GET_EBID}("password_strong_input")').send_keys(self.bitdefender_password)
        exec_js(f'{GET_EBID}("signup-terms-checkbox").click()')
        exec_js(f'{GET_EBID}("submit-create").click()')
        console_log('Successfully!!!', OK)

        console_log('\nCreating an account...', INFO)
        time.sleep(1.5)
        if self.driver.page_source.find('Activate your account') != -1:
            self.confirmAccount()
            console_log('Account successfully created!!!', OK)
            return True
        else:
            for _ in range(DEFAULT_MAX_ITER):
                if self.driver.page_source.find('Welcome') != -1:
                    console_log('Account successfully created!!!', OK)
                    return True
                time.sleep(DEFAULT_DELAY)
        raise RuntimeError('Account creation error!!!') 
    
    #Activate your account
    def confirmAccount(self):
        uCE = untilConditionExecute
        if isinstance(self.email_obj, CustomEmailAPI):
            token = parseToken(self.email_obj, max_iter=100, delay=3)
        else:
            console_log(f'\n[{self.email_obj.class_name}] Bitdefender-Token interception...', INFO)
            if isinstance(self.email_obj, (Hi2inAPI, TenMinuteMailAPI, TempMailAPI, GuerRillaMailAPI)):
                token = parseToken(self.email_obj, self.driver, max_iter=100, delay=3)
                self.driver.switch_to.window(self.window_handle)
            else:
                token = parseToken(self.email_obj, max_iter=100, delay=3) # 1secmail, developermail
        console_log(f'Bitdefender-Token: {token}', OK)
        console_log('\nAccount confirmation is in progress...', INFO)
        self.driver.get(f'https://login.bitdefender.com/validate?lang=en_US&{token}')
        console_log('Account successfully confirmed!!!\n', OK)
        return True