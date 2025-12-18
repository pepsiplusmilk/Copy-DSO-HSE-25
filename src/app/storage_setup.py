from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import settings

db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, echo=settings.echo_sql)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
