import os
import logging
from dotenv import load_dotenv
from type import *
import pyotp

load_dotenv()

account: Account = {
    "username": os.getenv("__PORTAL_USERNAME"),
    "password": os.getenv("__PORTAL_PASSWORD"),
    "totp": pyotp.parse_uri(os.getenv("__PORTAL_TOTP_SECRET"))
}

DC_WEBHOOK = os.getenv("__DC_WEBHOOK")

DEFAULT_HEADLESS = True
DEFAULT_COOKIES = [{"name": "portal", "value": "20241112173923zkgMuM3MmQin20230220154343n5AISRqIfeTD_LVKf_hp4_Er5K.GUbTrVdlXhvGpywgPnqR_nk.bfz", "domain": "portal.ncu.edu.tw",
                    "path": "/", "expires": 10000000000, "httpOnly": False, "secure": False}]
DELAY = 0
