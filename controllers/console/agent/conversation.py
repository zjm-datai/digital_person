from flask_restful import reqparse, Resource

from controllers.console import console_ns
from models.conversation import Conversation
from models.engine import db

conversation_parser = reqparse.RequestParser()
conversation_parser.add_argument()

@console_ns("/agent/doctor_agent/conversation")
class ConversationResource(Resource):

    def get(self):
        """Create a new conversation."""

        new_conversation = ConversationService.create_conversation()

        return {
            "id": new_conversation.id,
            "created_at": new_conversation.created_at.isoformat(),
            "updated_at": new_conversation.updated_at.isoformat()
        }, 201
