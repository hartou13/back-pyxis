from datetime import datetime
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text
from src.database.mysql_connector import Base

from sqlalchemy import Enum
from enum import Enum as PyEnum

class AccountMoveTypeEnum(PyEnum):
    INCOME = "income"
    EXPENSE = "expense"
    MOVEMENT = "movement"
    
class AccountTypeEnum(PyEnum):
    EXTERNAL = "external"
    PERSONAL = "personal"

class Account(Base):
    __tablename__ = "accounts"
    id = Column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )    
    user_id = Column(String(36), ForeignKey("users.id"))
    account_name = Column(String(255))
    account_move_type = Column(Enum(AccountMoveTypeEnum, name="account_move_type_enum"), nullable=False, default=AccountMoveTypeEnum.INCOME)
    account_type = Column(Enum(AccountTypeEnum, name="account_type_enum"), nullable=False, default=AccountTypeEnum.PERSONAL)
    


