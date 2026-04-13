from datetime import datetime
from pydantic import BaseModel, Field
from src.account.models.account import AccountMoveTypeEnum, AccountTypeEnum
from typing import Optional


class MoveDto(BaseModel):
    amount: float = Field(..., description="The amount field is required")
    from_account_id : str = Field(..., description="The from_account_id field is required")
    to_account_id : str = Field(..., description="The to_account_id field is required")
    description : str = Field(..., description="The to_account_id field is required")
    detail : Optional[str] = Field(None, description="The to_account_id field is required")
    date: datetime = Field(..., description="The to_account_id field is required")