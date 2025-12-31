
import uuid

from typing import Any

from sqlalchemy import CHAR, TEXT, Dialect, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql.type_api import TypeEngine

class StringUUID(TypeDecorator[uuid.UUID | str | None]):
    impl = CHAR
    cache_ok = True
    
    # 返回值是要存在数据库的值
    def process_bind_param(
        self, value: uuid.UUID | str | None, dialect: Dialect
    ) -> str | None:
        if value is None:
            return value
        elif dialect.name in ["postgresql", "mysql"]:
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return value.hex
            return value
    
    # 决定 数据库存储类型（CHAR、UUID 等）        
    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))
        
    def process_result_value(self, value: uuid.UUID | str | None, dialect: Dialect) -> str | None:
        if value is None:
            return value
        return str(value)
    
class LongText(TypeDecorator[str | None]):
    impl = TEXT
    cache_ok = True
    
    def process_bind_param(self, value: str | None, dialect: Dialect) -> str | None:
        if value is None:
            return value
        return value
    
    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(TEXT())
        elif dialect.name == "mysql":
            return dialect.type_descriptor(LONGTEXT())
        else:
            return dialect.type_descriptor(TEXT())
        
    def process_result_value(self, value: str | None, dialect: Dialect) -> str | None:
        if value is None:
            return value
        return value