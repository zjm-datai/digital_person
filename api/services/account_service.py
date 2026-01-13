import base64
import logging
import secrets
from datetime import datetime, timedelta

from pydantic import BaseModel
from pytz import UTC

from configs import app_config
from constants.languages import language_timezone_mapping, get_valid_language
from extensions.ext_redis import redis_client
from libs.datetime_utils import naive_utc_now
from libs.passport import PassportService
from libs.password import hash_password, compare_password, valid_password
from libs.token import generate_csrf_token
from models import Account
from extensions.ext_database import db
from models.model import AppSetup
from services.errors.account import AccountPasswordError

logger = logging.getLogger(__name__)

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    csrf_token: str

REFRESH_TOKEN_PREFIX = "refresh_token:"
ACCOUNT_REFRESH_TOKEN_PREFIX = "account_refresh_token:"
REFRESH_TOKEN_EXPIRY = timedelta(days=app_config.REFRESH_TOKEN_EXPIRE_DAYS)

class AccountService:

    @staticmethod
    def _get_refresh_token_key(refresh_token: str) -> str:
        return f"{REFRESH_TOKEN_PREFIX}{refresh_token}"

    @staticmethod
    def _get_account_refresh_token_key(account_id: str) -> str:
        return f"{ACCOUNT_REFRESH_TOKEN_PREFIX}{account_id}"

    @staticmethod
    def _store_refresh_token(refresh_token: str, account_id: str):
        redis_client.setex(AccountService._get_refresh_token_key(refresh_token), REFRESH_TOKEN_EXPIRY, account_id)
        redis_client.setex(
            AccountService._get_account_refresh_token_key(account_id), REFRESH_TOKEN_EXPIRY, refresh_token
        )

    @staticmethod
    def _delete_refresh_token(refresh_token: str, account_id: str):
        redis_client.delete(AccountService._get_refresh_token_key(refresh_token))
        redis_client.delete(AccountService._get_account_refresh_token_key(account_id))


    @staticmethod
    def load_user(user_id: str) -> None | Account:
        account = db.session.query(Account).filter(Account.id == user_id).first()
        if not account:
            return None

        return account

    @staticmethod
    def get_account_jwt_token(account: Account) -> str:
        exp_dt = datetime.now(UTC) + timedelta(hours=app_config.ACCESS_TOKEN_EXPIRE_MINUTES)
        exp = int(exp_dt.timestamp())
        payload = {
            "user_id": account.id,
            "exp": exp,
            "iss": app_config.EDITION,
            "sub": "Console API Passport",
        }

        token: str = PassportService().issue(payload)
        return token

    @staticmethod
    def authenticate(email: str, password: str) -> Account:
        """authenticate account with email and password"""

        account = db.session.query(Account).filter_by(email=email).first()
        if not account:
            raise AccountPasswordError("Invalid email or password.")

        if password and account.password is None:
            # if invite_token is valid, set password and password_salt
            salt = secrets.token_bytes(16)
            base64_salt = base64.b64encode(salt).decode()
            password_hashed = hash_password(password, salt)
            base64_password_hashed = base64.b64encode(password_hashed).decode()
            account.password = base64_password_hashed
            account.password_salt = base64_salt

        if account.password is None or not compare_password(password, account.password, account.password_salt):
            raise AccountPasswordError("Invalid email or password.")

        db.session.commit()

        return account

    @staticmethod
    def update_login_info(account: Account, *, ip_address: str):
        account.last_login_at = naive_utc_now()
        account.last_login_ip = ip_address
        db.session.add(account)
        db.session.commit()

    @staticmethod
    def login(account: Account, *, ip_address: str | None = None) -> TokenPair:
        if ip_address:
            AccountService.update_login_info(account=account, ip_address=ip_address)

        access_token = AccountService.get_account_jwt_token(account=account)
        refresh_token = _generate_refresh_token()
        csrf_token = generate_csrf_token(account.id)

        AccountService._store_refresh_token(refresh_token, account.id)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            csrf_token=csrf_token,
        )

    @staticmethod
    def create_account(
            email: str,
            name: str,
            interface_language: str,
            password: str | None = None,
            is_setup: bool | None = False
    ) -> Account:

        password_to_set = None
        salt_to_set = None

        if password:
            valid_password(password)

            salt = secrets.token_bytes(16)
            base64_salt = base64.b64encode(salt).decode()

            password_hashed = hash_password(password, salt)
            base64_password_hashed = base64.b64encode(password_hashed).decode()

            password_to_set = base64_password_hashed
            salt_to_set = base64_salt

        account = Account(
            name=name,
            email=email,
            password=password_to_set,
            password_salt=salt_to_set,
            interface_language=interface_language,
            timezone=language_timezone_mapping.get(interface_language, "UTC"),
        )

        db.session.add(account)
        db.session.commit()
        return account


    @staticmethod
    def load_logged_in_account(*, account_id: str):
        return AccountService.load_user(account_id)

    @staticmethod
    def refresh_token(refresh_token: str) -> TokenPair:
        account_id = redis_client.get(AccountService._get_refresh_token_key(refresh_token))
        if not account_id:
            raise ValueError("Invalid refresh token")

        account = AccountService.load_user(account_id.decode("utf-8"))
        if not account:
            raise ValueError("Invalid account")

        # Generate new access token and refresh token
        new_access_token = AccountService.get_account_jwt_token(account)
        new_refresh_token = _generate_refresh_token()

        AccountService._delete_refresh_token(refresh_token, account.id)
        AccountService._store_refresh_token(new_refresh_token, account.id)
        csrf_token = generate_csrf_token(account.id)

        return TokenPair(access_token=new_access_token, refresh_token=new_refresh_token, csrf_token=csrf_token)

def _generate_refresh_token(length: int = 64):
    token = secrets.token_hex(length)
    return token

class RegisterService:

    @classmethod
    def setup(cls, email: str, name: str, password: str, ip_address: str, language: str | None):

        try:
            account = AccountService.create_account(
                email=email,
                name=name,
                interface_language=get_valid_language(language),
                password=password,
                is_setup=True,
            )

            account.last_login_ip = ip_address
            account.initialized_at = naive_utc_now()

            app_setup = AppSetup(version=app_config.project.version)
            db.session.add(app_setup)
            db.session.commit()
        except Exception as e:
            db.session.query(AppSetup).delete()
            db.session.query(Account).delete()

            db.session.rollback()

            logger.exception("Setup account failed, email: %s, name: %s", email, name)
            raise ValueError(f"Setup failed: {e}")
