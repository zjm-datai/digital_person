

from flask_restx import Resource, reqparse

from configs import app_config
from controllers.console.error import AlreadySetupError
from . import api, console_ns

@console_ns.route("/setup")
class SetupApi(Resource):

    @api.doc("get_setup_status")
    @api.doc(description="Get system setup status")
    @api.response(
        200,
        "Success",
        api.model(
            "SetupStatusResponse"
            {

            }
        )
    )
    def get(self):
        """Get system setup status"""
        if app_config.EDITION == "SELF_HOSTED":
            setup_status = get_setup_status()
            # check if setup_status is a AppSetup object rather than a bool
            if setup_status and not isinstance(setup_status, bool):
                return {
                    "step": "finished",
                    "setup_at": setup_status.setup_at.isoformat()
                }
            elif setup_status:
                return  {
                    "step": "finished"
                }
            return {
                "step": "not_started"
            }
        return {
            "step": "finished"
        }
    
    def post(self):
        """Initialize system setup with admin account"""

        # is set up
        if get_setup_status():
            raise AlreadySetupError()
        
        # is tenant created
        tenant_count = TenantService.get_tenant_count()
        if tenant_count > 0:
            raise AlreadySetupError()
        
        if not get_init_validate_status():
            raise NotInitValidateError()
        
        parser = reqparse.RequestParser()

        parser.add_argument("email", type=email, required=True, location="json")
        parser.add_argument("name", type=StrLen(30), required=True, location="json")
        parser.add_argument("password", type=valid_password, required=True, location="json")
        args = parser.parse_args()

        # setup
        RegisterService.setup(
            email=args["email"], name=args["name"], password=args["password"], ip_address=extract_remote_ip(request)
        )

        return {"result": "success"}, 201
