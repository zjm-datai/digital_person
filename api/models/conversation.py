
from datetime import datetime
from enum import StrEnum
from uuid import uuid4

import sqlalchemy as sa

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .types import StringUUID

class MessageRole(StrEnum):

    ASSISTANT = "assistant"
    USER = "user"

class Conversation(Base):
    __tablename__ = "conversations"
    
    __table_args__ = (
        sa.PrimaryKeyConstraint("id", name="conversation_pkey"),
    )

    id: Mapped[str] = mapped_column(
        StringUUID, default=lambda: str(uuid4())
    )

    opc_id: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    app_type: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.current_timestamp(), server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.current_timestamp(),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class Message(Base):
    __tablename__ = "messages"
    
    __table_args__ = (
        sa.PrimaryKeyConstraint("id", name="message_pkey"),
    )

    id: Mapped[str] = mapped_column(
        StringUUID, default=lambda: str(uuid4())
    )

    conversation_id: Mapped[str] = mapped_column(StringUUID, nullable=False)
    app_type: Mapped[str] = mapped_column(String(255), nullable=False)

    current_stage: Mapped[str] = mapped_column(
        String(255), nullable=True,
        comment="只有 role 为 assistant 的时候存在该字段，代表提问时所处的问诊阶段"
    )
    current_field: Mapped[str] = mapped_column(
        String(255), nullable=True,
        comment = "只有 role 为 assistant 的时候存在该字段，代表提问时所提问的问诊字段"
    )
    message_kind: Mapped[str] = mapped_column(
        String(255), nullable=True,
    )

    role: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.current_timestamp(), server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    