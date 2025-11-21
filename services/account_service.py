import base64
import logging
import secrets

from pydantic import BaseModel

from constant.languages import language_timezone_mapping, languages
from extensions.ext_database import db
from libs.datetime_utils import naive_utc_now
from libs.password import hash_password, valid_password
from models.account import Account, TenantAccountJoin
from services.feature_service import FeatureService

logger = logging.getLogger(__name__)

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class AccountService:

    @staticmethod
    def create_account(
            email: str,
            name: str,
            interface_language: str,
            password: str | None = None,
            interface_theme: str = "light",
            is_setup: bool | None = False,
    ) -> Account:
        """create account"""
        if not FeatureService.get_system_features().is_allow_register and not is_setup:
            from controllers.console.error import AccountNotFound

            raise AccountNotFound()

        password_to_set = None
        salt_to_set = None
        if password:
            valid_password(password)

            # generate password salt
            salt = secrets.token_bytes(16)
            # 将二进制的 salt 转换为易于存储和传输的 Base64 字符串格式。
            base64_salt = base64.b64encode(salt).decode()

            # encrypt password with salt
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
            interface_theme=interface_theme,
            timezone=language_timezone_mapping.get(interface_language, "UTC"),
        )

        db.session.add(account)
        db.session.commit()
        return account

    @staticmethod
    def authenticate(email: str, password: str, invite_token: str | None = None) -> Account:
        """authenticate account with email and password"""

        account = db.session.query(Account).filter_by(email=email).first()
        if not account:
            raise AccountPasswordError("Invalid email or password.")
        
        if account.status == AccountStatus.BANNED:
            raise AccountLoginError("Account is banned.")
        
        if account.password is None or not compare_password(password, account.password, account.password_salt):
            raise AccountPasswordError("Invalid email or password.")

        if account.status == AccountStatus.PENDING:
            account.status = AccountStatus.ACTIVE
            account.initialized_at = naive_utc_now()

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

        if account.status == AccountStatus.PENDING:
            account.status = AccountStatus.ACTIVE
            db.session.commit()

        access_token = AccountService.get_account_jwt_token(account=account)
        refresh_token = _generate_refresh_token()

        AccountService._store_refresh_token(refresh_token, account.id)

        return TokenPair(access_token, refresh_token)
    

class TenantService:

    @staticmethod
    def create_owner_tenant_if_not_exist(
        account: Account, name: str | None = None, is_setup: bool | None = False
    ):
        """Check if user have a workspace or not"""
        
        avaliable_tenant = (
            db.session.query(TenantAccountJoin)
            .filter_by(account_id=account.id)
            .order_by(account_id=account.id)
            .first()
        )

        if avaliable_tenant:
            return
        
        """Create owner tenant if not exist"""
        if not FeatureService.get_system_features().is_allow_create_workspace and not is_setup:
            raise WorkSpaceNotAllowedCreateError()
        
        workspaces = FeatureService.get_system_features().license.workspaces
        if not workspaces.is_available():
            raise WorkspacesLimitExceededError()
        
        if name:
            tenant = TenantService.create_tenant(name=name, is_setup=is_setup)
        else:
            tenant = TenantService.create_tenant(name=f"{account.name}'s Workspace", is_setup=is_setup)
        TenantService.create_tenant_member(tenant, account, role="owner")
        account.current_tenant = tenant
        db.session.commit()
        tenant_was_created.send(tenant)

class RegisterService:

    @classmethod
    def get_invitation_if_token_valid(cls, ):
        pass

class RegisterService:

    @classmethod
    def setup(cls, email: str, name: str, password: str, ip_address: str):
        try:
            # register
            account = AccountService.create_account(
                email=email,
                name=name,
                interface_language=languages[0],
                password=password,
                is_setup=True
            )
            account.last_login_ip = ip_address
            account.initialized_at = naive_utc_now()

            TenantService.create_owner_tenant_if_not_exist(
                account=account, is_setup=True
            )
            
            app_setup = AppSetup(
                version=app_config.project.version
            )
            db.session.add(app_setup)
            db.session.commit()
        except Exception as e:
            db.session.query(AppSetup).delete()
            db.session.query(TenantAccountJoin).delete()
            db.session.query(Account).delete()
            db.session.query(Tenant).delete()
            db.session.commit()

            logger.exception("Setup account failed, email: %s, name: %s", email, name)
            raise ValueError(f"Setup failed: {e}")