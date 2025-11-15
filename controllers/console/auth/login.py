


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

        parser = (
            reqparse.RequestParser()
            .add_argument("email", type=email, required=True, location="json")

        )
    