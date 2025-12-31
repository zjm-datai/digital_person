

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.decl_api import MappedAsDataclass

from .engine import metadata


class Base(DeclarativeBase):
    
    metadata = metadata
    
class TypeBase(MappedAsDataclass, DeclarativeBase):
    
    metadata = metadata