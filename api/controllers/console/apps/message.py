
import logging
from typing import Optional, List

from flask import request
from flask_restx import fields
from pydantic import BaseModel, Field
from flask_restx.resource import Resource
from werkzeug.exceptions import InternalServerError, NotFound
import sqlalchemy as sa

from libs.login import login_required
from models import Conversation, Message
from services.message_service import MessageService
from extensions.ext_database import db
from controllers.console import console_ns

logger = logging.getLogger(__name__)
DEFAULT_REF_TEMPLATE_SWAGGER_2_0 = "#/definitions/{model}"

class ChatMessageQuery(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    app_type: Optional[str] = Field(None, description="App Type")

chat_message_out_fields = console_ns.model("ChatMessageOut", {
    "id": fields.String,
    "role": fields.String,
    "content": fields.String(required=False),
    "thinking": fields.String(required=False),
    "summary": fields.String(required=False),
    "suggestions": fields.List(fields.String),
})

def reg(cls: type[BaseModel]):
    console_ns.schema_model(cls.__name__, cls.model_json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0))

reg(ChatMessageQuery)

def parse_suggestions(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [s.strip() for s in raw.split("|") if s.strip()]

@console_ns.route("/apps/chat-messages")
class ChatMessageListApi(Resource):

    @console_ns.doc("list_chat_messages")
    @console_ns.doc(description="List chat messages")
    @console_ns.expect(console_ns.models[ChatMessageQuery.__name__])
    @console_ns.marshal_list_with(chat_message_out_fields)
    @console_ns.response(400, "Missing conversation id")
    @console_ns.response(404, "Conversation not found")
    @console_ns.response(404, "Conversation not found")
    @login_required
    def get(self):
        args = ChatMessageQuery.model_validate(request.args.to_dict(flat=True)) # type: ignore

        conversation = (
            db.session.query(Conversation)
            .where(Conversation.id == args.conversation_id)
            .first()
        )

        if not conversation:
            raise NotFound("Conversation Not Exists.")

        q = (
            db.session.query(Message)
            .where(Message.conversation_id == args.conversation_id)
            .order_by(
                sa.asc(Message.created_at),
            )
        )
        rows: List[Message] = q.all()

        out: List[dict] = []
        for m in rows:
            if m.message_kind == "summary":
                out.append({
                    "id": m.id,
                    "role": m.role,
                    "content": None,
                    "thinking": None,
                    "summary": m.content or "",
                    "suggestions": parse_suggestions(getattr(m, "suggested_answers", None)),
                })
            else:
                out.append({
                    "id": m.id,
                    "role": m.role,
                    "content": m.content or "",
                    "thinking": None,
                    "summary": None,
                    "suggestions": parse_suggestions(getattr(m, "suggested_answers", None)),
                })

        return out, 200

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