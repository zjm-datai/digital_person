from models import Account
from extensions.ext_database import db

class AccountService:

    @staticmethod
    def load_user(user_id: str) -> None | Account:
        account = db.session.query(Account).filter(Account.id == user_id).first()
        if not account:
            return None

        return account

    @staticmethod
    def load_logged_in_account(*, account_id: str):
        return AccountService.load_user(account_id)