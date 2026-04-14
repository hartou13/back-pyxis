from fastapi import APIRouter, Depends

from src.solde.services.solde_service import get_account_solde_service
from src.move.services.move_service import get_account_history, calculate_accound_solde_service
from src.account.dto.account_dto import SimpleNewAccountDto
from src.users.services.user_service import get_current_user
from src.account.services.account_service import create_account_service, get_account_service, get_user_accounts_service, update_account_service, delete_account_service


router = APIRouter(
    prefix="/account",
    tags=["account"],
    responses={404: {"description": "Not found"}},
)

@router.post("")
async def create_account(account: SimpleNewAccountDto, current_user: str = Depends(get_current_user)):
    account = await create_account_service(account, current_user)
    return account

@router.get("/{account_id}/move-history")
async def get_account_move_history(account_id: str, current_user: str = Depends(get_current_user), page : int = 1, limit : int = 0):
    account = await get_account_history(account_id, current_user, page, pageSize=limit)
    return account

@router.get("/{account_id}")
async def get_account(account_id: str, current_user: str = Depends(get_current_user)):
    account = await get_account_service(account_id, current_user)
    return account

@router.get("/{account_id}/solde")
async def get_account_solde(account_id: str, current_user: str = Depends(get_current_user)):
    account = await get_account_solde_service(account_id, current_user)
    return account

@router.get("")
async def get_user_accounts(current_user: str = Depends(get_current_user)):
    accounts = await get_user_accounts_service(current_user)
    return accounts

@router.put("/{account_id}")
async def update_account(account_id: str, account: SimpleNewAccountDto, current_user: str = Depends(get_current_user)):
    account = await update_account_service(account_id, account, current_user)
    return account

@router.delete("/{account_id}")
async def delete_account(account_id: str, current_user: str = Depends(get_current_user)):
    account = await delete_account_service(account_id, current_user)
    return account