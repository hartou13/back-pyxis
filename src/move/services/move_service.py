from fastapi import HTTPException
from sqlalchemy import delete, func, insert, or_, select, update
from src.account.models.account import AccountMoveTypeEnum
from src.account.services.account_service import get_account_service
from src.database.mysql_connector import get_db
from src.move.dto.move_dto import MoveDto
from src.move.models.move import Move

async def check_move_validity_service(move: MoveDto, current_user_id: str):
    from_account = await get_account_service(move.from_account_id, current_user_id)
    to_account = await get_account_service(move.to_account_id, current_user_id)
    if from_account.account_move_type == AccountMoveTypeEnum.EXPENSE:
        raise HTTPException(status_code=400, detail="Cannot take from an expense account")
    if to_account.account_move_type == AccountMoveTypeEnum.INCOME:  
        raise HTTPException(status_code=400, detail="Cannot put into an income account")
        

async def create_move_service(move: MoveDto, current_user_id: str):
    async with get_db() as db:
        await check_move_validity_service(move, current_user_id)
        stmt = insert(Move).values(
            user_id = current_user_id,
            amount = move.amount,
            from_account_id = move.from_account_id,
            to_account_id = move.to_account_id, 
            description = move.description,
            detail = move.detail,
            date = move.date
        )
        result=await db.execute(stmt)
        await db.commit()
        return result.inserted_primary_key[0]
    
async def update_move_service(move_id: str, move: MoveDto, current_user_id: str):
    async with get_db() as db:
        stmt = select(Move).where(Move.id == move_id, Move.user_id == current_user_id)
        result = await db.scalar(stmt)
        if result:
            await check_move_validity_service(move, current_user_id)
            result.amount = move.amount
            result.from_account_id = move.from_account_id
            result.to_account_id = move.to_account_id
            result.description = move.description
            result.detail = move.detail
            result.date = move.date 
            return result
        raise HTTPException(status_code=404, detail="Move not found")
        
async def delete_move_service(move_id: str, current_user_id: str):
    async with get_db() as db:
        result = await db.scalar(select(Move).where(Move.id == move_id, Move.user_id == current_user_id))
        if result:
            await db.execute(delete(Move).where(Move.id == move_id))
            await db.commit()
            return result
        raise HTTPException(status_code=404, detail="Move not found")
    
async def get_user_moves_service(current_user_id: str, page: int = 1, pageSize: int = 10):
    async with get_db() as db:
        base = select(Move).where(Move.user_id == current_user_id)
        total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar()
        stmt = base.order_by(Move.date.desc()).limit(pageSize).offset((page - 1) * pageSize)
        result = await db.execute(stmt)
        return {"data": result.scalars().all(), "pagination": {"total": total, "page": page, "pageSize": pageSize}}
    
async def get_one_move_service(move_id: str, current_user_id: str):
    async with get_db() as db:
        result = await db.scalar(select(Move).where(Move.id == move_id, Move.user_id == current_user_id))
        if not result:
            raise HTTPException(status_code=404, detail="Move not found")
        return result
    
async def get_account_history(account_id: str, current_user_id: str, page: int = 1, pageSize: int = 10):
    async with get_db() as db:
        account = await get_account_service(account_id, current_user_id)
        base = select(Move).where(Move.user_id == current_user_id, or_(Move.from_account_id == account.id, Move.to_account_id == account.id))
        total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar()
        stmt = base.order_by(Move.date.desc()).limit(pageSize).offset((page - 1) * pageSize)
        result = await db.execute(stmt)
        return {"data": result.scalars().all(), "pagination": {"total": total, "page": page, "pageSize": pageSize}}