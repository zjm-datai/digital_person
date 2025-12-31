
import logging


from extensions.ext_database import db
from models.conversation import Message

logger = logging.getLogger(__name__)


class MessageService:
    
    @staticmethod
    def create_message(
        conversation_id: str, message: str, 
    ) -> str:
        try:

            new_message = Message(
                conversation_id=conversation_id,
                content=message
            )
            db.session.add(new_message)
            db.session.commit()
            logger.info(f"Message created with ID: {new_message.id}")
            return new_message.id
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create message: {e}")
            raise
        
    @staticmethod
    def get_suggested_answers_after_question(
        app_type: str, message_id: str
    ):
        # TODO
        pass