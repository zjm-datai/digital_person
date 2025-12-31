

import logging

from flask import g
from flask_restx import Resource, fields, reqparse
from werkzeug.exceptions import InternalServerError

from controllers.console import console_ns, api

from services.app_generate_service import AppGenerateService
from services.message_service import MessageService
from services.conversation_service import ConversationService

from libs import helper

logger = logging.getLogger(__name__)


@console_ns.route("/apps/<string:app_type>/completion-messages")
class CompletionMessageApi(Resource):

    @console_ns.doc("预问诊对话接口")
    @console_ns.doc(description="")
    @console_ns.doc(params={"app_type": "应用类型"})
    @console_ns.expect(
        api.model(
            "ChatRequest",
            {   
                "conversation_id": fields.String(required=False, description="会话 id"),
                "opc_id": fields.String(required=True, description="就诊号"),
                "message": fields.String(required=True, description="用户输入的消息内容"),
                "response_mode": fields.String(enum=["blocking", "streaming"], description="响应模式"),
            }
        )
    )
    @console_ns.response(200, "Chat successfully")
    @console_ns.response(400, "Invalid request parameters")
    @console_ns.response(404, "Application type not found")
    def post(self, app_type: str):
        parser = (
            reqparse.RequestParser()
            .add_argument("opc_id", type=str, required=True, help="就诊号", location="json")
            .add_argument("conversation_id", type=str, required=False, location="json")
            .add_argument("message", type=str, required=True, help="用户输入的消息内容", location="json")
            .add_argument("response_mode", type=str, choices=("blocking", "streaming"), location="json")
        )
        args = parser.parse_args()

        opc_id = args["opc_id"]
        conversation_id = args["conversation_id"]
        message = args["message"]
        streaming = args["response_mode"] != "blocking"
        
        try:
            conversation_id = ConversationService.get_or_create(
                opc_id=opc_id, app_type=app_type, conversation_id=conversation_id,
            )
            message_id = MessageService.create_message(
                conversation_id=conversation_id, message=message
            )

            g.llm_run_context = {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "opc_id": opc_id,
                "hospital_guid": "...",
                "hospital_name": "...",
            }
            
            response = AppGenerateService.generate(
                app_type, conversation_id, message, streaming
            )
            
            return helper.compact_generate_response(response)
        except Exception as e:
            logger.exception("internal server error.")
            raise InternalServerError()
        