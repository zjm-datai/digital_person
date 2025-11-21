


from ipaddress import ip_address
from flask import request
from flask_restx import Resource, reqparse
from controllers.console import console_ns
from controllers.console.wraps import setup_required

from libs.helper import email

@console_ns.route("/login")
class LoginApi(Resource):
    """Resource for user login."""

    @setup_required
    def post(self):
        """Authenticate user and login."""

        parser = reqparse.RequestParser()
        parser.add_argument("email", type=email, required=True, location="json")
        parser.add_argument("password", type=str, required=True, location="json")
        parser.add_argument("remember_me", type=bool, required=False, default=False)

        args = parser.parse_args()

        try:

            account = AccountService.authenticate(
                args["email"], args["password"]
            )
        except services.errors.account.AccountLoginError:
            raise AccountBannedError()
        except services.errors.account.AccountPasswordError:
            raise AuthenticationFailedError()
        
        token_pair = AccountService.login(account=account, ip_address=extract_remote_ip(request))

        return {
            "result": "success",
            "data": token_pair.model_dump()
        }