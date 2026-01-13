

from flask_restx import fields, reqparse
from flask_restx.resource import Resource
from controllers.console import console_ns
from controllers.console.wraps import setup_required
from libs.login import login_required
from services.conversation_service import ConversationService

conversation_model = console_ns.model(
    "Conversation",
    {
        "id": fields.String,
        "opc_id": fields.String,
        "app_type": fields.String,
        "created_at": fields.DateTime,
    }
)

create_model = console_ns.model(
    "ConversationCreate",
    {
        "opc_id": fields.String(required=True),
    }
)

@console_ns.route("/apps/<string:app_type>/conversation")
class ConversationList(Resource):
    
    @console_ns.doc(
        summary="create conversation",
    )
    @console_ns.expect(create_model)
    @console_ns.marshal_with(conversation_model)
    @setup_required
    @login_required
    def post(self, app_type: str):
        parser = (
            reqparse.RequestParser()
            .add_argument("opc_id", type=str, required=True, location="json")
        )
        
        args = parser.parse_args()
        
        opc_id = args["opc_id"]
        
        return ConversationService.create(opc_id, app_type)


        