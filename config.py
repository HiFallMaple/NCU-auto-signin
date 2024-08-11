import os
import logging
from dotenv import load_dotenv
from type import *

load_dotenv()

account:Account = {
    "username": os.getenv("__PORTAL_USERNAME"),
    "password": os.getenv("__PORTAL_PASSWORD")
}
    
DEFAULT_HEADLESS = True
DEFAULT_COOKIES = [{"name": "portal", "value": "20240713105518zkgMuM3MmQin20230220154343n5AISRqIfeTD_LVKf_hp4_Er5K.GUbTrVdlXhvGpywgPnqR_nk.bfz", "domain": "portal.ncu.edu.tw",
                    "path": "/", "expires": 10000000000, "httpOnly": False, "secure": False}]
DELAY = 0

print(account["username"])
print(account["password"])