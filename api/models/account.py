
from datetime import datetime
from flask_login import UserMixin

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.sql.sqltypes import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


from models.types import StringUUID

from .base import Base


class Account(UserMixin, Base):
    __tablename__ = "accounts"
    
    __table_args__ = (
        sa.PrimaryKeyConstraint("id", name="account_pkey"),
    )
    
    id: Mapped[str] = mapped_column(
        StringUUID, server_default=sa.text("uuid_generate_v4()")
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    password: Mapped[str | None] = mapped_column(String(255), default=None)
    password_salt: Mapped[str | None] = mapped_column(String(255), default=None)

    interface_language: Mapped[str | None] = mapped_column(String(255), default=None)
    timezone: Mapped[str | None] = mapped_column(String(255), default=None)

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
    last_login_ip: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    initialized_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), 
        nullable=False, onupdate=func.current_timestamp()
    )