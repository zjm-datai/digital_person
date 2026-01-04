
import logging

from flask_restx import fields
from pydantic import BaseModel, Field
from flask_restx.resource import Resource
from werkzeug.exceptions import InternalServerError

from services.message_service import MessageService
from controllers.console import console_ns

logger = logging.getLogger(__name__)
DEFAULT_REF_TEMPLATE_SWAGGER_2_0 = "#/definitions/{model}"

class ChatMessageQuery(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")

def reg(cls: type[BaseModel]):
    console_ns.schema_model(cls.__name__, cls.model_json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0))

reg(ChatMessageQuery)

@console_ns.route("/apps/<string:app_type>/chat-messages")
class ChatMessageListApi(Resource):
    
    @console_ns.doc("list_chat_messages")
    @console_ns.expect(console_ns.models[ChatMessageQuery.__name__])
    def post(self, app_type: str):
        return {
            "data": ["sssss"]
        }

@console_ns.route("/apps/<string:app_type>/chat-messages/<uuid:message_id>/suggested-answers")
class MessageSuggestedAnswerApi(Resource):
    @console_ns.doc("get_message_suggested_answer")
    @console_ns.response(
        200,
        "Suggested answer generated successfully",
        console_ns.model(
            "SuggestedAnswersResponse", {
                "data": fields.List(fields.String(description="Suggested answers"))
            }
        )   
    )
    @console_ns.response(404, "Message or conversation not found")
    def get(self, app_type: str, message_id):
        message_id = str(message_id)
        
        try:
            answers = MessageService.get_suggested_answers_after_question(
                app_type=app_type, message_id=message_id
            )
        except Exception:
            logger.exception("internal server error.")
            raise InternalServerError()

        return {
            "data": answers
        }