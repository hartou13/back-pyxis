from datetime import datetime
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text, Float
from src.database.mysql_connector import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Enum
from enum import Enum as PyEnum


class Solde(Base):
    __tablename__ = "soldes"
    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    remaining = Column(Float, nullable=False, default=0)