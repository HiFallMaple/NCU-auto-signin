from typing import TypedDict
import pyotp


class Cookie(TypedDict):
    name: str
    value: str
    domain: str
    path: str
    expires: int
    httpOnly: bool
    secure: bool
    sameSite: str
    
class Account(TypedDict):
    username: str
    password: str
    totp: pyotp.totp.TOTP