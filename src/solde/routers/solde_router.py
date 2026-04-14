from fastapi import APIRouter, Depends, Query

from src.solde.services.solde_service import refresh_solde_service, refresh_soldes_service
from src.users.services.user_service import get_current_user


router = APIRouter(
    prefix="/solde",
    tags=["solde"],
    responses={404: {"description": "Not found"}},
)

@router.post("/refresh")
async def refresh_solde(current_user: str = Depends(get_current_user)):
    return await refresh_soldes_service(current_user)

@router.post("/refresh/{account_id}")
async def refresh_solde(account_id: str, current_user: str = Depends(get_current_user)):
    return await refresh_solde_service(account_id, current_user)