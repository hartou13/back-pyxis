from fastapi import HTTPException
from sqlalchemy import insert, select
from src.database.mysql_connector import get_db
from src.account.dto.account_dto import SimpleNewAccountDto
from src.account.models.account import Account, AccountMoveTypeEnum
from sqlalchemy.orm import load_only, joinedload

async def create_account_service(account: SimpleNewAccountDto, user_id: str):
    async with get_db() as db:
        result = await db.scalar(select(Account).options(load_only(Account.account_name)).where(Account.account_name==account.account_name, Account.user_id==user_id))
        if (result):
            raise HTTPException(status_code=400, detail="Account already exists")
        if account.super_account_id:
            super_account = await db.scalar(select(Account).options(load_only(Account.id)).where(Account.id==account.super_account_id, Account.user_id==user_id))
            if (not super_account):
                raise HTTPException(status_code=404, detail="Super account not found")
        stmt = insert(Account).values(
            account_name=account.account_name,
            account_move_type=account.account_move_type,
            account_type=account.account_type,
            user_id=user_id,
            super_account_id=account.super_account_id or None,
        )
        result=await db.execute(stmt)
        await db.commit()
        return result.inserted_primary_key[0]

async def get_account_service(account_id: str, user_id: str):
    async with get_db() as db:
        result = await db.scalar(select(Account).options(
            joinedload(Account.super_account),
            joinedload(Account.sub_accounts).noload(Account.sub_accounts)
        ).where(Account.id==account_id, Account.user_id==user_id))
        if (result):
            return result
        raise HTTPException(status_code=404, detail="Account not found")

async def get_user_accounts_service(user_id: str, account_move_type: AccountMoveTypeEnum = None):
    async with get_db() as db:
        stmt = select(Account).options(load_only(Account.id, Account.account_name, Account.account_move_type, Account.account_type, Account.super_account_id)).where(Account.user_id==user_id)
        if (account_move_type):
            stmt = stmt.where(Account.account_move_type==account_move_type)
        result = await db.execute(stmt)
        return result.scalars().all()
        
async def update_account_service(account_id: str, account: SimpleNewAccountDto, user_id: str):
    async with get_db() as db:
        result = await db.scalar(select(Account).options(load_only(Account.account_name)).where(Account.id==account_id, Account.user_id==user_id))
        if account.super_account_id:
            super_account = await db.scalar(select(Account).options(load_only(Account.id)).where(Account.id==account.super_account_id, Account.user_id==user_id))
            if (not super_account):
                raise HTTPException(status_code=404, detail="Super account not found")

        if (result):
            result.account_name = account.account_name
            result.account_move_type = account.account_move_type
            result.account_type = account.account_type
            result.super_account_id = account.super_account_id or None
            await db.commit()
            return result
        raise HTTPException(status_code=404, detail="Account not found")
        
async def delete_account_service(account_id: str, user_id: str):
    async with get_db() as db:
        result = await db.scalar(select(Account).options(load_only(Account.id)).where(Account.id==account_id, Account.user_id==user_id))
        if (result):
            await db.delete(result)
            await db.commit()
            return result
        raise HTTPException(status_code=404, detail="Account not found")