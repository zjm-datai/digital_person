from libs.exception import BaseHTTPException

class AuthenticationFailedError(BaseHTTPException):
    error_code = "account_banned"
    description = "Account is banned."
    code = 400

class NotInitValidateError(BaseHTTPException):
    error_code = "not_init_validated"
    description = "Init validation has not been completed yet. Please proceed with the init validation process first."
    code = 401