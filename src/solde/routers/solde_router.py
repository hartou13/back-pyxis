from datetime import datetime
from fastapi import APIRouter, Depends, Query

from src.move.services.move_service import calculate_user_soldes_services
from src.solde.services.solde_service import get_user_accounts_evolution, get_user_soldes_service, refresh_solde_service, refresh_soldes_service
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

@router.get("")
async def get_user_soldes(current_user: str = Depends(get_current_user)):
    return await get_user_soldes_service(current_user)

@router.get("/evolution")
async def get_user_soldes_evolution(current_user: str = Depends(get_current_user), start_date: datetime = Query(...), end_date: datetime = Query(...)):
    return await get_user_accounts_evolution(start_date, end_date, current_user)