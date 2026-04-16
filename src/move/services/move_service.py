from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import case, delete, func, insert, or_, select, update
from src.account.models.account import Account, AccountMoveTypeEnum
from src.account.services.account_service import get_account_service
from src.database.mysql_connector import get_db
from src.move.dto.move_dto import MoveDto
from src.move.models.move import Move
from sqlalchemy.orm import joinedload, load_only

async def check_move_validity_service(move: MoveDto, current_user_id: str):
    from_account = await get_account_service(move.from_account_id, current_user_id)
    to_account = await get_account_service(move.to_account_id, current_user_id)
    if from_account.account_move_type == AccountMoveTypeEnum.EXPENSE:
        raise HTTPException(status_code=400, detail="Cannot take from an expense account")
    if to_account.account_move_type == AccountMoveTypeEnum.INCOME:  
        raise HTTPException(status_code=400, detail="Cannot put into an income account")
        

async def create_move_service(move: MoveDto, current_user_id: str):
    from src.solde.services.solde_service import add_to_solde_service
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
        await add_to_solde_service(move.from_account_id, -move.amount)
        await add_to_solde_service(move.to_account_id, move.amount)
        await db.commit()
        return result.inserted_primary_key[0]
    
async def update_move_service(move_id: str, move: MoveDto, current_user_id: str):
    from src.solde.services.solde_service import add_to_solde_service
    async with get_db() as db:
        stmt = select(Move).where(Move.id == move_id, Move.user_id == current_user_id)
        result = await db.scalar(stmt)
        if result:
            await check_move_validity_service(move, current_user_id)
            previous_amount = result.amount
            result.amount = move.amount
            result.from_account_id = move.from_account_id
            result.to_account_id = move.to_account_id
            result.description = move.description
            result.detail = move.detail
            result.date = move.date 
            if previous_amount != move.amount:
                await add_to_solde_service(move.from_account_id, previous_amount - move.amount)
                await add_to_solde_service(move.to_account_id, move.amount - previous_amount)
            return result
        raise HTTPException(status_code=404, detail="Move not found")
        
async def delete_move_service(move_id: str, current_user_id: str):
    from src.solde.services.solde_service import add_to_solde_service
    async with get_db() as db:
        result = await db.scalar(select(Move).where(Move.id == move_id, Move.user_id == current_user_id))
        if result:
            await db.execute(delete(Move).where(Move.id == move_id))
            await add_to_solde_service(result.from_account_id, result.amount)
            await add_to_solde_service(result.to_account_id, -result.amount)
            await db.commit()
            return result
        raise HTTPException(status_code=404, detail="Move not found")
    
async def get_user_moves_service(current_user_id: str, page: int = 1, pageSize: int = 10):
    async with get_db() as db:
        base = select(Move).options(
            joinedload(Move.from_account).options(load_only(Account.id, Account.account_name, Account.account_move_type, Account.account_type)), 
            joinedload(Move.to_account).options(load_only(Account.id, Account.account_name, Account.account_move_type, Account.account_type))
        ).where(Move.user_id == current_user_id)
        total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar()
        stmt = base.order_by(Move.date.desc()).limit(pageSize).offset((page - 1) * pageSize)
        result = await db.execute(stmt)
        return {"data": result.scalars().all(), "pagination": {"total": total, "page": page, "pageSize": pageSize}}
    
async def get_one_move_service(move_id: str, current_user_id: str):
    async with get_db() as db:
        result = await db.scalar(select(Move).options(joinedload(Move.from_account), joinedload(Move.to_account)).where(Move.id == move_id, Move.user_id == current_user_id))
        if not result:
            raise HTTPException(status_code=404, detail="Move not found")
        return result
    
async def get_account_history(account_id: str, current_user_id: str, page: int = 1, pageSize: int = 10):
    async with get_db() as db:
        account = await get_account_service(account_id, current_user_id)
        base = select(Move).options(
            joinedload(Move.from_account).options(load_only(Account.id, Account.account_name, Account.account_move_type, Account.account_type)), 
            joinedload(Move.to_account).options(load_only(Account.id, Account.account_name, Account.account_move_type, Account.account_type))
        ).where(Move.user_id == current_user_id, or_(Move.from_account_id == account.id, Move.to_account_id == account.id))
        total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar()
        stmt = base.order_by(Move.date.desc()).limit(pageSize).offset((page - 1) * pageSize)
        result = await db.execute(stmt)
        return {"data": result.scalars().all(), "pagination": {"total": total, "page": page, "pageSize": pageSize}}
    
async def calculate_user_soldes_services(current_user_id: str, start_date: datetime = None, end_date: datetime = None):
    async with get_db() as db:
        stmt = select(
            Account.id,
            Account.account_name,
            Account.account_move_type,
            func.coalesce(
                func.sum(case((Move.to_account_id == Account.id, Move.amount), else_=0)) -
                func.sum(case((Move.from_account_id == Account.id, Move.amount), else_=0)),
                0
            ).label("balance")
        ).select_from(Account).outerjoin(
            Move, Account.user_id == Move.user_id
        ).where(Account.user_id == current_user_id).group_by(Account.id, Account.account_name, Account.account_move_type)
        
        if (start_date and end_date):
            stmt = stmt.where(Move.date.between(start_date, end_date))

        result = await db.execute(stmt)
        rows = result.all()
        return [{"id":row[0], "account_name":row[1], "account_move_type":row[2], "balance":row[3]} for row in rows]
    
