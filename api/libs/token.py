from datetime import timedelta, datetime

from flask import Response
from flask.wrappers import Request
from pytz import UTC

from configs import app_config
from constants import (
    COOKIE_NAME_ACCESS_TOKEN,
    COOKIE_NAME_CSRF_TOKEN,
    COOKIE_NAME_REFRESH_TOKEN,
)
from libs.passport import PassportService


def is_secure() -> bool:
    return app_config.CONSOLE_WEB_URL.startswith("https") and app_config.CONSOLE_API_URL.startswith("https")

def _cookie_domain() -> str | None:
    """
    Returns the normalized cookie domain.

    Leading dots are stripped from the configured domain. Historically, a leading dot
    indicated that a cookie should be sent to all subdomains, but modern browsers treat
    'example.com' and '.example.com' identically. This normalization ensures consistent
    behavior and avoids confusion.
    """
    domain = app_config.COOKIE_DOMAIN.strip()
    domain = domain.removeprefix(".")
    return domain or None

def _real_cookie_name(cookie_name: str) -> str:
    if is_secure() and _cookie_domain() is None:
        return "__Host-" + cookie_name
    else:
        return cookie_name

def _try_extract_from_header(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization")
    if auth_header:
        if " " not in auth_header:
            return None
        else:
            auth_scheme, auth_token = auth_header.split(None, 1)
            auth_scheme = auth_scheme.lower()
            if auth_scheme != "bearer":
                return None
            else:
                return auth_token
    return None

def extract_access_token(request: Request) -> str | None:

    def _try_extract_from_cookie(request: Request) -> str | None:
        return request.cookies.get(_real_cookie_name(COOKIE_NAME_ACCESS_TOKEN))

    return _try_extract_from_cookie(request) or _try_extract_from_header(request)

def extract_refresh_token(request: Request) -> str | None:
    return request.cookies.get(_real_cookie_name(COOKIE_NAME_REFRESH_TOKEN))

def extract_csrf_token(request: Request) -> str | None:
    return request.cookies.get(_real_cookie_name(COOKIE_NAME_CSRF_TOKEN))

def set_access_token_to_cookie(request: Request, response: Response, token: str, samesite: str = "Lax"):
    response.set_cookie(
        _real_cookie_name(COOKIE_NAME_ACCESS_TOKEN),
        value=token,
        httponly=True,
        domain=_cookie_domain(),
        secure=is_secure(),
        samesite=samesite,
        max_age=int(app_config.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        path="/",
    )

def set_refresh_token_to_cookie(request: Request, response: Response, token: str):
    response.set_cookie(
        _real_cookie_name(COOKIE_NAME_REFRESH_TOKEN),
        value=token,
        httponly=True,
        domain=_cookie_domain(),
        secure=is_secure(),
        samesite="Lax",
        max_age=int(60 * 60 * 24 * app_config.REFRESH_TOKEN_EXPIRE_DAYS),
        path="/",
    )


def set_csrf_token_to_cookie(request: Request, response: Response, token: str):
    response.set_cookie(
        _real_cookie_name(COOKIE_NAME_CSRF_TOKEN),
        value=token,
        httponly=False,
        domain=_cookie_domain(),
        secure=is_secure(),
        samesite="Lax",
        max_age=int(60 * app_config.ACCESS_TOKEN_EXPIRE_MINUTES),
        path="/",
    )

def generate_csrf_token(user_id: str) -> str:
    exp_dt = datetime.now(UTC) + timedelta(minutes=app_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "exp": int(exp_dt.timestamp()),
        "sub": user_id,
    }

    return PassportService().issue(payload)