from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from bot.config import DATABASE_URL
from bot.database.models import Base
import logging

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logging.info("Database tables created/verified.")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise
