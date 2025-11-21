

import uuid
from typing import Any
from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.type_api import TypeEngine

# 定义一个自定义类型装饰器，用于处理UUID与字符串之间的转换，支持 uuid.UUID、str 和 None 类型
class StringUUID(TypeDecorator[uuid.UUID | str | None]):

    # 指定基础数据类型为 CHAR 字符类型
    impl = CHAR
    # 标记该类型可以安全地被缓存，提高性能
    cache_ok = True

    # 处理绑定参数的方法，将 python 端的值转换为数据库可以接收的格式
    # 在执行 INSERT、UPDATE 时调用
    def process_bind_param(
        self, value: uuid.UUID | str | None, dialect: Dialect
    ):
        if value is None:
            return None
        elif dialect.name == "postgresql":
            # 直接将值转换为字符串（PostgreSQL的UUID类型可直接接受字符串形式）
            return str(value)
        # 其他数据库（如 MySQL、SQLite 等）
        else:
            # 如果值是 UUID 对象，转换为十六进制字符串（32 位无横线格式）
            if isinstance(value, uuid.UUID):
                return value.hex
            # 如果是字符串，直接返回（假设已符合格式要求）
            return value

    # 根据数据库方言加载对应的具体类型实现
    # 定义模型表结构或创建表时调用
    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        # 如果是 PostgreSQL，使用其原生的 UUID 类型
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        # 其他数据库使用 36 位字符类型（UUID 标准格式带横线）
        else:
            return dialect.type_descriptor(CHAR(36))

    # 处理查询结果的方法：将数据库返回的值转换为 Python 端可用的格式
    # SELECT 时调用
    def process_result_value(self, value: uuid.UUID | str | None, dialect: Dialect) -> str | None:
        # 如果值为 None，直接返回 None
        if value is None:
            return value
        # 无论数据库返回的是UUID对象还是字符串，统一转换为字符串返回
        return str(value)