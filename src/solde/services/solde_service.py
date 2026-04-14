from fastapi import HTTPException
from sqlalchemy import select
from src.account.models.account import AccountMoveTypeEnum
from src.account.services.account_service import get_account_service, get_user_accounts_service
from src.database.mysql_connector import get_db
from src.move.services.move_service import calculate_accound_solde_service, calculate_user_soldes_services
from src.solde.models.solde import Solde


async def refresh_soldes_service(current_user_id: str):
    user_soldes=await calculate_user_soldes_services(current_user_id)
    new_soldes = []
    for user_solde in user_soldes:
        new_soldes.append(await update_solde_service(user_solde["id"], user_solde["balance"]))
    return new_soldes

async def update_solde_service(account_id: str, solde: float):
    async with get_db() as db:
        existing_solde = await db.scalar(select(Solde).where(Solde.account_id == account_id))
        if existing_solde:
            existing_solde.remaining = solde
        else:
            existing_solde = Solde(account_id=account_id, remaining=solde)
            db.add(existing_solde)
        await db.commit()
        return existing_solde
    
async def refresh_solde_service(account_id: str, current_user_id: str):
    user_solde = await calculate_accound_solde_service(account_id, current_user_id)
    new_solde = await update_solde_service(account_id, user_solde[0])
    return new_solde

async def add_to_solde_service(account_id: str, amount: float):
    async with get_db() as db:
        existing_solde = await db.scalar(select(Solde).where(Solde.account_id == account_id))
        if existing_solde:
            existing_solde.remaining += amount
        else:
            existing_solde = Solde(account_id=account_id, remaining=amount)
            db.add(existing_solde)
        await db.commit()
        return existing_solde
    
async def get_account_solde_service(account_id: str, current_user_id: str):
    async with get_db() as db:
        account = await get_account_service(account_id, current_user_id)
        existing_solde = await db.scalar(select(Solde).where(Solde.account_id == account.id))
        if existing_solde:
            return existing_solde
        return refresh_solde_service(account_id, current_user_id)
    
async def get_user_soldes_service(current_user_id: str):
    async with get_db() as db:
        user_accounts = await get_user_accounts_service(current_user_id, account_move_type=AccountMoveTypeEnum.MOVEMENT)
        soldes = await db.scalars(select(Solde).where(Solde.account_id.in_([account.id for account in user_accounts])))
        for user_account in user_accounts:
            user_account.solde = next((solde for solde in soldes if solde.account_id == user_account.id), None)
        return user_accounts