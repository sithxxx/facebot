from sqlalchemy import select, update
from bot.database.connection import async_session
from bot.database.models import User, AnalysisJob, Payment
from datetime import datetime

async def upsert_user(user_id: int, username: str | None, first_name: str | None) -> User:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            # All analyses are paid: no signup freebie (free_analyses stays 0).
            user = User(
                id=user_id,
                username=username,
                first_name=first_name,
            )
            session.add(user)
        else:
            user.username = username
            user.first_name = first_name
            user.last_seen = datetime.utcnow()
            
        await session.commit()
        await session.refresh(user)
        return user

async def get_user(user_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

async def decrement_free_analysis(user_id: int) -> bool:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user and user.free_analyses > 0:
            user.free_analyses -= 1
            await session.commit()
            return True
        return False

async def increment_total_analyses(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.total_analyses += 1
            await session.commit()

async def create_analysis_job(user_id: int, gender: str) -> AnalysisJob:
    async with async_session() as session:
        job = AnalysisJob(user_id=user_id, gender=gender, status="pending")
        session.add(job)
        await session.commit()
        await session.refresh(job)
        return job

async def update_job_status(job_id: int, status: str, error_msg: str | None = None, overall_score: float | None = None, metrics_json: dict | None = None):
    async with async_session() as session:
        job = await session.get(AnalysisJob, job_id)
        if job:
            job.status = status
            if error_msg:
                job.error_msg = error_msg
            if status in ["done", "failed"]:
                job.completed_at = datetime.utcnow()
            if overall_score is not None:
                job.overall_score = overall_score
            if metrics_json is not None:
                job.metrics_json = metrics_json
            await session.commit()

async def create_payment(user_id: int, telegram_payment_charge_id: str | None, amount: str, method: str = "stars") -> Payment:
    async with async_session() as session:
        payment = Payment(
            user_id=user_id,
            telegram_payment_charge_id=telegram_payment_charge_id,
            amount=amount,
            method=method
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        return payment

async def set_subscription_used(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.free_analyses += 1
            user.subscription_used = True
            await session.commit()


async def update_best_score(user_id: int, score: float, gender: str | None = None) -> bool:
    """
    Promote the user's leaderboard score if this analysis beat their best.
    Stores the gender of the best analysis (the leaderboard is gender-split).
    Returns True if the score improved (user moved up), else False.
    """
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            return False
        if user.best_score is None or score > user.best_score:
            user.best_score = score
            user.best_at = datetime.utcnow()
            if gender:
                user.gender = gender
            await session.commit()
            return True
        return False


async def set_user_lang(user_id: int, lang: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.lang = lang
            await session.commit()


async def get_user_lang(user_id: int) -> str | None:
    user = await get_user(user_id)
    return user.lang if user else None


async def set_leaderboard_visibility(user_id: int, visible: bool):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.show_on_leaderboard = visible
            await session.commit()


def _display_name(user: User) -> str | None:
    """Public label for the leaderboard: @username, else first_name, else None."""
    if user.username:
        return f"@{user.username}"
    return user.first_name


async def get_global_leaderboard(gender: str, limit: int = 50) -> list[dict]:
    """Top users of one gender by best_score, opted-in and scored. Highest first."""
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .where(User.best_score.is_not(None))
            .where(User.show_on_leaderboard.is_(True))
            .where(User.gender == gender)
            .order_by(User.best_score.desc(), User.best_at.asc())
            .limit(limit)
        )
        users = result.scalars().all()
    return [
        {
            "user_id": u.id,
            "name": _display_name(u),
            "score": round(u.best_score, 2),
            "rank": i + 1,
        }
        for i, u in enumerate(users)
    ]


async def get_tier_leaderboard(gender: str, score_min: float, score_max: float, limit: int = 50) -> list[dict]:
    """
    Top users of one gender whose best_score falls in [score_min, score_max),
    highest first. Caller derives the band from tier_service.
    """
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .where(User.best_score.is_not(None))
            .where(User.show_on_leaderboard.is_(True))
            .where(User.gender == gender)
            .where(User.best_score >= score_min)
            .where(User.best_score < score_max)
            .order_by(User.best_score.desc(), User.best_at.asc())
            .limit(limit)
        )
        users = result.scalars().all()
    return [
        {
            "user_id": u.id,
            "name": _display_name(u),
            "score": round(u.best_score, 2),
            "rank": i + 1,
        }
        for i, u in enumerate(users)
    ]


async def get_user_rank(user_id: int) -> dict | None:
    """The user's own best_score and rank within their gender (1 = highest)."""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None or user.best_score is None:
            return None
        from sqlalchemy import func
        ahead = await session.execute(
            select(func.count(User.id))
            .where(User.best_score.is_not(None))
            .where(User.show_on_leaderboard.is_(True))
            .where(User.gender == user.gender)
            .where(User.best_score > user.best_score)
        )
        rank = (ahead.scalar() or 0) + 1
    return {
        "user_id": user.id,
        "name": _display_name(user),
        "score": round(user.best_score, 2),
        "rank": rank,
        "gender": user.gender,
        "show_on_leaderboard": user.show_on_leaderboard,
    }
