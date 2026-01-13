from flask import request, make_response
from flask_restx import Resource

from pydantic import BaseModel, EmailStr, Field

import services
from controllers.console import console_ns
from controllers.console.error import AuthenticationFailedError
from libs.token import extract_refresh_token, set_csrf_token_to_cookie, set_access_token_to_cookie, \
    set_refresh_token_to_cookie
from services.account_service import AccountService

DEFAULT_REF_TEMPLATE_SWAGGER_2_0 = "#/definitions/{model}"

class LoginPayload(BaseModel):
    email: EmailStr = Field(..., description='Email address')
    password: str = Field(..., description='Password')
    remember_me: bool = Field(False, description='Remember me')
    invite_token: str | None = Field(default=None, description='Invite token')

def reg(cls: type[BaseModel]):
    console_ns.schema_model(cls.__name__, cls.model_json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0))

reg(LoginPayload)

@console_ns.route("/login")
class LoginApi(Resource):
    """Resource for user login."""

    @console_ns.expect(console_ns.models[LoginPayload.__name__])
    def post(self):
        """Authenticate user and login."""

        args = LoginPayload.model_validate(console_ns.payload)

        try:
            account = AccountService.authenticate(str(args.email), args.password)
        except services.errors.account.AccountLoginError:
            raise AuthenticationFailedError()
        except services.errors.account.AccountPasswordError:
            raise AuthenticationFailedError()

        token_pair = AccountService.login(account=account)

        # Create response with cookies instead of returning tokens in body
        response = make_response({"result": "success"})

        set_access_token_to_cookie(request, response, token_pair.access_token)
        set_refresh_token_to_cookie(request, response, token_pair.refresh_token)
        set_csrf_token_to_cookie(request, response, token_pair.csrf_token)

        return response

@console_ns.route("/refresh-token")
class RefreshTokenApi(Resource):
    def post(self):

        refresh_token = extract_refresh_token(request)

        if not refresh_token:
            return {
                "result": "fail",
                "message": "No refresh token provided"
            }, 401

        try:
            new_token_pair = AccountService.refresh_token(refresh_token)

            # Create response with new cookies
            response = make_response({"result": "success"})

            # Update cookies with new tokens
            set_csrf_token_to_cookie(request, response, new_token_pair.csrf_token)
            set_access_token_to_cookie(request, response, new_token_pair.refresh_token)
            set_refresh_token_to_cookie(request, response, new_token_pair.refresh_token)

            return response
        except Exception as e:
            return {
                "result": "fail",
                "message": str(e)
            }, 401