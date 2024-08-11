import sys
import playwright
import logging
from config import *
from type import *
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)


class NotLoginError(Exception):
    pass


class AlreadyLoginError(Exception):
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

    def __enter__(self) -> "NCU":
        """Start the browser when exit the context manager.

        Returns:
            self: NCU object
        """
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=self.headless)
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

    def login(self) -> None:
        """Login to the website.

        Raises:
            AlreadyLoginError: If the user is already logged in.
            LoginFailedError: If the login failed.
        """
        logger.debug("login")
        # if self.is_login():
        #     raise AlreadyLoginError()
        self.page.goto("https://portal.ncu.edu.tw/login")

        self.page.click('button[type="submit"]')
        logger.debug("submit login form")
    
        try:
            # redirect to the home page after login successfully
            self.page.wait_for_url("https://portal.ncu.edu.tw/", timeout=10000)
        except playwright._impl._errors.Error as e:
            # if the page doesn't redirect, check the error message
            message = self.get_login_failed_message()
            logger.error(message)
            raise LoginFailedError(message)
        
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

        logger.debug("goto HumanSys")
        # if self.is_login():
        #     raise AlreadyLoginError()
        self.goto_HumanSys()
        self.page.click('#signin')

        try:
            # redirect to the home page after login successfully
            # TODO wait url
            self.page.wait_for_url("https://portal.ncu.edu.tw/", timeout=10000)
        except playwright._impl._errors.Error as e:
            # if the page doesn't redirect, check the error message
            message = "Failed to sign in"
            logger.error(message)
            raise SigninFailedError(message)

    def signout_HumanSys(self) -> None:

        logger.debug("goto HumanSys")
        # if self.is_login():
        #     raise AlreadyLoginError()
        self.goto_HumanSys()
        self.page.fill('#AttendWork', '維護網站')

        self.page.click('#signout')

        try:
            # redirect to the home page after login successfully
            # TODO wait url https://cis.ncu.edu.tw/HumanSys/student/stdSignIn/create?ParttimeUsuallyId=247891&msg=signin_ok
            # https://cis.ncu.edu.tw/HumanSys/student/stdSignIn/create?ParttimeUsuallyId=247891&msg=signout_ok
            self.page.wait_for_url("https://portal.ncu.edu.tw/", timeout=10000)
        except playwright._impl._errors.Error as e:
            # if the page doesn't redirect, check the error message
            message = "Failed to sign in"
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
            ncu.login()
            ncu.signin_HumanSys()
        elif sys.argv[1] == "signout":
            ncu.login()
            ncu.signout_HumanSys()
