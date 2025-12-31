
from datetime import timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, String, DateTime


from .base import Base

class Image(Base):
    __tablename__ = "images"
    
    id = Column(String, primary_key=True)
    
    category = Column(String, nullable=False)
    oss_url = Column(String, nullable=False)
    embedding = Column(Vector(512), nullable=False)
    
    created_at = Column(DateTime, default=timezone.utc)