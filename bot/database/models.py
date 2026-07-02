from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String, Float, DateTime, JSON, Boolean
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user_id
    username: Mapped[str | None] = mapped_column(String(64))
    first_name: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    last_seen: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    free_analyses: Mapped[int] = mapped_column(default=0)
    total_analyses: Mapped[int] = mapped_column(default=0)
    subscription_used: Mapped[bool] = mapped_column(default=False)
    # Leaderboard: best overall_score ever achieved, when, and a privacy
    # opt-out switch (default True = shown in the public Mini App ranking).
    # gender comes from the analysis that produced the best score — the
    # leaderboard is fully gender-split (male/female sections).
    best_score: Mapped[float | None] = mapped_column(Float, default=None)
    best_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    gender: Mapped[str | None] = mapped_column(String(8), default=None)
    show_on_leaderboard: Mapped[bool] = mapped_column(Boolean, default=True)

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    gender: Mapped[str] = mapped_column(String(8))
    overall_score: Mapped[float | None] = mapped_column(Float)
    metrics_json: Mapped[dict | None] = mapped_column(JSON)   # full FullAnalysisResult
    status: Mapped[str] = mapped_column(String(16), default="pending")
    # status: pending | processing | done | failed
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    completed_at: Mapped[datetime | None]
    error_msg: Mapped[str | None] = mapped_column(String(512))

class Payment(Base):
    __tablename__ = "payments"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    telegram_payment_charge_id: Mapped[str | None] = mapped_column(String(128))
    method: Mapped[str] = mapped_column(String(16), default="stars")
    amount: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
