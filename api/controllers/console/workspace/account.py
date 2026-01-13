from flask_restx import Resource, marshal_with

from controllers.console import console_ns
from controllers.console.wraps import setup_required
from fields.member_fields import account_fields
from libs.login import login_required, current_account


@console_ns.route("/account/profile")
class AccountProfile(Resource):

    @setup_required
    @login_required
    @marshal_with(account_fields)
    def get(self):
        current_user = current_account()
        return current_user