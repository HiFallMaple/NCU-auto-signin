from ast import Tuple
import re
import sys
import time
import playwright
import logging
from config import *
from type import *
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)



class NotHaveDaysRemainingError(Exception):
    pass

class LoginFailedError(Exception):
    pass

class SigninFailedError(Exception):
    pass

class SignoutFailedError(Exception):
    pass

class NCU:
    browser: Browser
    context: BrowserContext
    page: Page
    account: Account
    headless: bool
    init_cookies: list[Cookie]

    def __init__(self, account: Account,
                 headless: bool = DEFAULT_HEADLESS,
                 cookies: list[Cookie] = DEFAULT_COOKIES) -> None:
        """Init NCU object.

        Args:
            account (Account): TypeDict Account with username and password.
            headless (bool, optional): Arg of p.chromium.launch(). Defaults to config.DEFAULT_HEADLESS.
            cookies (list[Cookie], optional): Cookies that want to be added to the context. Defaults to config.DEFAULT_COOKIES.
        """
        self.account = account
        self.headless = headless
        self.init_cookies = cookies
        self.days_remaining: int = -1

    def __enter__(self) -> "NCU":
        """Start the browser when exit the context manager.

        Returns:
            self: NCU object
        """
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(executable_path=chrome_path, headless=self.headless)
        self.context = self.browser.new_context()
        self.context.add_cookies(self.init_cookies)
        self.page = self.context.new_page()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Close the browser when exit the context manager.

        Args:
            exc_type
            exc_value
            traceback
        """
        self.page.close()
        self.context.close()
        self.browser.close()
        self.p.stop()
        
    def get_days_remaining(self, page) -> int:
        day_locator = page.locator('xpath=/html/body/section/div/div/div[1]/div/div/form/fieldset/div[1]/ul/li[1]')
        self.days_remaining = int(re.search(r'(\d+)\s*天', day_locator.text_content()).group(1))
        
    def has_login_remembered(self) -> bool:
        self.page.goto("https://portal.ncu.edu.tw/")
        response = self.page.wait_for_load_state("networkidle")
        final_url = self.page.url
        if final_url == 'https://portal.ncu.edu.tw/login':
            if self.page.locator('input[name="login-name"]').count() > 0:
                self.get_days_remaining(self.page)
                return True
        logger.error("Don't have login remembered")
        raise NotHaveDaysRemainingError()
        
    def is_login(self) -> bool:
        self.page.goto("https://portal.ncu.edu.tw/")
        response = self.page.wait_for_load_state("networkidle")
        final_url = self.page.url
        if final_url == 'https://portal.ncu.edu.tw':
            logger.debug("Already login")
            return True
        if final_url == 'https://portal.ncu.edu.tw/login':
            if self.has_login_remembered():
                self.pre_login()
                return True
        return False

    def pre_login(self) -> None:
        """Login to the website.

        Raises:
            AlreadyLoginError: If the user is already logged in.
            LoginFailedError: If the login failed.
        """
        logger.debug("pre login")
        self.page.goto("https://portal.ncu.edu.tw/login")
        
        self.page.click('button[type="submit"]')
        logger.debug("submit login form")
        
        response = self.page.wait_for_load_state("networkidle")
        final_url = self.page.url
        
        if final_url == 'https://portal.ncu.edu.tw/login':
            alert_locator = self.page.locator('body > div:nth-child(2) > div > div > div > div')
            if alert_locator.count() == 0:
                logger.error("Can't login. No alert message.")
                raise LoginFailedError("Login failed")
            mes_locator = alert_locator.locator('p')
            mes = mes_locator.text_content()
            if mes.strip() == 'Two factor authentication required':
                logger.info("Two factor authentication required")
                self.page.fill('#totp-code', self.account["totp"].now())
                # click 這部裝置以後不需要驗證
                self.page.locator('body > section > div > div > div:nth-child(1) > div > div > form > div:nth-child(5) > div > label > input').click()
                self.page.locator('button[type="submit"]').click()
            else:
                logger.error(mes)
                raise LoginFailedError(mes)
        elif final_url == 'https://portal.ncu.edu.tw/':
            logger.info("Already login")
        else:
            logger.error("Unknown error")
            raise LoginFailedError("Unknown error")
    
        
    def goto_HumanSys(self) -> None:
            logger.debug("goto HumanSys")
            # if self.is_login():
            #     raise AlreadyLoginError()
            signin_url = "https://cis.ncu.edu.tw/HumanSys/student/stdSignIn/create?ParttimeUsuallyId=247891"
            self.page.goto(signin_url)
            self.page.wait_for_load_state("networkidle")
            if self.page.url == "https://portal.ncu.edu.tw/leaving":
                self.page.click('button[type="submit"]')
    
            try:
                # redirect to the home page after login successfully
                self.page.wait_for_url(signin_url, timeout=10000)
            except playwright._impl._errors.Error as e:
                # if the page doesn't redirect, check the error message
                message = self.get_login_failed_message()
                logger.error(message)
                raise LoginFailedError(message)

    def signin_HumanSys(self) -> None:

        self.goto_HumanSys()
        self.page.click('#signin')

        try:
            # https://cis.ncu.edu.tw/HumanSys/student/stdSignIn/create?ParttimeUsuallyId=247891&msg=signin_ok
            self.page.wait_for_url("https://cis.ncu.edu.tw/HumanSys/student/stdSignIn/create?ParttimeUsuallyId=247891&msg=signin_ok")
        except playwright._impl._errors.Error as e:
            # if the page doesn't redirect, check the error message
            message = "Failed to sign in"
            logger.error(message)
            raise SigninFailedError(message)

    def signout_HumanSys(self) -> None:

        self.goto_HumanSys()
        self.page.fill('#AttendWork', '誤按')

        self.page.click('#signout')

        try:
            # https://cis.ncu.edu.tw/HumanSys/student/stdSignIn/create?ParttimeUsuallyId=247891&msg=signout_ok
            self.page.wait_for_url("https://cis.ncu.edu.tw/HumanSys/student/stdSignIn/create?ParttimeUsuallyId=247891&msg=signout_ok")
        except playwright._impl._errors.Error as e:
            # if the page doesn't redirect, check the error message
            message = "Failed to sign out"
            logger.error(message)
            raise SignoutFailedError(message)
  

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <action>")
        sys.exit(1)
    if sys.argv[1] not in ["signin", "signout"]:
        print("Invalid action")
        sys.exit(1)
    with NCU(account, headless=False) as ncu:
        if sys.argv[1] == "signin":
            ncu.is_login()            
            ncu.signin_HumanSys()
        elif sys.argv[1] == "signout":
            ncu.is_login()
            ncu.signout_HumanSys()