async def calculate_accound_solde_service(account_id: str, current_user_id: str):
    async with get_db() as db:
        stmt = select(
            func.coalesce(
                func.sum(case((Move.to_account_id == account_id, Move.amount), else_=0)) -
                func.sum(case((Move.from_account_id == account_id, Move.amount), else_=0)),
                0
            ).label("balance")
        ).where(
            Move.user_id == current_user_id,
            or_(Move.to_account_id == account_id, Move.from_account_id == account_id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
async def calculate_account_tendency_service(account_id: str, current_user_id: str):
    from datetime import datetime, timedelta
    async with get_db() as db:
        now = datetime.now()
        one_year_ago = now - timedelta(days=365)

        # Generate all months in the range
        months = {}
        current = one_year_ago.replace(day=1)
        while current <= now:
            key = (current.year, current.month)
            months[key] = 0
            # Add one month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        stmt = select(
            func.year(Move.date).label("year"),
            func.month(Move.date).label("month"),
            func.coalesce(
                func.sum(case((Move.to_account_id == account_id, Move.amount), else_=0)) -
                func.sum(case((Move.from_account_id == account_id, Move.amount), else_=0)),
                0
            ).label("balance")
        ).where(
            Move.user_id == current_user_id,
            or_(Move.to_account_id == account_id, Move.from_account_id == account_id),
            Move.date >= one_year_ago
        ).group_by(
            func.year(Move.date),
            func.month(Move.date)
        ).order_by(
            func.year(Move.date),
            func.month(Move.date)
        )

        result = await db.execute(stmt)
        rows = result.all()

        # Fill in the data
        for row in rows:
            key = (row[0], row[1])
            months[key] = row[2]

        # Return sorted by year and month
        return [{"year": k[0], "month": k[1], "balance": months[k]} for k in sorted(months.keys())]

async def calculate_account_tendency_weekly_service(account_id: str, current_user_id: str):
    from datetime import datetime, timedelta, date
    async with get_db() as db:
        now = datetime.now()
        three_months_ago = now - timedelta(days=90)

        # Generate all weeks in the range, labeled by Monday
        weeks = {}
        current = three_months_ago.date()
        # Find the Monday of the week containing current date
        monday = current - timedelta(days=current.weekday())
        while monday <= now.date():
            weeks[monday] = 0
            monday += timedelta(weeks=1)

        stmt = select(
            func.year(Move.date).label("year"),
            func.week(Move.date).label("week"),
            func.coalesce(
                func.sum(case((Move.to_account_id == account_id, Move.amount), else_=0)) -
                func.sum(case((Move.from_account_id == account_id, Move.amount), else_=0)),
                0
            ).label("balance")
        ).where(
            Move.user_id == current_user_id,
            or_(Move.to_account_id == account_id, Move.from_account_id == account_id),
            Move.date >= three_months_ago
        ).group_by(
            func.year(Move.date),
            func.week(Move.date)
        ).order_by(
            func.year(Move.date),
            func.week(Move.date)
        )

        result = await db.execute(stmt)
        rows = result.all()

        # Convert weeks to actual Monday dates
        for row in rows:
            # row[0] is year, row[1] is week number
            # Calculate the Monday of that week (ISO week starts on Monday)
            year, week = row[0], row[1]
            jan4 = date(year, 1, 4)
            monday_week1 = jan4 - timedelta(days=jan4.weekday())
            monday = monday_week1 + timedelta(weeks=week)
            weeks[monday] = row[2]

        # Return sorted by date (Monday)
        return [{"monday": str(k), "balance": weeks[k]} for k in sorted(weeks.keys())]

async def calculate_account_tendency_daily_service(account_id: str, current_user_id: str):
    from datetime import datetime, timedelta, date
    async with get_db() as db:
        now = datetime.now()
        three_weeks_ago = now - timedelta(days=21)

        # Generate all days in the range
        days = {}
        current = three_weeks_ago.date()
        while current <= now.date():
            days[current] = 0
            current += timedelta(days=1)

        stmt = select(
            func.date(Move.date).label("date"),
            func.coalesce(
                func.sum(case((Move.to_account_id == account_id, Move.amount), else_=0)) -
                func.sum(case((Move.from_account_id == account_id, Move.amount), else_=0)),
                0
            ).label("balance")
        ).where(
            Move.user_id == current_user_id,
            or_(Move.to_account_id == account_id, Move.from_account_id == account_id),
            Move.date >= three_weeks_ago
        ).group_by(
            func.date(Move.date)
        ).order_by(
            func.date(Move.date)
        )

        result = await db.execute(stmt)
        rows = result.all()

        # Fill in the data
        for row in rows:
            key = row[0]
            days[key] = row[1]

        # Return sorted by date
        return [{"date": str(k), "balance": days[k]} for k in sorted(days.keys())]