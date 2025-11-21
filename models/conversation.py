import datetime
from typing import Optional


import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import TypeBase
from models.types import StringUUID


class Message(TypeBase):
    __tablename__ = "message"
    __table_args__ = (
        
    )

    id: Mapped[str] = mapped_column(StringUUID, server_default=sa.text("uuid_generate_v4()"))
    conversation_id: Mapped[str] = mapped_column(StringUUID, sa.ForeignKey("conversations.id"))
    parent_message_id: Mapped[str] = mapped_column(StringUUID, nullable=True)

    role: Mapped[str] = mapped_column(
        sa.String(length=32),
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        sa.Text,
        nullable=False,
        server_default="",
    )
    message_kind: Mapped[Optional[str]] = mapped_column(
        sa.String(length=32),
        nullable=True,
    )
    target_stage: Mapped[Optional[str]] = mapped_column(
        sa.String(length=32),
        nullable=True,
    )
    target_field: Mapped[Optional[str]] = mapped_column(
        sa.String(length=64),
        nullable=True,
    )

    suggested_answers: Mapped[Optional[str]] = mapped_column(
        sa.Text,
        nullable=True,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, server_default=func.current_timestamp())


class Conversation(TypeBase):
    __tablename__ = "conversation"
    __table_args__ = (

    )

    id: Mapped[str] = mapped_column(StringUUID, server_default=sa.text("uuid_generate_v4()"))

    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, nullable=False, server_default=func.current_timestamp())

