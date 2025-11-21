
from flask_restx import Resource, fields, reqparse
from controllers.console import console_ns, api

active_parser = reqparse.RequestParser()
active_parser.add_argument("workspace_id", type=str, required=False, nullable=True)


@console_ns.route("/activate")
class ActivateApi(Resource):

    @api.doc("activate_account")
    @api.doc(description="Activate account with invitation token")
    @api.expect(active_parser)
    @api.response(
        200,
        "Account activated successfully",
        api.model(
            "ActivationResponse",
            {
                "result": fields.String(description="Operation result"),
                "data": fields.Raw(description="Login token data"),
            },
        ),
    )
    @api.response(400, "Already activated or invalid token")
    def post(self):
        args = active_parser.parse_args()

        invitation = RegisterService.get_invitation_if_token_valid(args["workspace_id"], args["email"], args["token"])
        if invitation is None:
            rasie AlreadyActivateError()

        RegisterService.revoke_token(
            args["workspace_id"], args["email"], args["token"]
        )

        account = invitation["account"]
        