from typing import Optional
from uuid import uuid4
from datetime import datetime

import sqlalchemy as sa

from sqlalchemy import BigInteger, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .types import StringUUID, LongText
from .base import Base


class LLMRunLog(Base):
    __tablename__ = "llm_run_logs"
    
    __table_args__ = (
        sa.PrimaryKeyConstraint("id", name="llm_run_log_pkey"),
    )

    id: Mapped[str] = mapped_column(
        StringUUID, default=lambda: str(uuid4())
    )

    trace_id: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="对应业务字段 opc_id"
    )
    conversation_id: Mapped[str] = mapped_column(
        StringUUID, nullable=False
    )
    message_id: Mapped[str] = mapped_column(
        StringUUID, nullable=False
    )
    inputs: Mapped[str] = mapped_column(
        LongText, nullable=False
    )
    outputs: Mapped[str] = mapped_column(
        LongText, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="运行状态 success / failed / running "
    )
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
    )
    elapsed_time: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="LLM 调用耗时（秒）"
    )

    hospital_guid: Mapped[str] = mapped_column(
        String(255), nullable=True
    )
    hospital_name: Mapped[str] = mapped_column(
        String(255), nullable=True
    )
    type: Mapped[str] = mapped_column(
        String(255), nullable=True
    )
    error: Mapped[str] = mapped_column(
        LongText, nullable=True
    )
    prompt_tokens: Mapped[int] = mapped_column(
        BigInteger, nullable=True
    )
    completion_tokens: Mapped[int] = mapped_column(
        BigInteger, nullable=True
    )
    total_tokens: Mapped[int] = mapped_column(
        BigInteger, nullable=True
    )