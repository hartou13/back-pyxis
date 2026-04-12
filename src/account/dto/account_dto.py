from pydantic import BaseModel, Field
from src.account.models.account import AccountMoveTypeEnum, AccountTypeEnum
from typing import Optional


class SimpleNewAccountDto(BaseModel):
    account_name: str = Field(..., description="The account_name field is required")
    account_move_type: AccountMoveTypeEnum = Field(..., description="The account_move_type field is required")
    account_type: AccountTypeEnum = Field(..., description="The account_type field is required")
    super_account_id: Optional[str] = Field(None, description="The super_account_id field is required")
