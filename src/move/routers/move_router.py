from fastapi import APIRouter, Depends, Query

from src.move.dto.move_dto import MoveDto
from src.move.services.move_service import create_move_service, delete_move_service, calculate_accound_solde_service, get_one_move_service, get_user_moves_service, update_move_service
from src.account.dto.account_dto import SimpleNewAccountDto
from src.users.services.user_service import get_current_user


router = APIRouter(
    prefix="/move",
    tags=["move"],
    responses={404: {"description": "Not found"}},
)

@router.get("")
async def read_moves(current_user: str = Depends(get_current_user), page : int = 1, limit : int = 10):
    return await get_user_moves_service(current_user_id=current_user, page=page, pageSize=limit)

@router.post("")
async def create_move(move: MoveDto, current_user: str = Depends(get_current_user)):
    return await create_move_service(current_user_id=current_user, move=move)

@router.put("/{move_id}")
async def update_move(move_id: str, move: MoveDto, current_user: str = Depends(get_current_user)):
    return await update_move_service(move_id, move, current_user)

@router.delete("/{move_id}")
async def delete_move(move_id: str, current_user: str = Depends(get_current_user)):
    return await delete_move_service(move_id, current_user)

@router.get("/{move_id}")
async def get_move(move_id: str, current_user: str = Depends(get_current_user)):
    return await get_one_move_service(move_id, current_user)
