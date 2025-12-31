import json

import flask_login
from flask import request, Response, Flask
from flask_login import user_logged_in, user_loaded_from_request
from werkzeug.exceptions import Unauthorized

from extensions.ext_database import db
from libs.passport import PassportService
from libs.token import extract_access_token

from configs import app_config
from models import Account

login_manager = flask_login.LoginManager()

@login_manager.request_loader
def load_user_from_request(request_from_flask_login):
    
    if app_config.SWAGGER_UI_ENABLED and request.path.endswith((app_config.SWAGGER_UI_PATH, "/swagger.json")):
        return None
    
    auth_token = extract_access_token(request)

    if app_config.ADMIN_API_KEY and auth_token:
        admin_api_key = app_config.ADMIN_API_KEY
        if admin_api_key and admin_api_key == auth_token:
            account = db.session.query(Account).first()

            return account
    
    if request.blueprint in {"console", "inner_api"}:
        if not auth_token:
            raise Unauthorized("Invalid Authorization token.")
        decoded = PassportService().verify(auth_token)
        user_id = decoded.get("user_id")
        source = decoded.get("token_source")

        if source:
            raise Unauthorized("Invalid Authorization token.")
        if not user_id:
            raise Unauthorized("Invalid Authorization token.")

        logged_in_account = AccountService.load_logged_in_account(account_id=user_id)

        return logged_in_account

@user_logged_in.connect
@user_loaded_from_request.connect
def on_user_logged_in(_sender, user):
    """
    Called when a user logs in.
    :param _sender:
    :param user:
    :return:
    """
    pass

@login_manager.unauthorized_handler
def unauthorized_handler():
    """Handle unauthorized requests."""

    return Response(
        json.dumps({"code": "unauthorized", "message": "Unauthorized."}),
        status=401,
        content_type="application/json",
    )

def init_app(app: Flask):
    login_manager.init_app(app)