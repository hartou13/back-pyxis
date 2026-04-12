from pydantic import BaseModel, Field
from src.account.models.account import AccountMoveTypeEnum, AccountTypeEnum


class SimpleNewAccountDto(BaseModel):
    account_name: str = Field(..., description="The account_name field is required")
    account_move_type: AccountMoveTypeEnum = Field(..., description="The account_move_type field is required")
    account_type: AccountTypeEnum = Field(..., description="The account_type field is required")
