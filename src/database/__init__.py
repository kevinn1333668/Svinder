from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

async def create_pool(database_url: str):
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
        poolclass=NullPool
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    return async_session 