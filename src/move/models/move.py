from datetime import datetime
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text, Float
from src.database.mysql_connector import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Enum
from enum import Enum as PyEnum


class Move(Base):
    __tablename__ = "moves"
    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    from_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    description = Column(String(100), nullable=False)
    detail = Column(String(255), nullable=True)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    from_account = relationship("Account", foreign_keys=[from_account_id], backref="from_moves")
    to_account = relationship("Account", foreign_keys=[to_account_id], backref="to_moves")