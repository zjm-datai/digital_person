

from libs.exception import BaseHTTPException

class AlreadySetupError(BaseHTTPException):
    error_code = "already_setup"
    description = "App has been successfully installed. Please refresh the page or return to the dashboard homepage."
    code = 403


class NotSetupError(BaseHTTPException):
    error_code = "not_setup"
    description = (
        "App has not been initialized and installed yet. "
        "Please proceed with the initialization and installation process first."
    )
    code = 401

class AccountNotFound(BaseHTTPException):
    error_code = "account_not_found"
    description = "Account not found."
    code = 400