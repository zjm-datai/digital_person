
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

    id: Mapped[str] = mapped_column(StringUUID, server_default=sa.text("uuid_generate_v4()"), init=False)
    name: Mapped[str] = mapped_column(String(255))
    encrypt_public_key: Mapped[str | None] = mapped_column(sa.Text, default=None)

    plan: Mapped[str] = mapped_column(
        String(255), server_default=sa.text("'basic'::character varying"), default="basic"
    )

    # 1. sa.text() 的作用是告诉 SQLAlchemy：
    # “这个内容是原生 SQL，不要改写，直接塞到建表语句里”

    # 2. 'basic'::character varying

    # 这是 PostgreSQL 特有的 类型转换语法：
    # 'basic' —— 字面量字符串
    # ::character varying —— 强制转成字符类型（varchar）
    # 这个语句在 PostgreSQL 中等价于：
    # DEFAULT 'basic'::varchar
    # 也可以这么写 sa.text("'basic'::varchar")
    
    # 在 PostgreSQL 中：
    # varchar
    # character varying
    # character varying(n)
    # varchar(n)
    # 本质上都是同一种类型。

    status: Mapped[str] = mapped_column(
        String(255), server_default=sa.text("'normal'::character varying"), default="normal"
    )
    custom_config: Mapped[str | None] = mapped_column(sa.Text, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), init=False)


class TenantAccountJoin(TypeBase):
    __tablename__ = "tenant_account_joins"
    __table_args__ = (
        sa.PrimaryKeyConstraint("id", name="tenant_account_join_pkey"),
        sa.Index("tenant_account_join_account_id_idx", "account_id"),
        sa.Index("tenant_account_join_tenant_id_idx", "tenant_id"),
        # 字段组合唯一约束
        sa.UniqueConstraint("tenant_id", "account_id", name="unique_tenant_account_join")
    )
    # CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    id: Mapped[str] = mapped_column(StringUUID, server_default=sa.text("uuid_generate_v4()"), init=False)
    tenant_id: Mapped[str] = mapped_column(StringUUID)
    account_id: Mapped[str] = mapped_column(StringUUID)
    current: Mapped[bool] = mapped_column(sa.Boolean, server_default=sa.text("false"), default=False)
    role: Mapped[str] = mapped_column(String(16), server_default="normal", default="normal")

    # default 由 python orm 来执行，在插入 sql 之前进行，orm 插入对象时候自动填充
    # server_default 由数据库执行，在 sql 执行的时候自动填充，数据库层面保证字段有默认值
    # nullable 是数据库层面的约束，允许数据库字段为 Null
    # init=False 的意思是：这个字段不会出现在 dataclass 自动生成的 __init__() 函数参数里，也就是不允许你手动初始化它
    
    # 为什么需要 init=False？
    # 这是企业级 SQLAlchemy dataclass ORM 的 最佳实践
    # 1. create_at 不能由业务代码来设置
    # 2. 使用 dataclass 时，所有字段都自动进入 init
    # 如果你使用 MappedAsDataclass，ORM 模型会自动变成 dataclass
    
    # @dataclass
    # class TenantAccountJoin:
    #   create_at: datetime

    # 不加 init=False 就会导致：
    
    # __init__(self, create_at: datetime)

    # 但这不合理，因为 create_at 应该由数据库生成。
    # 于是 init=False 可以告诉 dataclass：
    # 这个字段不要放进 init 方法中。

    # 3. 防止 ORM 在 flush 前赋空导致数据库报错

    # 如果你把字段放在 __init__ 范围里，但它是：

    # nullable=False
    # server_default=xxx

    # 但 ORM 会在 INSERT 前把它作为空字段写入
    # 你会得到错误：

    # IntegrityError: NOT NULL constraint failed

    # 用 init=False 可以让 ORM 不把它视为一个需要由应用初始化的字段，从而让数据库默认值生效。

    # 注意：

    # 1. init=True/False 发生在 Python 对象创建阶段
    # 2. default=... 发生在 ORM flush 到数据库之前
    # 这是一个完全不同的逻辑：
    # SQLAlchemy 会检查字段是否未赋值
    # 如果未赋值 → 执行 default
    # 这一切发生在 INSERT SQL 生成之前
    # 也就是说：
    # 👉 default 是 ORM 自动补值，不依赖你是否在 init 里设置值。

    # init=False 是 dataclass 的参数控制，不影响 ORM。
    # default 是 ORM 的字段默认值，由 ORM 在 flush 时执行。
    # default 永远会生效，只要你没有给字段手动赋值。
    # init=False 不会阻止 default 的执行，它只是阻止你传 init 参数。

    invited_by: Mapped[str | None] = mapped_column(StringUUID, nullable=True, default=None)
    create_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False, init=False
    )