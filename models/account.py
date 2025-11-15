
import enum

from datetime import datetime
from dataclasses import field

import sqlalchemy as sa
from sqlalchemy import DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column


from flask_login import UserMixin

from models.base import TypeBase

from .types import StringUUID

class TenantAccountRole(enum.StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    NORMAL = "normal"
    DATASET_OPERATOR = "dataset_operator"

class Account(UserMixin, TypeBase):

    __tablename__ = 'accounts'
    __table_args__ = (
        sa.PrimaryKeyConstraint("id", name="account_pkey"), 
        sa.Index("account_email_idx", "email")
    )

    id: Mapped[str] = mapped_column(
        StringUUID, 
        server_default=sa.text("uuid_generate_v4()"), 
        init=False
    )
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    password: Mapped[str | None] = mapped_column(
        String(255), 
        default=None
    )
    password_salt: Mapped[str | None] = mapped_column(String(255), default=None)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    interface_language: Mapped[str | None] = mapped_column(String(255), default=None)
    interface_theme: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    timezone: Mapped[str | None] = mapped_column(String(255), default=None)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
    last_login_ip: Mapped[str | None] = mapped_column(
        String(255), 
        nullable=True, 
        default=None
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False, init=False
    )
    status: Mapped[str] = mapped_column(
        String(16), server_default=sa.text("'active'::character varying"), default="active"
    )
    initialized_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False, init=False, onupdate=func.current_timestamp()
    )

    role: TenantAccountRole | None = field(default=None, init=False)
    _current_tenant: "Tenant | None" = field(default=None, init=False)


class Tenant(TypeBase):
    __tablename__ = "tenants"
    __table_args__ = (sa.PrimaryKeyConstraint("id", name="tenant_pkey"),)

