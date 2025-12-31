from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from extensions.ext_database import db
from models.conversation import Conversation


class ConversationService:

    @staticmethod
    def create(opc_id: str, app_type: str):
        try:
            conversation = Conversation(
                opc_id=opc_id,
                app_type=app_type
            )
            db.session.add(conversation)
            db.session.commit()
            db.session.refresh(conversation)
            return conversation

        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_or_create(
        opc_id: str,
        app_type: str,
        conversation_id: Optional[str] = None
    ) -> str:
        try:
            if conversation_id:
                stmt = select(Conversation).where(
                    Conversation.id == conversation_id
                )
                conversation = db.session.execute(stmt).scalar_one_or_none()

                if conversation:
                    if (
                        conversation.opc_id != opc_id
                        or conversation.app_type != app_type
                    ):
                        conversation = Conversation(
                            opc_id=opc_id,
                            app_type=app_type
                        )
                        db.session.add(conversation)
                        db.session.commit()
                        db.session.refresh(conversation)
                else:
                    conversation = Conversation(
                        opc_id=opc_id,
                        app_type=app_type
                    )
                    db.session.add(conversation)
                    db.session.commit()
                    db.session.refresh(conversation)

                return str(conversation.id)

            else:
                conversation = Conversation(
                    opc_id=opc_id,
                    app_type=app_type
                )
                db.session.add(conversation)
                db.session.commit()
                db.session.refresh(conversation)
                return str(conversation.id)

        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
